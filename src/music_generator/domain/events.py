from abc import ABC
from dataclasses import dataclass


NOTE_SEMITONES: dict[str, int] = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "H": 10,
    "B": 11,
}


def note_to_midi_number(note_name: str, octave: int) -> int:
    normalized_note = note_name.upper()
    if normalized_note not in NOTE_SEMITONES:
        valid_notes = ", ".join(sorted(NOTE_SEMITONES))
        raise ValueError(f"note_name must be one of: {valid_notes}.")
    if not 0 <= octave <= 9:
        raise ValueError("octave must be between 0 and 9.")

    midi_number = (octave + 1) * 12 + NOTE_SEMITONES[normalized_note]
    if not 0 <= midi_number <= 127:
        raise ValueError(
            f"note {normalized_note}{octave} produces MIDI number "
            f"{midi_number}, outside the valid range 0-127."
        )
    return midi_number


@dataclass(frozen=True, slots=True)
class MusicalEvent(ABC):
    def __new__(cls, *args: object, **kwargs: object) -> "MusicalEvent":
        if cls is MusicalEvent:
            raise TypeError("MusicalEvent is an abstract base class.")
        return super().__new__(cls)


@dataclass(frozen=True, slots=True)
class NoteEvent(MusicalEvent):
    note_name: str
    midi_number: int
    octave: int
    volume: int
    instrument: int
    duration_beats: float


@dataclass(frozen=True, slots=True)
class RestEvent(MusicalEvent):
    duration_beats: float


@dataclass(frozen=True, slots=True)
class InstrumentChangeEvent(MusicalEvent):
    instrument: int


@dataclass(frozen=True, slots=True)
class VolumeChangeEvent(MusicalEvent):
    volume: int


@dataclass(frozen=True, slots=True)
class OctaveChangeEvent(MusicalEvent):
    octave: int
