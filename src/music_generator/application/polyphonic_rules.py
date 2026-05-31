from abc import ABC, abstractmethod
from dataclasses import dataclass

from music_generator.application.rules import DEFAULT_DURATION_BEATS
from music_generator.domain.events import (
    InstrumentChangeEvent,
    MusicalEvent,
    NoteEvent,
    OctaveChangeEvent,
    RestEvent,
    VolumeChangeEvent,
    note_to_midi_number,
)
from music_generator.domain.state import MusicalState


PHASE_TWO_NOTES = frozenset({"A", "B", "C", "D", "E", "Mb", "F", "G", "H"})
LOWERCASE_REST_CHARACTERS = frozenset("abcdefgh")
SPECIAL_VOWELS = frozenset("OoIiUu")
ODD_DIGITS = frozenset("13579")
EVEN_DIGITS = frozenset("02468")


@dataclass(frozen=True, slots=True)
class PhaseTwoInterpretationContext:
    state: MusicalState
    token: str
    previous_token_was_note: bool
    previous_note_name: str | None


@dataclass(frozen=True, slots=True)
class PhaseTwoRuleResult:
    event: MusicalEvent | None = None
    bpm_delta: int | None = None

    @property
    def advances_beat(self) -> bool:
        return isinstance(self.event, (NoteEvent, RestEvent))

    @property
    def generated_note(self) -> NoteEvent | None:
        if isinstance(self.event, NoteEvent):
            return self.event
        return None


class PhaseTwoTokenRule(ABC):
    @abstractmethod
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        raise NotImplementedError


def create_phase_two_note_event(note_name: str, state: MusicalState) -> NoteEvent:
    state.set_last_played_note(note_name)
    return NoteEvent(
        note_name=note_name,
        midi_number=note_to_midi_number(note_name, state.current_octave),
        octave=state.current_octave,
        volume=state.current_volume,
        instrument=state.current_instrument,
        duration_beats=DEFAULT_DURATION_BEATS,
    )


def create_phase_two_rest_event(state: MusicalState) -> RestEvent:
    state.clear_last_played_note()
    return RestEvent(duration_beats=DEFAULT_DURATION_BEATS)


class PhaseTwoNoteRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token in PHASE_TWO_NOTES

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=create_phase_two_note_event(context.token, context.state),
        )


class PhaseTwoLowercaseRestRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token in LOWERCASE_REST_CHARACTERS

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(event=create_phase_two_rest_event(context.state))


class PhaseTwoSpaceVolumeRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == " "

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=VolumeChangeEvent(volume=context.state.double_volume()),
        )


class PhaseTwoExclamationInstrumentRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == "!"

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=InstrumentChangeEvent(
                instrument=context.state.change_instrument(22),
            ),
        )


class PhaseTwoOctaveUpRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == "?"

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=OctaveChangeEvent(
                octave=context.state.increase_octave_or_reset(),
            ),
        )


class PhaseTwoOctaveDownRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == "V"

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=OctaveChangeEvent(
                octave=context.state.decrease_octave_or_reset(),
            ),
        )


class PhaseTwoSemicolonInstrumentRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == ";"

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=InstrumentChangeEvent(
                instrument=context.state.change_instrument(15),
            ),
        )


class PhaseTwoCommaInstrumentRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == ","

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=InstrumentChangeEvent(
                instrument=context.state.change_instrument(20),
            ),
        )


class PhaseTwoSpecialVowelInstrumentRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token in SPECIAL_VOWELS

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=InstrumentChangeEvent(
                instrument=context.state.change_instrument(110),
            ),
        )


class PhaseTwoEvenDigitInstrumentRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token in EVEN_DIGITS

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=InstrumentChangeEvent(
                instrument=context.state.increment_instrument(int(context.token)),
            ),
        )


class PhaseTwoOddDigitInstrumentRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token in ODD_DIGITS

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(
            event=InstrumentChangeEvent(
                instrument=context.state.change_instrument(15),
            ),
        )


class PhaseTwoBpmIncreaseRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == ">"

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(bpm_delta=10)


class PhaseTwoBpmDecreaseRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return context.token == "<"

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        return PhaseTwoRuleResult(bpm_delta=-10)


class PhaseTwoDefaultRule(PhaseTwoTokenRule):
    def matches(self, context: PhaseTwoInterpretationContext) -> bool:
        return True

    def apply(self, context: PhaseTwoInterpretationContext) -> PhaseTwoRuleResult:
        if context.previous_token_was_note and context.previous_note_name is not None:
            return PhaseTwoRuleResult(
                event=create_phase_two_note_event(
                    context.previous_note_name,
                    context.state,
                ),
            )
        return PhaseTwoRuleResult(event=create_phase_two_rest_event(context.state))


def default_phase_two_rules() -> list[PhaseTwoTokenRule]:
    return [
        PhaseTwoNoteRule(),
        PhaseTwoLowercaseRestRule(),
        PhaseTwoSpaceVolumeRule(),
        PhaseTwoExclamationInstrumentRule(),
        PhaseTwoOctaveUpRule(),
        PhaseTwoOctaveDownRule(),
        PhaseTwoSemicolonInstrumentRule(),
        PhaseTwoCommaInstrumentRule(),
        PhaseTwoSpecialVowelInstrumentRule(),
        PhaseTwoEvenDigitInstrumentRule(),
        PhaseTwoOddDigitInstrumentRule(),
        PhaseTwoBpmIncreaseRule(),
        PhaseTwoBpmDecreaseRule(),
        PhaseTwoDefaultRule(),
    ]
