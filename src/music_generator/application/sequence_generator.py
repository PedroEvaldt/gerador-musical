from music_generator.application.interpreter import TextInterpreter
from music_generator.domain.composition import MusicalComposition
from music_generator.domain.settings import PlaybackSettings
from music_generator.domain.state import MusicalState


class SequenceGenerator:
    def __init__(self, interpreter: TextInterpreter | None = None) -> None:
        self._interpreter = interpreter or TextInterpreter.with_default_phase_one_rules()

    def generate(
        self,
        text: str,
        settings: PlaybackSettings,
    ) -> MusicalComposition:
        state = MusicalState.from_settings(settings)
        return self._interpreter.interpret(text=text, settings=settings, state=state)
