import pytest

from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.domain.events import (
    BpmChangeEvent,
    InstrumentChangeEvent,
    NoteEndEvent,
    NoteEvent,
    NoteStartEvent,
    OctaveChangeEvent,
    RestEvent,
    VolumeChangeEvent,
)
from music_generator.domain.polyphony import VoiceSettings
from music_generator.domain.settings import PlaybackSettings


def generate(text: str):
    return PolyphonicSequenceGenerator().generate(text)


def timeline_events(text: str):
    return list(generate(text).timeline)


def note_starts(text: str) -> list[tuple[int, float, NoteEvent]]:
    starts: list[tuple[int, float, NoteEvent]] = []
    for scheduled in timeline_events(text):
        if isinstance(scheduled.event, NoteStartEvent):
            starts.append(
                (
                    scheduled.voice_index,
                    scheduled.absolute_beat,
                    scheduled.event.note,
                ),
            )
    return starts


def test_voice_settings_follow_four_voice_cycle() -> None:
    assert VoiceSettings.from_voice_index(0) == VoiceSettings(6, 100, 6)
    assert VoiceSettings.from_voice_index(1) == VoiceSettings(5, 80, 20)
    assert VoiceSettings.from_voice_index(2) == VoiceSettings(4, 60, 0)
    assert VoiceSettings.from_voice_index(3) == VoiceSettings(3, 40, 70)
    assert VoiceSettings.from_voice_index(4) == VoiceSettings(6, 100, 6)


def test_single_voice_generates_polyphonic_composition() -> None:
    composition = generate("C")

    assert [voice.voice_id for voice in composition.voices] == ["V0"]
    assert note_starts("C") == [
        (
            0,
            0.0,
            NoteEvent("C", 84, 6, 100, 6, 1.0),
        ),
    ]


def test_multiple_lines_generate_simultaneous_voices() -> None:
    starts = note_starts("C\nD")

    assert [(voice, beat, note.note_name) for voice, beat, note in starts] == [
        (0, 0.0, "C"),
        (1, 0.0, "D"),
    ]


def test_empty_internal_lines_are_preserved_and_final_newline_is_ignored() -> None:
    composition = generate("A\n\nB\n")

    assert [voice.voice_id for voice in composition.voices] == ["V0", "V1", "V2"]
    assert composition.voices[1].events == ()


@pytest.mark.parametrize("prefix", ["[0]C", "[4] C", "[4]    C"])
def test_initial_delay_accepts_zero_and_optional_spaces(prefix: str) -> None:
    composition = generate(prefix)

    [voice] = composition.voices
    expected_delay = int(prefix[1])
    assert voice.initial_delay_beats == expected_delay
    [start] = [event for event in composition.timeline if isinstance(event.event, NoteStartEvent)]
    assert start.absolute_beat == float(expected_delay)


@pytest.mark.parametrize("line", ["[x]C", "[-1]C", "[1 C", "[]C"])
def test_invalid_initial_delay_raises_clear_error(line: str) -> None:
    with pytest.raises(ValueError, match="initial delay"):
        generate(line)


def test_mb_is_tokenized_as_e_flat_before_single_character_rules() -> None:
    [(_, _, note)] = note_starts("Mb")

    assert note.note_name == "Mb"
    assert note.midi_number == 87


def test_phase_two_instrument_commands_for_exclamation_and_comma() -> None:
    composition = generate("!C\n,C")

    first_voice_note = next(
        event.event.note
        for event in composition.timeline
        if event.voice_index == 0 and isinstance(event.event, NoteStartEvent)
    )
    second_voice_note = next(
        event.event.note
        for event in composition.timeline
        if event.voice_index == 1 and isinstance(event.event, NoteStartEvent)
    )
    assert first_voice_note.instrument == 22
    assert second_voice_note.instrument == 20


