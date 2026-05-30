from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass

from music_generator.domain.events import MusicalEvent


@dataclass(frozen=True, slots=True)
class MusicalComposition:
    _events: tuple[MusicalEvent, ...]
    initial_bpm: int

    def __init__(
        self,
        events: Iterable[MusicalEvent],
        initial_bpm: int,
    ) -> None:
        if initial_bpm <= 0:
            raise ValueError("initial_bpm must be greater than 0.")
        object.__setattr__(self, "_events", tuple(events))
        object.__setattr__(self, "initial_bpm", initial_bpm)

    def __iter__(self) -> Iterator[MusicalEvent]:
        return iter(self._events)

    def __len__(self) -> int:
        return len(self._events)

    @property
    def events(self) -> Sequence[MusicalEvent]:
        return self._events
