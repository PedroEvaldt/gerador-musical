"""
Controlador de reprodução.
Arquivo: src/music_generator/gui/playback_controller.py

Orquestra geração da composição, início/pausa/retomada da reprodução e
cálculo de progresso. Depende apenas de abstrações (`AudioPlayer`,
`PolyphonicSequenceGenerator`) injetadas no construtor — não conhece
Tkinter nem widgets concretos. A comunicação com a interface acontece
por meio de callbacks simples (funções), o que mantém o controlador
livre de qualquer framework de UI e, portanto, testável isoladamente.
"""

from collections.abc import Callable

from music_generator.application.playback_service import PlaybackService
from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.domain.polyphony import PolyphonicComposition
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.audio.player import AudioPlayer


class PlaybackController:
    """Controla o ciclo de vida da reprodução de uma composição polifônica."""

    def __init__(
        self,
        player_factory: Callable[[], AudioPlayer],
        generator: PolyphonicSequenceGenerator | None = None,
    ) -> None:
        """
        player_factory: função que cria um novo AudioPlayer quando chamada.
            Recebida por injeção para que o controlador não conheça (nem
            instancie diretamente) nenhuma implementação concreta, como o
            FluidSynthPlayer — basta trocar a fábrica para usar outro
            player, sem alterar este controlador (Aberto/Fechado).
        generator: gerador de sequência polifônica; injetável para testes.
        """
        self._player_factory = player_factory
        self._generator = generator or PolyphonicSequenceGenerator()
        self._playback_service: PlaybackService | None = None
        self._composition: PolyphonicComposition | None = None
        self._total_seconds: float = 0.0
        self._elapsed_seconds: float = 0.0

    def is_playing(self) -> bool:
        return bool(self._playback_service and self._playback_service.is_playing())

    def start(self, text: str, settings: PlaybackSettings) -> None:
        """Gera a composição a partir do texto e inicia a reprodução."""
        if self.is_playing():
            return

        composition = self._generator.generate(text, settings)
        player = self._player_factory()

        self._composition = composition
        self._playback_service = PlaybackService(player)
        self._playback_service.start(composition)

        seconds_per_beat = 60.0 / settings.bpm
        self._total_seconds = (
            composition.timeline[-1].absolute_beat * seconds_per_beat
            if composition.timeline
            else 0.0
        )
        self._elapsed_seconds = 0.0

    def pause(self) -> None:
        """Interrompe a reprodução em andamento, se houver uma."""
        if self._playback_service:
            self._playback_service.stop()

    def resume(self) -> None:
        """Reinicia a reprodução da composição atual desde o início (sem seek)."""
        if self._playback_service and self._composition:
            self._playback_service.start(self._composition)
            self._elapsed_seconds = 0.0

    def close(self) -> None:
        """Libera os recursos de áudio, interrompendo qualquer reprodução."""
        if self._playback_service:
            self._playback_service.close()

    def advance_progress(self, delta_seconds: float) -> float:
        """
        Avança o tempo decorrido em *delta_seconds* e retorna o percentual
        concluído (0 a 100). Não depende de nenhum timer concreto — quem
        chama decide a cadência (ex.: Tkinter `after`, um loop de teste, etc.).
        """
        self._elapsed_seconds += delta_seconds
        if self._total_seconds <= 0:
            return 0.0
        return min(self._elapsed_seconds / self._total_seconds * 100, 100)

    @property
    def elapsed_seconds(self) -> float:
        return self._elapsed_seconds
