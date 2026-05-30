from abc import ABC, abstractmethod

from music_generator.domain.composition import MusicalComposition


class AudioPlayer(ABC):
    @abstractmethod
    def play(self, composition: MusicalComposition) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
