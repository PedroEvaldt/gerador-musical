import threading

from music_generator.domain.composition import MusicalComposition
from music_generator.domain.polyphony import PolyphonicComposition
from music_generator.infrastructure.audio.player import AudioPlayer


PlayableComposition = MusicalComposition | PolyphonicComposition


class PlaybackService:
    def __init__(self, player: AudioPlayer) -> None:
        self._player = player
        self._lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._is_playing = False

    def start(self, composition: PlayableComposition) -> None:
        with self._lock:
            if self._is_playing:
                raise RuntimeError("Playback is already running.")
            self._is_playing = True
            self._thread = threading.Thread(
                target=self._run,
                args=(composition,),
                name="music-generator-playback",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        thread: threading.Thread | None
        with self._lock:
            thread = self._thread
        self._player.stop()
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
        with self._lock:
            if self._thread is thread and (thread is None or not thread.is_alive()):
                self._is_playing = False

    def is_playing(self) -> bool:
        with self._lock:
            return self._is_playing

    def close(self) -> None:
        self.stop()
        self._player.close()

    def _run(self, composition: PlayableComposition) -> None:
        try:
            self._player.play(composition)
        finally:
            with self._lock:
                self._is_playing = False
