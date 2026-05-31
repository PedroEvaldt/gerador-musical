from collections.abc import Sequence

from music_generator.application.initial_delay_parser import InitialDelayParser
from music_generator.application.polyphonic_rules import (
    PhaseTwoInterpretationContext,
    PhaseTwoRuleResult,
    PhaseTwoTokenRule,
    default_phase_two_rules,
)
from music_generator.application.timeline_scheduler import (
    BpmChangeCommand,
    TimelineScheduler,
)
from music_generator.domain.events import MusicalEvent, NoteEvent, NoteStartEvent
from music_generator.domain.polyphony import (
    MAX_MELODIC_VOICES,
    MusicalVoice,
    PolyphonicComposition,
    ScheduledMusicalEvent,
    VoiceSettings,
)
from music_generator.domain.settings import PlaybackSettings
from music_generator.domain.state import MusicalState


class PolyphonicSequenceGenerator:
    def __init__(
        self,
        rules: Sequence[PhaseTwoTokenRule] | None = None,
        initial_delay_parser: InitialDelayParser | None = None,
        scheduler: TimelineScheduler | None = None,
    ) -> None:
        self._rules = tuple(default_phase_two_rules() if rules is None else rules)
        self._initial_delay_parser = initial_delay_parser or InitialDelayParser()
        self._scheduler = scheduler or TimelineScheduler()

    def generate(
        self,
        text: str,
        settings: PlaybackSettings | None = None,
    ) -> PolyphonicComposition:
        initial_bpm = 120 if settings is None else settings.bpm
        if initial_bpm < 10:
            raise ValueError("initial BPM must be greater than or equal to 10.")

        lines = text.splitlines()
        if len(lines) > MAX_MELODIC_VOICES:
            raise ValueError(
                f"Polyphonic playback supports at most {MAX_MELODIC_VOICES} "
                "melodic voices."
            )

        voices: list[MusicalVoice] = []
        note_events: list[ScheduledMusicalEvent] = []
        bpm_commands: list[BpmChangeCommand] = []

        for voice_index, line in enumerate(lines):
            voice, voice_note_events, voice_bpm_commands = self._interpret_voice(
                voice_index=voice_index,
                line=line,
            )
            voices.append(voice)
            note_events.extend(voice_note_events)
            bpm_commands.extend(voice_bpm_commands)

        timeline = self._scheduler.schedule(
            note_events=note_events,
            bpm_commands=bpm_commands,
            initial_bpm=initial_bpm,
        )
        return PolyphonicComposition(
            voices=voices,
            timeline=timeline,
            initial_bpm=initial_bpm,
        )

    def _interpret_voice(
        self,
        voice_index: int,
        line: str,
    ) -> tuple[MusicalVoice, list[ScheduledMusicalEvent], list[BpmChangeCommand]]:
        parsed_line = self._initial_delay_parser.parse(line)
        voice_settings = VoiceSettings.from_voice_index(voice_index)
        state = MusicalState(
            current_instrument=voice_settings.initial_instrument,
            current_octave=voice_settings.base_octave,
            current_volume=voice_settings.initial_volume,
            default_octave=voice_settings.base_octave,
        )
        current_beat = float(parsed_line.initial_delay_beats)
        local_events: list[MusicalEvent] = []
        note_events: list[ScheduledMusicalEvent] = []
        bpm_commands: list[BpmChangeCommand] = []
        previous_token_was_note = False
        previous_note_name: str | None = None

        for origin_order, token in enumerate(self._tokenize(parsed_line.body)):
            result = self._apply_first_matching_rule(
                PhaseTwoInterpretationContext(
                    state=state,
                    token=token,
                    previous_token_was_note=previous_token_was_note,
                    previous_note_name=previous_note_name,
                ),
            )
            if result.event is not None:
                local_events.append(result.event)
            if isinstance(result.event, NoteEvent):
                note_events.extend(
                    self._scheduler.note_start_and_end(
                        note=NoteStartEvent(note=result.event),
                        absolute_beat=current_beat,
                        voice_index=voice_index,
                        origin_order=origin_order,
                    ),
                )
            if result.bpm_delta is not None:
                bpm_commands.append(
                    BpmChangeCommand(
                        absolute_beat=current_beat,
                        voice_index=voice_index,
                        origin_order=origin_order,
                        delta=result.bpm_delta,
                    ),
                )
            if result.advances_beat:
                current_beat += result.event.duration_beats  # type: ignore[union-attr]

            generated_note = result.generated_note
            previous_token_was_note = generated_note is not None
            previous_note_name = generated_note.note_name if generated_note else None

        return (
            MusicalVoice(
                voice_index=voice_index,
                settings=voice_settings,
                initial_delay_beats=parsed_line.initial_delay_beats,
                source_text=parsed_line.body,
                events=local_events,
            ),
            note_events,
            bpm_commands,
        )

    def _apply_first_matching_rule(
        self,
        context: PhaseTwoInterpretationContext,
    ) -> PhaseTwoRuleResult:
        for rule in self._rules:
            if rule.matches(context):
                return rule.apply(context)
        raise RuntimeError("No phase 2 token rule matched the current token.")

    def _tokenize(self, text: str) -> list[str]:
        tokens: list[str] = []
        index = 0
        while index < len(text):
            if text.startswith("Mb", index):
                tokens.append("Mb")
                index += 2
            else:
                tokens.append(text[index])
                index += 1
        return tokens
