from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass

from music_generator.domain.events import (
    BpmChangeEvent,
    MusicalEvent,
    NoteEndEvent,
    NoteStartEvent,
)


MAX_MELODIC_VOICES = 15
MELODIC_CHANNELS: tuple[int, ...] = tuple(
    channel for channel in range(16) if channel != 9
)


@dataclass(frozen=True, slots=True)
class VoiceSettings:
    base_octave: int
    initial_volume: int
    initial_instrument: int

    @classmethod
    def from_voice_index(cls, voice_index: int) -> "VoiceSettings":
        cycle = (
            cls(base_octave=6, initial_volume=100, initial_instrument=6),
            cls(base_octave=5, initial_volume=80, initial_instrument=20),
            cls(base_octave=4, initial_volume=60, initial_instrument=0),
            cls(base_octave=3, initial_volume=40, initial_instrument=70),
        )
        if voice_index < 0:
            raise ValueError("voice_index must be greater than or equal to 0.")
        return cycle[voice_index % len(cycle)]


@dataclass(frozen=True, slots=True)
class MusicalVoice:
    voice_id: str
    voice_index: int
    settings: VoiceSettings
    initial_delay_beats: float
    source_text: str
    _events: tuple[MusicalEvent, ...]

    def __init__(
        self,
        voice_index: int,
        settings: VoiceSettings,
        initial_delay_beats: float,
        source_text: str,
        events: Iterable[MusicalEvent],
    ) -> None:
        if voice_index < 0:
            raise ValueError("voice_index must be greater than or equal to 0.")
        if initial_delay_beats < 0:
            raise ValueError("initial_delay_beats must be greater than or equal to 0.")
        object.__setattr__(self, "voice_id", f"V{voice_index}")
        object.__setattr__(self, "voice_index", voice_index)
        object.__setattr__(self, "settings", settings)
        object.__setattr__(self, "initial_delay_beats", initial_delay_beats)
        object.__setattr__(self, "source_text", source_text)
        object.__setattr__(self, "_events", tuple(events))

    @property
    def events(self) -> Sequence[MusicalEvent]:
        return self._events


@dataclass(frozen=True, slots=True)
class ScheduledMusicalEvent:
    absolute_beat: float
    voice_index: int
    origin_order: int
    event: MusicalEvent

    def __post_init__(self) -> None:
        if self.absolute_beat < 0:
            raise ValueError("absolute_beat must be greater than or equal to 0.")
        if self.voice_index < 0:
            raise ValueError("voice_index must be greater than or equal to 0.")
        if self.origin_order < 0:
            raise ValueError("origin_order must be greater than or equal to 0.")

    @property
    def priority(self) -> int:
        if isinstance(self.event, BpmChangeEvent):
            return 0
        if isinstance(self.event, NoteEndEvent):
            return 1
        if isinstance(self.event, NoteStartEvent):
            return 2
        return 3

    @property
    def sort_key(self) -> tuple[float, int, int, int]:
        return (
            self.absolute_beat,
            self.priority,
            self.voice_index,
            self.origin_order,
        )


@dataclass(frozen=True, slots=True)
class PolyphonicComposition:
    _voices: tuple[MusicalVoice, ...]
    _timeline: tuple[ScheduledMusicalEvent, ...]
    initial_bpm: int

    def __init__(
        self,
        voices: Iterable[MusicalVoice],
        timeline: Iterable[ScheduledMusicalEvent],
        initial_bpm: int = 120,
    ) -> None:
        voice_tuple = tuple(voices)
        if len(voice_tuple) > MAX_MELODIC_VOICES:
            raise ValueError(
                f"Polyphonic playback supports at most {MAX_MELODIC_VOICES} "
                "melodic voices."
            )
        if initial_bpm < 10:
            raise ValueError("initial_bpm must be greater than or equal to 10.")

        object.__setattr__(self, "_voices", voice_tuple)
        object.__setattr__(
            self,
            "_timeline",
            tuple(sorted(timeline, key=lambda scheduled: scheduled.sort_key)),
        )
        object.__setattr__(self, "initial_bpm", initial_bpm)

    def __iter__(self) -> Iterator[ScheduledMusicalEvent]:
        return iter(self._timeline)

    def __len__(self) -> int:
        return len(self._timeline)

    @property
    def voices(self) -> Sequence[MusicalVoice]:
        return self._voices

    @property
    def timeline(self) -> Sequence[ScheduledMusicalEvent]:
        return self._timeline
