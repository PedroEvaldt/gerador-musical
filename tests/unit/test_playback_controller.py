"""
Testes unitários do PlaybackController.

Estratégia:
    - O AudioPlayer real é substituído por um FakePlayer (mesmo padrão de
      test_playback_service.py), isolando os testes de qualquer
      dependência de áudio real.
    - O controlador recebe uma player_factory por injeção, confirmando
      que ele não conhece nenhuma implementação concreta de player
      (princípio da Inversão de Dependência) — basta trocar a fábrica
      para usar outro player, sem alterar PlaybackController.
"""

import threading

import pytest

from music_generator.domain.composition import MusicalComposition
from music_generator.domain.settings import PlaybackSettings
from music_generator.gui.playback_controller import PlaybackController
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


@pytest.fixture()
def fake_player() -> FakePlayer:
    return FakePlayer()


@pytest.fixture()
def controller(fake_player: FakePlayer) -> PlaybackController:
    return PlaybackController(player_factory=lambda: fake_player)


@pytest.fixture()
def settings() -> PlaybackSettings:
    return PlaybackSettings(bpm=120, initial_volume=80, default_octave=4, initial_instrument=0)


class TestStart:
    def test_start_inicia_reproducao_sem_bloquear(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E", settings)

        assert fake_player.started.wait(timeout=1.0)
        assert controller.is_playing()

        controller.pause()

    def test_start_chama_a_player_factory(
        self, settings: PlaybackSettings
    ) -> None:
        fake_player = FakePlayer()
        calls: list[int] = []

        def factory() -> FakePlayer:
            calls.append(1)
            return fake_player

        controller = PlaybackController(player_factory=factory)
        controller.start("C", settings)
        fake_player.started.wait(timeout=1.0)

        assert len(calls) == 1
        controller.pause()

    def test_start_ignorado_se_ja_esta_tocando(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E", settings)
        fake_player.started.wait(timeout=1.0)

        controller.start("F G H", settings)  # não deve levantar nem reiniciar

        assert fake_player.play_calls == 1
        controller.pause()

    def test_start_calcula_duracao_total_a_partir_da_timeline(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E F", settings)
        fake_player.started.wait(timeout=1.0)

        # 4 notas de 1 beat a 120 BPM = 0.5s por nota = 2.0s no total
        percentual = controller.advance_progress(0.0)
        assert percentual == 0.0  # nada decorrido ainda, mas não deve dar ZeroDivisionError

        controller.pause()

    def test_start_propaga_erro_do_gerador(self, settings: PlaybackSettings) -> None:
        controller = PlaybackController(player_factory=FakePlayer)

        with pytest.raises(ValueError):
            # BPM abaixo do mínimo aceito gera ValueError na geração
            invalid_settings = PlaybackSettings(
                bpm=1, initial_volume=80, default_octave=4, initial_instrument=0
            )
            controller.start("C D E", invalid_settings)


class TestPauseEResume:
    def test_pause_para_a_reproducao(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E", settings)
        fake_player.started.wait(timeout=1.0)

        controller.pause()

        assert not controller.is_playing()

    def test_pause_sem_reproducao_nao_levanta_excecao(
        self, controller: PlaybackController
    ) -> None:
        controller.pause()  # não deve levantar

    def test_resume_reinicia_a_composicao_atual(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E", settings)
        fake_player.started.wait(timeout=1.0)
        controller.pause()
        fake_player.started.clear()
        fake_player.stop_requested.clear()

        controller.resume()

        assert fake_player.started.wait(timeout=1.0)
        assert fake_player.play_calls == 2
        controller.pause()

    def test_resume_zera_o_tempo_decorrido(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E", settings)
        fake_player.started.wait(timeout=1.0)
        controller.advance_progress(1.0)
        controller.pause()
        fake_player.stop_requested.clear()

        controller.resume()

        assert controller.elapsed_seconds == 0.0
        controller.pause()

    def test_resume_sem_composicao_previa_nao_levanta_excecao(
        self, controller: PlaybackController
    ) -> None:
        controller.resume()  # não deve levantar


class TestProgresso:
    def test_advance_progress_sem_composicao_retorna_zero(
        self, controller: PlaybackController
    ) -> None:
        assert controller.advance_progress(1.0) == 0.0

    def test_advance_progress_acumula_tempo_decorrido(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E F", settings)
        fake_player.started.wait(timeout=1.0)

        controller.advance_progress(0.5)
        controller.advance_progress(0.5)

        assert controller.elapsed_seconds == 1.0
        controller.pause()

    def test_advance_progress_nao_ultrapassa_cem_por_cento(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C", settings)
        fake_player.started.wait(timeout=1.0)

        percentual = controller.advance_progress(1000.0)

        assert percentual == 100.0
        controller.pause()


class TestClose:
    def test_close_para_reproducao_e_libera_o_player(
        self, controller: PlaybackController, fake_player: FakePlayer, settings: PlaybackSettings
    ) -> None:
        controller.start("C D E", settings)
        fake_player.started.wait(timeout=1.0)

        controller.close()

        assert fake_player.closed

    def test_close_sem_reproducao_nao_levanta_excecao(
        self, controller: PlaybackController
    ) -> None:
        controller.close()  # não deve levantar
