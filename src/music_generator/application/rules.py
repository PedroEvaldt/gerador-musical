from abc import ABC, abstractmethod
from dataclasses import dataclass

from music_generator.domain.events import (
    InstrumentChangeEvent,
    MusicalEvent,
    NoteEvent,
    OctaveChangeEvent,
    RestEvent,
    VolumeChangeEvent,
    note_to_midi_number,
)
from music_generator.domain.settings import PlaybackSettings
from music_generator.domain.state import MusicalState


DEFAULT_DURATION_BEATS = 1.0
NOTE_CHARACTERS = frozenset("ABCDEFGH")
LOWERCASE_REST_CHARACTERS = frozenset("abcdefgh")
SPECIAL_VOWELS = frozenset("OoIiUu")
ODD_DIGITS = frozenset("13579")
EVEN_DIGITS = frozenset("02468")


@dataclass(slots=True)
class InterpretationContext:
    state: MusicalState
    current_character: str
    previous_character: str | None
    index: int
    settings: PlaybackSettings


class CharacterMappingRule(ABC):
    @abstractmethod
    def matches(self, context: InterpretationContext) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self, context: InterpretationContext) -> MusicalEvent:
        raise NotImplementedError


def create_note_event(note_name: str, state: MusicalState) -> NoteEvent:
    normalized_note = note_name.upper()
    state.set_last_played_note(normalized_note)
    return NoteEvent(
        note_name=normalized_note,
        midi_number=note_to_midi_number(normalized_note, state.current_octave),
        octave=state.current_octave,
        volume=state.current_volume,
        instrument=state.current_instrument,
        duration_beats=DEFAULT_DURATION_BEATS,
    )


def create_rest_event(state: MusicalState) -> RestEvent:
    state.clear_last_played_note()
    return RestEvent(duration_beats=DEFAULT_DURATION_BEATS)


def previous_character_is_note(context: InterpretationContext) -> bool:
    return context.previous_character in NOTE_CHARACTERS


def repeat_previous_note_or_rest(context: InterpretationContext) -> MusicalEvent:
    if previous_character_is_note(context):
        return create_note_event(context.previous_character or "", context.state)
    return create_rest_event(context.state)


class UppercaseNoteRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character in NOTE_CHARACTERS

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return create_note_event(context.current_character, context.state)


class LowercaseRestRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character in LOWERCASE_REST_CHARACTERS

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return create_rest_event(context.state)


class SpaceVolumeRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character == " "

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return VolumeChangeEvent(volume=context.state.double_volume())


class ExclamationInstrumentRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character == "!"

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return InstrumentChangeEvent(
            instrument=context.state.change_instrument(24),
        )


class SpecialVowelInstrumentRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character in SPECIAL_VOWELS

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return InstrumentChangeEvent(
            instrument=context.state.change_instrument(110),
        )


class OtherConsonantRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        character = context.current_character
        return character.isalpha() and character.upper() not in "AEIOU"

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return repeat_previous_note_or_rest(context)


class EvenDigitInstrumentRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character in EVEN_DIGITS

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        amount = int(context.current_character)
        return InstrumentChangeEvent(
            instrument=context.state.increment_instrument(amount),
        )


class OctaveMarkerRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character in {"?", "."}

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return OctaveChangeEvent(octave=context.state.increase_octave_or_reset())


class NewlineInstrumentRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character == "\n"

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return InstrumentChangeEvent(
            instrument=context.state.change_instrument(123),
        )


class OddDigitOrSemicolonRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character == ";" or context.current_character in ODD_DIGITS

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return InstrumentChangeEvent(
            instrument=context.state.change_instrument(15),
        )


class CommaInstrumentRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return context.current_character == ","

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return InstrumentChangeEvent(
            instrument=context.state.change_instrument(114),
        )


class DefaultRule(CharacterMappingRule):
    def matches(self, context: InterpretationContext) -> bool:
        return True

    def apply(self, context: InterpretationContext) -> MusicalEvent:
        return repeat_previous_note_or_rest(context)


def default_phase_one_rules() -> list[CharacterMappingRule]:
    return [
        UppercaseNoteRule(),
        LowercaseRestRule(),
        SpaceVolumeRule(),
        ExclamationInstrumentRule(),
        SpecialVowelInstrumentRule(),
        OtherConsonantRule(),
        EvenDigitInstrumentRule(),
        OctaveMarkerRule(),
        NewlineInstrumentRule(),
        OddDigitOrSemicolonRule(),
        CommaInstrumentRule(),
        DefaultRule(),
    ]
