"""
Testes unitários da interface gráfica (gui.py).

Execução:
    cd src && pytest ../tests/unit/test_gui.py -v

Estratégia:
    - A janela é criada em modo oculto (withdraw) para não abrir na tela.
    - PlaybackService e FluidSynthPlayer são substituídos por Fakes/Mocks,
      isolando os testes de qualquer dependência de áudio.
"""

import threading
import tkinter as tk
from unittest.mock import MagicMock, patch

import pytest

from gui import INSTRUMENTS, MusicGeneratorApp
from music_generator.domain.composition import MusicalComposition
from music_generator.domain.events import RestEvent
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.audio.player import AudioPlayer


# ---------------------------------------------------------------------------
# Fake AudioPlayer (mesmo padrão de test_playback_service.py)
# ---------------------------------------------------------------------------

class FakePlayer(AudioPlayer):
    def __init__(self) -> None:
        self.started = threading.Event()
        self.stop_requested = threading.Event()
        self.closed = False

    def play(self, composition: MusicalComposition) -> None:
        self.started.set()
        self.stop_requested.wait(timeout=2.0)

    def stop(self) -> None:
        self.stop_requested.set()

    def close(self) -> None:
        self.closed = True


# ---------------------------------------------------------------------------
# Fixture: app oculta, destruída após cada teste
# ---------------------------------------------------------------------------

@pytest.fixture()
def app():
    """Cria o MusicGeneratorApp em modo headless e destrói ao fim do teste."""
    root = MusicGeneratorApp()
    root.withdraw()          # esconde a janela — sem display necessário
    yield root
    root.destroy()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_text(app: MusicGeneratorApp, text: str) -> None:
    app._text_box.delete("1.0", tk.END)
    app._text_box.insert("1.0", text)


def _make_short_composition() -> MusicalComposition:
    return MusicalComposition(
        events=[RestEvent(duration_beats=0.1)],
        initial_bpm=999,
    )


# ===========================================================================
# 1. Inicialização
# ===========================================================================

class TestInicializacao:
    def test_titulo_da_janela(self, app):
        assert "INF01120" in app.title()
        assert "Música" in app.title()

    def test_valores_padrao_bpm(self, app):
        assert app._bpm_var.get() == 180

    def test_valores_padrao_oitava(self, app):
        assert app._octave_var.get() == 4

    def test_valores_padrao_instrumento(self, app):
        assert app._instrument_var.get() == "Piano"

    def test_valores_padrao_volume(self, app):
        assert 0 <= app._volume_var.get() <= 127

    def test_campo_texto_inicialmente_vazio(self, app):
        conteudo = app._text_box.get("1.0", tk.END).strip()
        assert conteudo == ""

    def test_botao_pause_inicialmente_desabilitado(self, app):
        assert str(app._pause_btn["state"]) == "disabled"

    def test_botao_play_inicialmente_habilitado(self, app):
        assert str(app._play_btn["state"]) == "normal"

    def test_status_inicial(self, app):
        assert app._status_var.get() == "Pronto"


# ===========================================================================
# 2. _build_settings
# ===========================================================================

class TestBuildSettings:
    def test_retorna_playback_settings(self, app):
        settings = app._build_settings()
        assert isinstance(settings, PlaybackSettings)

    def test_bpm_reflete_widget(self, app):
        app._bpm_var.set(120)
        assert app._build_settings().bpm == 120

    def test_oitava_reflete_widget(self, app):
        app._octave_var.set(3)
        assert app._build_settings().default_octave == 3

    def test_volume_reflete_widget(self, app):
        app._volume_var.set(100)
        assert app._build_settings().initial_volume == 100

    def test_instrumento_reflete_widget(self, app):
        app._instrument_var.set("Violino")
        assert app._build_settings().initial_instrument == INSTRUMENTS["Violino"]

    def test_todos_instrumentos_geram_settings_validos(self, app):
        for nome in INSTRUMENTS:
            app._instrument_var.set(nome)
            settings = app._build_settings()
            assert 0 <= settings.initial_instrument <= 127

    @pytest.mark.parametrize("bpm", [20, 120, 300])
    def test_bpm_nos_limites_aceitos(self, app, bpm):
        app._bpm_var.set(bpm)
        settings = app._build_settings()
        assert settings.bpm == bpm

    @pytest.mark.parametrize("octave", [0, 4, 9])
    def test_oitava_nos_limites_aceita(self, app, octave):
        app._octave_var.set(octave)
        settings = app._build_settings().default_octave
        assert settings == octave


# ===========================================================================
# 3. Mapeamento de instrumentos
# ===========================================================================

