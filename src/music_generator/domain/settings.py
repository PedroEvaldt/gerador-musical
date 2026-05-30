from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlaybackSettings:
    bpm: int
    initial_volume: int
    default_octave: int
    initial_instrument: int

    def __post_init__(self) -> None:
        if self.bpm <= 0:
            raise ValueError("bpm must be greater than 0.")
        if not 0 <= self.initial_volume <= 127:
            raise ValueError("initial_volume must be between 0 and 127.")
        if not 0 <= self.default_octave <= 9:
            raise ValueError("default_octave must be between 0 and 9.")
        if not 0 <= self.initial_instrument <= 127:
            raise ValueError("initial_instrument must be between 0 and 127.")
