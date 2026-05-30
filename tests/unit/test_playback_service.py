import threading
import time

import pytest

from music_generator.application.playback_service import PlaybackService
from music_generator.domain.composition import MusicalComposition
from music_generator.domain.events import RestEvent
from music_generator.infrastructure.audio.player import AudioPlayer


class FakePlayer(AudioPlayer):
    def __init__(self) -> None:
        self.started = threading.Event()
        self.stop_requested = threading.Event()
        self.closed = False
        self.play_calls = 0

    def play(self, composition: MusicalComposition) -> None:
        self.play_calls += 1
        self.started.set()
        self.stop_requested.wait(timeout=2.0)

    def stop(self) -> None:
        self.stop_requested.set()

    def close(self) -> None:
        self.closed = True


def make_composition() -> MusicalComposition:
    return MusicalComposition(
        events=[RestEvent(duration_beats=1.0)],
        initial_bpm=120,
    )


def test_playback_service_starts_without_blocking() -> None:
    player = FakePlayer()
    service = PlaybackService(player)

    service.start(make_composition())

    assert player.started.wait(timeout=1.0)
    assert service.is_playing()

    service.stop()


def test_playback_service_prevents_two_simultaneous_runs() -> None:
    player = FakePlayer()
    service = PlaybackService(player)
    service.start(make_composition())
    assert player.started.wait(timeout=1.0)

    with pytest.raises(RuntimeError, match="already running"):
        service.start(make_composition())

    service.stop()


def test_playback_service_stop_interrupts_playback() -> None:
    player = FakePlayer()
    service = PlaybackService(player)
    service.start(make_composition())
    assert player.started.wait(timeout=1.0)

    service.stop()
    time.sleep(0.01)

    assert not service.is_playing()


def test_playback_service_close_stops_and_closes_player() -> None:
    player = FakePlayer()
    service = PlaybackService(player)
    service.start(make_composition())
    assert player.started.wait(timeout=1.0)

    service.close()

    assert not service.is_playing()
    assert player.closed
