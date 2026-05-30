import pytest

from music_generator.application.sequence_generator import SequenceGenerator
from music_generator.domain.events import (
    InstrumentChangeEvent,
    NoteEvent,
    OctaveChangeEvent,
    RestEvent,
    VolumeChangeEvent,
    note_to_midi_number,
)
from music_generator.domain.settings import PlaybackSettings


@pytest.fixture
def settings() -> PlaybackSettings:
    return PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=4,
        initial_instrument=0,
    )


def generate_events(text: str, settings: PlaybackSettings) -> list[object]:
    return list(SequenceGenerator().generate(text, settings))


@pytest.mark.parametrize(
    ("note", "expected"),
    [
        ("C", 60),
        ("D", 62),
        ("E", 64),
        ("F", 65),
        ("G", 67),
        ("A", 69),
        ("H", 70),
        ("B", 71),
    ],
)
def test_note_to_midi_number_for_each_supported_note(
    note: str,
    expected: int,
) -> None:
    assert note_to_midi_number(note, 4) == expected


def test_h_represents_b_flat() -> None:
    assert note_to_midi_number("H", 4) == 70


@pytest.mark.parametrize("character", list("ABCDEFGH"))
def test_uppercase_letters_generate_notes(
    character: str,
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events(character, settings)

    assert isinstance(event, NoteEvent)
    assert event.note_name == character
    assert event.duration_beats == 1.0


@pytest.mark.parametrize("character", list("abcdefgh"))
def test_lowercase_a_to_h_generate_rests(
    character: str,
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events(character, settings)

    assert isinstance(event, RestEvent)
    assert event.duration_beats == 1.0


def test_space_doubles_volume_and_generates_volume_change(
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events(" ", settings)

    assert isinstance(event, VolumeChangeEvent)
    assert event.volume == 127


def test_exclamation_changes_instrument_to_24(
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events("!", settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 24


@pytest.mark.parametrize("character", list("OoIiUu"))
def test_special_vowels_change_instrument_to_110(
    character: str,
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events(character, settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 110


def test_other_consonant_repeats_immediately_previous_note(
    settings: PlaybackSettings,
) -> None:
    events = generate_events("AZ", settings)

    assert isinstance(events[0], NoteEvent)
    assert isinstance(events[1], NoteEvent)
    assert events[1].note_name == "A"


def test_other_consonant_without_previous_note_generates_rest(
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events("Z", settings)

    assert isinstance(event, RestEvent)


def test_even_digit_increments_current_instrument(
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events("8", settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 8


def test_even_digit_instrument_increment_saturates_at_127() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=4,
        initial_instrument=126,
    )

    [event] = generate_events("8", settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 127


@pytest.mark.parametrize("character", ["?", "."])
def test_octave_markers_increase_octave(
    character: str,
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events(character, settings)

    assert isinstance(event, OctaveChangeEvent)
    assert event.octave == 5


def test_octave_marker_resets_to_default_when_at_maximum() -> None:
    settings = PlaybackSettings(
        bpm=120,
        initial_volume=80,
        default_octave=9,
        initial_instrument=0,
    )

    [event] = generate_events("?", settings)

    assert isinstance(event, OctaveChangeEvent)
    assert event.octave == 9


def test_newline_changes_instrument_to_123(settings: PlaybackSettings) -> None:
    [event] = generate_events("\n", settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 123


def test_semicolon_changes_instrument_to_15(settings: PlaybackSettings) -> None:
    [event] = generate_events(";", settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 15


@pytest.mark.parametrize("character", list("13579"))
def test_odd_digits_change_instrument_to_15(
    character: str,
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events(character, settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 15


def test_comma_changes_instrument_to_114(settings: PlaybackSettings) -> None:
    [event] = generate_events(",", settings)

    assert isinstance(event, InstrumentChangeEvent)
    assert event.instrument == 114


def test_default_rule_repeats_immediately_previous_note(
    settings: PlaybackSettings,
) -> None:
    events = generate_events("A@", settings)

    assert isinstance(events[1], NoteEvent)
    assert events[1].note_name == "A"


def test_default_rule_without_previous_note_generates_rest(
    settings: PlaybackSettings,
) -> None:
    [event] = generate_events("@", settings)

    assert isinstance(event, RestEvent)


def test_repetition_uses_only_immediately_previous_character(
    settings: PlaybackSettings,
) -> None:
    events = generate_events("A @", settings)

    assert isinstance(events[0], NoteEvent)
    assert isinstance(events[1], VolumeChangeEvent)
    assert isinstance(events[2], RestEvent)


def test_rule_priority_treats_h_as_lowercase_rest_not_consonant_repeat(
    settings: PlaybackSettings,
) -> None:
    events = generate_events("Ah", settings)

    assert isinstance(events[0], NoteEvent)
    assert isinstance(events[1], RestEvent)


def test_rule_priority_treats_uppercase_a_as_note(settings: PlaybackSettings) -> None:
    [event] = generate_events("A", settings)

    assert isinstance(event, NoteEvent)
    assert event.note_name == "A"
