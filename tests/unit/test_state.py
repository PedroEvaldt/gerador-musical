import pytest

from music_generator.domain.settings import PlaybackSettings
from music_generator.domain.state import MusicalState


def test_state_is_created_from_settings() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=4,
        initial_instrument=10,
    )

    state = MusicalState.from_settings(settings)

    assert state.current_instrument == 10
    assert state.current_octave == 4
    assert state.current_volume == 80
    assert state.default_octave == 4
    assert state.last_played_note is None


def test_double_volume_saturates_at_127() -> None:
    state = MusicalState(0, 4, 80, 4)

    assert state.double_volume() == 127
    assert state.current_volume == 127


def test_increase_octave_or_reset_returns_to_default_at_maximum() -> None:
    state = MusicalState(0, 9, 80, 4)

    assert state.increase_octave_or_reset() == 4
    assert state.current_octave == 4


def test_increase_octave_increments_when_possible() -> None:
    state = MusicalState(0, 4, 80, 4)

    assert state.increase_octave_or_reset() == 5


def test_increment_instrument_saturates_at_127() -> None:
    state = MusicalState(126, 4, 80, 4)

    assert state.increment_instrument(8) == 127
    assert state.current_instrument == 127


def test_change_instrument_validates_range() -> None:
    state = MusicalState(0, 4, 80, 4)

    with pytest.raises(ValueError, match="instrument_id"):
        state.change_instrument(128)


def test_last_played_note_can_be_set_and_cleared() -> None:
    state = MusicalState(0, 4, 80, 4)

    state.set_last_played_note("A")
    assert state.last_played_note == "A"

    state.clear_last_played_note()
    assert state.last_played_note is None