def test_phase_two_octave_up_and_down_are_local_commands() -> None:
    composition = generate("?C\nVC")

    first_voice_note = next(
        event.event.note
        for event in composition.timeline
        if event.voice_index == 0 and isinstance(event.event, NoteStartEvent)
    )
    second_voice_note = next(
        event.event.note
        for event in composition.timeline
        if event.voice_index == 1 and isinstance(event.event, NoteStartEvent)
    )
    assert first_voice_note.octave == 7
    assert second_voice_note.octave == 4


def test_octave_commands_wrap_to_base_octave() -> None:
    [(_, _, note)] = note_starts("????C")

    assert note.octave == 6


def test_global_bpm_changes_after_initial_delay_and_before_note() -> None:
    composition = generate("[4]>C")

    events_at_four = [
        scheduled.event for scheduled in composition.timeline if scheduled.absolute_beat == 4.0
    ]
    assert [type(event) for event in events_at_four] == [BpmChangeEvent, NoteStartEvent]
    assert isinstance(events_at_four[0], BpmChangeEvent)
    assert events_at_four[0].bpm == 130


def test_bpm_decrease_never_goes_below_ten() -> None:
    composition = PolyphonicSequenceGenerator().generate(
        "<<C",
        PlaybackSettings(
            bpm=20,
            initial_volume=80,
            default_octave=4,
            initial_instrument=0,
        ),
    )

    bpm_events = [
        scheduled.event for scheduled in composition.timeline if isinstance(scheduled.event, BpmChangeEvent)
    ]
    assert [event.bpm for event in bpm_events] == [10, 10]


def test_phase_one_rules_not_replaced_are_kept_in_phase_two() -> None:
    composition = generate("O2C3C")

    local_events = composition.voices[0].events
    assert isinstance(local_events[0], InstrumentChangeEvent)
    assert local_events[0].instrument == 110
    assert isinstance(local_events[1], InstrumentChangeEvent)
    assert local_events[1].instrument == 112
    assert isinstance(local_events[3], InstrumentChangeEvent)
    assert local_events[3].instrument == 15


def test_dot_follows_generic_rule_in_phase_two() -> None:
    composition = generate(".\nA.")

    assert isinstance(composition.voices[0].events[0], RestEvent)
    second_voice_events = composition.voices[1].events
    assert [event.note_name for event in second_voice_events if isinstance(event, NoteEvent)] == [
        "A",
        "A",
    ]


def test_volume_instrument_and_octave_are_isolated_between_voices() -> None:
    starts = note_starts(" ?C\nC")

    first_voice_note = starts[0][2]
    second_voice_note = starts[1][2]
    assert first_voice_note.volume == 127
    assert first_voice_note.octave == 7
    assert second_voice_note.volume == 80
    assert second_voice_note.octave == 5


def test_timeline_orders_note_endings_before_new_starts_at_same_beat() -> None:
    scheduled_events = [
        (event.absolute_beat, event.voice_index, type(event.event))
        for event in timeline_events("CC\n[1]C")
        if event.absolute_beat == 1.0
    ]

    assert scheduled_events == [
        (1.0, 0, NoteEndEvent),
        (1.0, 0, NoteStartEvent),
        (1.0, 1, NoteStartEvent),
    ]


def test_timeline_orders_simultaneous_events_by_voice_and_origin() -> None:
    starts = [
        (event.voice_index, event.origin_order)
        for event in timeline_events("CC\nCC")
        if event.absolute_beat == 0.0 and isinstance(event.event, NoteStartEvent)
    ]

    assert starts == [(0, 0), (1, 0)]


def test_more_than_fifteen_voices_raise_clear_error() -> None:
    text = "\n".join("C" for _ in range(16))

    with pytest.raises(ValueError, match="at most 15"):
        generate(text)


def test_local_command_events_are_available_for_export_integration() -> None:
    composition = generate(" !?;,C")

    assert [type(event) for event in composition.voices[0].events[:5]] == [
        VolumeChangeEvent,
        InstrumentChangeEvent,
        OctaveChangeEvent,
        InstrumentChangeEvent,
        InstrumentChangeEvent,
    ]
