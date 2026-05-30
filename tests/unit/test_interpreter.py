from music_generator.application.interpreter import TextInterpreter
from music_generator.domain.events import (
    InstrumentChangeEvent,
    NoteEvent,
    RestEvent,
    VolumeChangeEvent,
)
from music_generator.domain.settings import PlaybackSettings
from music_generator.domain.state import MusicalState


def test_interpreter_preserves_event_order() -> None:
    settings = PlaybackSettings(
        bpm=90,
        initial_volume=40,
        default_octave=4,
        initial_instrument=0,
    )
    state = MusicalState.from_settings(settings)

    composition = TextInterpreter.with_default_phase_one_rules().interpret(
        text="A b!",
        settings=settings,
        state=state,
    )

    events = list(composition)
    assert composition.initial_bpm == 90
    assert [type(event) for event in events] == [
        NoteEvent,
        VolumeChangeEvent,
        RestEvent,
        InstrumentChangeEvent,
    ]


def test_note_event_uses_snapshot_of_current_state() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=70,
        default_octave=4,
        initial_instrument=10,
    )
    state = MusicalState.from_settings(settings)

    composition = TextInterpreter.with_default_phase_one_rules().interpret(
        text="A B",
        settings=settings,
        state=state,
    )

    first_note, _, second_note = list(composition)
    assert isinstance(first_note, NoteEvent)
    assert first_note.volume == 70
    assert first_note.instrument == 10
    assert isinstance(second_note, NoteEvent)
    assert second_note.volume == 127
    assert second_note.instrument == 10


def test_composition_events_are_not_exposed_as_mutable_list() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=4,
        initial_instrument=0,
    )
    state = MusicalState.from_settings(settings)

    composition = TextInterpreter.with_default_phase_one_rules().interpret(
        text="A",
        settings=settings,
        state=state,
    )

    assert isinstance(composition.events, tuple)
