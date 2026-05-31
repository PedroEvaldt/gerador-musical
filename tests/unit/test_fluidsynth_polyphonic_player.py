import threading

from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer


class FakeSynth:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def program_select(
        self,
        channel: int,
        soundfont_id: int,
        bank: int,
        instrument: int,
    ) -> None:
        self.calls.append(("program_select", channel, soundfont_id, bank, instrument))

    def noteon(self, channel: int, midi_number: int, volume: int) -> None:
        self.calls.append(("noteon", channel, midi_number, volume))

    def noteoff(self, channel: int, midi_number: int) -> None:
        self.calls.append(("noteoff", channel, midi_number))


def make_player_without_native_fluidsynth(fake_synth: FakeSynth) -> FluidSynthPlayer:
    player = object.__new__(FluidSynthPlayer)
    player._stop_event = threading.Event()
    player._lock = threading.RLock()
    player._active_note = None
    player._active_notes = set()
    player._current_instrument_by_channel = {}
    player._closed = False
    player._synth = fake_synth
    player._soundfont_id = 1
    player._wait = lambda _seconds: None
    return player


def test_fluidsynth_player_uses_distinct_melodic_channels_for_polyphony() -> None:
    fake_synth = FakeSynth()
    player = make_player_without_native_fluidsynth(fake_synth)
    composition = PolyphonicSequenceGenerator().generate("C\nD")

    player.play(composition)

    noteon_calls = [call for call in fake_synth.calls if call[0] == "noteon"]
    noteoff_calls = [call for call in fake_synth.calls if call[0] == "noteoff"]
    assert noteon_calls == [
        ("noteon", 0, 84, 100),
        ("noteon", 1, 74, 80),
    ]
    assert noteoff_calls == [
        ("noteoff", 0, 84),
        ("noteoff", 1, 74),
    ]
    assert all(call[1] != 9 for call in noteon_calls)
