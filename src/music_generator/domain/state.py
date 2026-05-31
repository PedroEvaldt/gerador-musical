from dataclasses import dataclass

from music_generator.domain.settings import PlaybackSettings


MAX_VOLUME = 127
MAX_OCTAVE = 9
MAX_INSTRUMENT = 127


@dataclass(slots=True)
class MusicalState:
    current_instrument: int
    current_octave: int
    current_volume: int
    default_octave: int
    last_played_note: str | None = None

    @classmethod
    def from_settings(cls, settings: PlaybackSettings) -> "MusicalState":
        return cls(
            current_instrument=settings.initial_instrument,
            current_octave=settings.default_octave,
            current_volume=settings.initial_volume,
            default_octave=settings.default_octave,
        )

    def double_volume(self) -> int:
        self.current_volume = min(self.current_volume * 2, MAX_VOLUME)
        return self.current_volume

    def increase_octave_or_reset(self) -> int:
        if self.current_octave < MAX_OCTAVE:
            self.current_octave += 1
        else:
            self.current_octave = self.default_octave
        return self.current_octave

    def decrease_octave_or_reset(self) -> int:
        if self.current_octave > 0:
            self.current_octave -= 1
        else:
            self.current_octave = self.default_octave
        return self.current_octave

    def change_instrument(self, instrument_id: int) -> int:
        if not 0 <= instrument_id <= MAX_INSTRUMENT:
            raise ValueError("instrument_id must be between 0 and 127.")
        self.current_instrument = instrument_id
        return self.current_instrument

    def increment_instrument(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount must be greater than or equal to 0.")
        self.current_instrument = min(
            self.current_instrument + amount,
            MAX_INSTRUMENT,
        )
        return self.current_instrument

    def set_last_played_note(self, note_name: str) -> None:
        self.last_played_note = note_name

    def clear_last_played_note(self) -> None:
        self.last_played_note = None
