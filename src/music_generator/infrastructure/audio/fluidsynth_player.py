import os
import threading
from pathlib import Path
from types import ModuleType
from typing import Any

from music_generator.domain.composition import MusicalComposition
from music_generator.domain.events import (
    BpmChangeEvent,
    InstrumentChangeEvent,
    NoteEndEvent,
    NoteEvent,
    NoteStartEvent,
    RestEvent,
)
from music_generator.domain.polyphony import MELODIC_CHANNELS, PolyphonicComposition
from music_generator.infrastructure.audio.player import AudioPlayer


class FluidSynthPlayerError(RuntimeError):
    pass


class FluidSynthPlayer(AudioPlayer):
    CHANNEL = 0

    def __init__(
        self,
        soundfont_path: str | Path | None = None,
        audio_driver: str | None = None,
    ) -> None:
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._active_note: int | None = None
        self._active_notes: set[tuple[int, int]] = set()
        self._current_instrument_by_channel: dict[int, int] = {}
        self._closed = False

        resolved_soundfont = self._resolve_soundfont_path(soundfont_path)
        fluidsynth = self._import_fluidsynth()
        self._synth = self._create_synth(fluidsynth, audio_driver)
        self._soundfont_id = self._load_soundfont(resolved_soundfont)

    def play(self, composition: MusicalComposition | PolyphonicComposition) -> None:
        with self._lock:
            if self._closed:
                raise FluidSynthPlayerError("Cannot play after FluidSynthPlayer.close().")
            self._stop_event.clear()

        if isinstance(composition, PolyphonicComposition):
            self._play_polyphonic(composition)
            return

        seconds_per_beat = 60.0 / composition.initial_bpm
        try:
            for event in composition:
                if self._stop_event.is_set():
                    break
                if isinstance(event, InstrumentChangeEvent):
                    self._select_instrument(event.instrument)
                elif isinstance(event, NoteEvent):
                    self._play_note(event, seconds_per_beat)
                elif isinstance(event, RestEvent):
                    self._wait(event.duration_beats * seconds_per_beat)
        finally:
            self._turn_off_active_note()
            self._turn_off_active_notes()

    def stop(self) -> None:
        self._stop_event.set()
        self._turn_off_active_note()
        self._turn_off_active_notes()

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self.stop()
            if hasattr(self._synth, "delete"):
                self._synth.delete()
            self._closed = True

    def _resolve_soundfont_path(self, soundfont_path: str | Path | None) -> Path:
        selected_path = soundfont_path or os.environ.get("SOUNDFONT_PATH")
        if not selected_path:
            raise FluidSynthPlayerError(
                "SoundFont not configured. Set SOUNDFONT_PATH or pass "
                "soundfont_path to FluidSynthPlayer."
            )

        resolved_path = Path(selected_path).expanduser()
        if not resolved_path.is_file():
            raise FluidSynthPlayerError(
                f"SoundFont file not found: {resolved_path}. Provide a valid .sf2 "
                "file through SOUNDFONT_PATH or soundfont_path."
            )
        return resolved_path

    def _import_fluidsynth(self) -> ModuleType:
        try:
            import fluidsynth
        except ImportError as exc:
            raise FluidSynthPlayerError(
                "pyfluidsynth is not installed. Install the optional audio "
                "dependency and the native FluidSynth library before playback."
            ) from exc
        return fluidsynth

    def _create_synth(self, fluidsynth: ModuleType, audio_driver: str | None) -> Any:
        try:
            synth = fluidsynth.Synth()
            if audio_driver:
                synth.start(driver=audio_driver)
            else:
                synth.start()
        except Exception as exc:
            raise FluidSynthPlayerError(
                "Could not initialize FluidSynth. Check that the native "
                "FluidSynth library and an audio driver are available."
            ) from exc
        return synth

    def _load_soundfont(self, soundfont_path: Path) -> int:
        soundfont_id = self._synth.sfload(str(soundfont_path))
        if soundfont_id == -1:
            raise FluidSynthPlayerError(
                f"FluidSynth could not load the SoundFont: {soundfont_path}."
            )
        return soundfont_id

    def _play_note(self, event: NoteEvent, seconds_per_beat: float) -> None:
        self._select_instrument(self.CHANNEL, event.instrument)
        with self._lock:
            self._synth.noteon(self.CHANNEL, event.midi_number, event.volume)
            self._active_note = event.midi_number
            self._active_notes.add((self.CHANNEL, event.midi_number))
        try:
            self._wait(event.duration_beats * seconds_per_beat)
        finally:
            self._turn_off_active_note()

    def _play_polyphonic(self, composition: PolyphonicComposition) -> None:
        if len(composition.voices) > len(MELODIC_CHANNELS):
            raise FluidSynthPlayerError(
                f"Polyphonic playback supports at most {len(MELODIC_CHANNELS)} "
                "melodic voices."
            )

        voice_channels = {
            voice.voice_index: MELODIC_CHANNELS[voice.voice_index]
            for voice in composition.voices
        }
        current_bpm = composition.initial_bpm
        current_beat = 0.0
        active_by_origin: dict[tuple[int, int], tuple[int, int]] = {}

        try:
            for scheduled in composition:
                if self._stop_event.is_set():
                    break

                beat_delta = scheduled.absolute_beat - current_beat
                if beat_delta > 0:
                    self._wait(beat_delta * 60.0 / current_bpm)
                    current_beat = scheduled.absolute_beat
                    if self._stop_event.is_set():
                        break

                event = scheduled.event
                if isinstance(event, BpmChangeEvent):
                    current_bpm = event.bpm
                elif isinstance(event, NoteEndEvent):
                    active_key = (scheduled.voice_index, scheduled.origin_order)
                    channel_and_note = active_by_origin.pop(active_key, None)
                    if channel_and_note is not None:
                        self._noteoff(*channel_and_note)
                elif isinstance(event, NoteStartEvent):
                    channel = voice_channels[scheduled.voice_index]
                    note = event.note
                    self._select_instrument(channel, note.instrument)
                    self._noteon(channel, note)
                    active_by_origin[(scheduled.voice_index, scheduled.origin_order)] = (
                        channel,
                        note.midi_number,
                    )
        finally:
            self._turn_off_active_notes()

    def _select_instrument(self, channel: int, instrument: int) -> None:
        with self._lock:
            if self._current_instrument_by_channel.get(channel) == instrument:
                return
            self._synth.program_select(
                channel,
                self._soundfont_id,
                0,
                instrument,
            )
            self._current_instrument_by_channel[channel] = instrument

    def _noteon(self, channel: int, note: NoteEvent) -> None:
        with self._lock:
            self._synth.noteon(channel, note.midi_number, note.volume)
            self._active_notes.add((channel, note.midi_number))

    def _noteoff(self, channel: int, midi_number: int) -> None:
        with self._lock:
            self._synth.noteoff(channel, midi_number)
            self._active_notes.discard((channel, midi_number))

    def _wait(self, seconds: float) -> None:
        self._stop_event.wait(max(seconds, 0.0))

    def _turn_off_active_note(self) -> None:
        with self._lock:
            if self._active_note is not None:
                self._synth.noteoff(self.CHANNEL, self._active_note)
                self._active_notes.discard((self.CHANNEL, self._active_note))
                self._active_note = None

    def _turn_off_active_notes(self) -> None:
        with self._lock:
            active_notes = tuple(self._active_notes)
            self._active_notes.clear()

        for channel, midi_number in active_notes:
            self._synth.noteoff(channel, midi_number)
