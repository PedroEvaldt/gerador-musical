"""Core package for the musical text generator."""

from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.application.sequence_generator import SequenceGenerator
from music_generator.domain.polyphony import PolyphonicComposition
from music_generator.domain.settings import PlaybackSettings

__all__ = [
    "PlaybackSettings",
    "PolyphonicComposition",
    "PolyphonicSequenceGenerator",
    "SequenceGenerator",
]
