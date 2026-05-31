import threading
import time

from music_generator.application.playback_service import PlaybackService
from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.domain.composition import MusicalComposition
from music_generator.domain.polyphony import PolyphonicComposition
from music_generator.infrastructure.audio.player import AudioPlayer


class FakePolyphonicPlayer(AudioPlayer):
    def __init__(self) -> None:
        self.started = threading.Event()
        self.stop_requested = threading.Event()
        self.received_composition: PolyphonicComposition | None = None

    def play(self, composition: MusicalComposition | PolyphonicComposition) -> None:
        assert isinstance(composition, PolyphonicComposition)
        self.received_composition = composition
        self.started.set()
        self.stop_requested.wait(timeout=2.0)

    def stop(self) -> None:
        self.stop_requested.set()

    def close(self) -> None:
        self.stop()


def test_playback_service_interrupts_polyphonic_playback_without_fluidsynth() -> None:
    composition = PolyphonicSequenceGenerator().generate("C\n[1]D")
    player = FakePolyphonicPlayer()
    service = PlaybackService(player)

    service.start(composition)
    assert player.started.wait(timeout=1.0)

    service.stop()
    time.sleep(0.01)

    assert not service.is_playing()
    assert player.received_composition is composition
