from dataclasses import dataclass

from music_generator.domain.events import BpmChangeEvent, NoteEndEvent, NoteStartEvent
from music_generator.domain.polyphony import ScheduledMusicalEvent


MIN_BPM = 10


@dataclass(frozen=True, slots=True)
class BpmChangeCommand:
    absolute_beat: float
    voice_index: int
    origin_order: int
    delta: int

    @property
    def sort_key(self) -> tuple[float, int, int]:
        return (self.absolute_beat, self.voice_index, self.origin_order)


class TimelineScheduler:
    def schedule(
        self,
        note_events: list[ScheduledMusicalEvent],
        bpm_commands: list[BpmChangeCommand],
        initial_bpm: int,
    ) -> tuple[ScheduledMusicalEvent, ...]:
        if initial_bpm < MIN_BPM:
            raise ValueError("initial_bpm must be greater than or equal to 10.")

        timeline = list(note_events)
        current_bpm = initial_bpm

        for command in sorted(bpm_commands, key=lambda item: item.sort_key):
            current_bpm = max(MIN_BPM, current_bpm + command.delta)
            timeline.append(
                ScheduledMusicalEvent(
                    absolute_beat=command.absolute_beat,
                    voice_index=command.voice_index,
                    origin_order=command.origin_order,
                    event=BpmChangeEvent(bpm=current_bpm),
                ),
            )

        return tuple(sorted(timeline, key=lambda item: item.sort_key))

    def note_start_and_end(
        self,
        note: NoteStartEvent,
        absolute_beat: float,
        voice_index: int,
        origin_order: int,
    ) -> tuple[ScheduledMusicalEvent, ScheduledMusicalEvent]:
        return (
            ScheduledMusicalEvent(
                absolute_beat=absolute_beat,
                voice_index=voice_index,
                origin_order=origin_order,
                event=note,
            ),
            ScheduledMusicalEvent(
                absolute_beat=absolute_beat + note.note.duration_beats,
                voice_index=voice_index,
                origin_order=origin_order,
                event=NoteEndEvent(note=note.note),
            ),
        )
