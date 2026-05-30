from music_generator.application.sequence_generator import SequenceGenerator
from music_generator.domain.events import NoteEvent
from music_generator.domain.settings import PlaybackSettings


def test_sequence_generator_builds_initial_state_and_generates_composition() -> None:
    settings = PlaybackSettings(
        bpm=140,
        initial_volume=64,
        default_octave=5,
        initial_instrument=12,
    )

    composition = SequenceGenerator().generate("C", settings)

    [event] = list(composition)
    assert composition.initial_bpm == 140
    assert isinstance(event, NoteEvent)
    assert event.octave == 5
    assert event.volume == 64
    assert event.instrument == 12