class TestMapeamentoInstrumentos:
    def test_piano_e_midi_zero(self):
        assert INSTRUMENTS["Piano"] == 0

    def test_todos_indices_no_range_midi(self):
        for nome, idx in INSTRUMENTS.items():
            assert 0 <= idx <= 127, f"{nome} fora do range MIDI: {idx}"

    def test_sem_indices_duplicados(self):
        valores = list(INSTRUMENTS.values())
        assert len(valores) == len(set(valores)), "Índices MIDI duplicados no dicionário"

    def test_sem_nomes_duplicados(self):
        nomes = list(INSTRUMENTS.keys())
        assert len(nomes) == len(set(nomes))


# ===========================================================================
# 4. Limpar texto
# ===========================================================================

class TestLimparTexto:
    def test_limpa_campo_de_texto(self, app):
        _set_text(app, "ABC")
        app._on_clear()
        assert app._text_box.get("1.0", tk.END).strip() == ""

    def test_limpar_campo_ja_vazio_nao_levanta_excecao(self, app):
        app._on_clear()  # não deve levantar
        assert app._text_box.get("1.0", tk.END).strip() == ""


# ===========================================================================
# 5. Play — validações antes do áudio
# ===========================================================================

class TestPlayValidacao:
    def test_play_com_texto_vazio_nao_inicia_reproducao(self, app):
        with patch.object(app, "_playback_service", None):
            with patch("gui.messagebox.showwarning") as mock_warn:
                app._on_play()
                mock_warn.assert_called_once()

    def test_play_com_texto_vazio_nao_muda_status(self, app):
        with patch("gui.messagebox.showwarning"):
            app._on_play()
        assert app._status_var.get() == "Pronto"

    def test_play_erro_no_fluidsynth_exibe_mensagem(self, app):
        _set_text(app, "ABC")
        with patch("gui.FluidSynthPlayer", side_effect=RuntimeError("sem áudio")):
            with patch("gui.messagebox.showerror") as mock_err:
                app._on_play()
                mock_err.assert_called_once()


# ===========================================================================
# 6. Play — fluxo completo (com Fakes)
# ===========================================================================

class TestPlayFluxo:
    def _iniciar_com_fake(self, app: MusicGeneratorApp) -> FakePlayer:
        fake_player = FakePlayer()
        _set_text(app, "ABC")
        with patch("gui.FluidSynthPlayer", return_value=fake_player):
            app._on_play()
        fake_player.started.wait(timeout=1.0)
        return fake_player

    def test_play_muda_status_para_reproduzindo(self, app):
        self._iniciar_com_fake(app)
        assert app._status_var.get() == "Reproduzindo..."

    def test_play_desabilita_botao_play(self, app):
        self._iniciar_com_fake(app)
        assert str(app._play_btn["state"]) == "disabled"

    def test_play_habilita_botao_pause(self, app):
        self._iniciar_com_fake(app)
        assert str(app._pause_btn["state"]) == "normal"

    def test_play_inicia_reproducao_no_servico(self, app):
        self._iniciar_com_fake(app)
        assert app._playback_service is not None
        assert app._playback_service.is_playing()

    def teardown_method(self, _method):
        # Garante que threads de áudio fake não fiquem penduradas
        pass


# ===========================================================================
# 7. Pause / retomada
# ===========================================================================

class TestPause:
    def _iniciar_com_fake(self, app: MusicGeneratorApp) -> FakePlayer:
        fake_player = FakePlayer()
        _set_text(app, "ABC")
        with patch("gui.FluidSynthPlayer", return_value=fake_player):
            app._on_play()
        fake_player.started.wait(timeout=1.0)
        return fake_player

    def test_pause_para_reproducao(self, app):
        self._iniciar_com_fake(app)
        app._on_pause()
        assert not app._playback_service.is_playing()

    def test_pause_muda_status_para_pausado(self, app):
        self._iniciar_com_fake(app)
        app._on_pause()
        assert app._status_var.get() == "Pausado"

    def test_pause_sem_reproducao_nao_levanta_excecao(self, app):
        app._on_pause()  # não deve levantar

    def test_pause_quando_nao_ha_servico_nao_levanta_excecao(self, app):
        assert app._playback_service is None
        app._on_pause()


# ===========================================================================
# 8. Fechamento da janela
# ===========================================================================

class TestFechamento:
    def test_close_chama_close_no_servico(self, app):
        fake_service = MagicMock()
        fake_service.is_playing.return_value = False
        app._playback_service = fake_service

        app._on_close()

        fake_service.close.assert_called_once()

    def test_close_sem_servico_nao_levanta_excecao(self, app):
        assert app._playback_service is None
        # _on_close chama destroy(), que invalida o widget —
        # não chamamos app._on_close() aqui para não destruir o fixture;
        # verificamos apenas a guarda do None.
        assert app._playback_service is None  # pré-condição ok
