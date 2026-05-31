from abc import ABC, abstractmethod

from music_generator.domain.composition import MusicalComposition
from music_generator.domain.polyphony import PolyphonicComposition


PlayableComposition = MusicalComposition | PolyphonicComposition


class AudioPlayer(ABC):
    @abstractmethod
    def play(self, composition: PlayableComposition) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
