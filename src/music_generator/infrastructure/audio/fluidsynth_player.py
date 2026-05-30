import os
import threading
from pathlib import Path
from types import ModuleType
from typing import Any

from music_generator.domain.composition import MusicalComposition
from music_generator.domain.events import (
    InstrumentChangeEvent,
    NoteEvent,
    RestEvent,
)
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
        self._current_instrument: int | None = None
        self._closed = False

        resolved_soundfont = self._resolve_soundfont_path(soundfont_path)
        fluidsynth = self._import_fluidsynth()
        self._synth = self._create_synth(fluidsynth, audio_driver)
        self._soundfont_id = self._load_soundfont(resolved_soundfont)

    def play(self, composition: MusicalComposition) -> None:
        with self._lock:
            if self._closed:
                raise FluidSynthPlayerError("Cannot play after FluidSynthPlayer.close().")
            self._stop_event.clear()

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

    def stop(self) -> None:
        self._stop_event.set()
        self._turn_off_active_note()

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
        self._select_instrument(event.instrument)
        with self._lock:
            self._synth.noteon(self.CHANNEL, event.midi_number, event.volume)
            self._active_note = event.midi_number
        try:
            self._wait(event.duration_beats * seconds_per_beat)
        finally:
            self._turn_off_active_note()

    def _select_instrument(self, instrument: int) -> None:
        with self._lock:
            if self._current_instrument == instrument:
                return
            self._synth.program_select(
                self.CHANNEL,
                self._soundfont_id,
                0,
                instrument,
            )
            self._current_instrument = instrument

    def _wait(self, seconds: float) -> None:
        self._stop_event.wait(max(seconds, 0.0))

    def _turn_off_active_note(self) -> None:
        with self._lock:
            if self._active_note is not None:
                self._synth.noteoff(self.CHANNEL, self._active_note)
                self._active_note = None
