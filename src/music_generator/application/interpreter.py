from collections.abc import Sequence

from music_generator.application.rules import (
    CharacterMappingRule,
    InterpretationContext,
    default_phase_one_rules,
)
from music_generator.domain.composition import MusicalComposition
from music_generator.domain.events import MusicalEvent
from music_generator.domain.settings import PlaybackSettings
from music_generator.domain.state import MusicalState


class TextInterpreter:
    def __init__(self, rules: Sequence[CharacterMappingRule] | None = None) -> None:
        self._rules = tuple(default_phase_one_rules() if rules is None else rules)

    @classmethod
    def with_default_phase_one_rules(cls) -> "TextInterpreter":
        return cls(default_phase_one_rules())

    def interpret(
        self,
        text: str,
        settings: PlaybackSettings,
        state: MusicalState,
    ) -> MusicalComposition:
        events: list[MusicalEvent] = []
        previous_character: str | None = None

        for index, current_character in enumerate(text):
            context = InterpretationContext(
                state=state,
                current_character=current_character,
                previous_character=previous_character,
                index=index,
                settings=settings,
            )
            events.append(self._apply_first_matching_rule(context))
            previous_character = current_character

        return MusicalComposition(events=events, initial_bpm=settings.bpm)

    def _apply_first_matching_rule(
        self,
        context: InterpretationContext,
    ) -> MusicalEvent:
        for rule in self._rules:
            if rule.matches(context):
                return rule.apply(context)
        raise RuntimeError("No character mapping rule matched the current character.")
