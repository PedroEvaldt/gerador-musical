"""
Testes unitários do MidiExportService.

Estratégia:
    - Usa um gerador e um exportador reais por padrão, validando a
      integração ponta a ponta (texto -> composição -> arquivo .mid).
    - Também testa com dublês injetados, confirmando que o serviço
      apenas orquestra as chamadas (princípio da Responsabilidade
      Única) e depende de abstrações substituíveis (Inversão de
      Dependência), sem hardcode de implementações concretas.
"""

from pathlib import Path
from unittest.mock import MagicMock

import mido
import pytest

from music_generator.domain.settings import PlaybackSettings
from music_generator.gui.midi_export_service import MidiExportService


@pytest.fixture()
def settings() -> PlaybackSettings:
    return PlaybackSettings(bpm=120, initial_volume=80, default_octave=4, initial_instrument=0)


class TestExportacaoReal:
    def test_export_gera_arquivo_midi_valido(
        self, tmp_path: Path, settings: PlaybackSettings
    ) -> None:
        output_path = tmp_path / "saida.mid"

        MidiExportService().export("C D E F", settings, output_path)

        assert output_path.exists()
        midi_file = mido.MidiFile(str(output_path))
        assert len(midi_file.tracks) >= 2  # faixa de tempo + ao menos uma voz

    def test_export_com_multiplas_vozes(self, tmp_path: Path, settings: PlaybackSettings) -> None:
        output_path = tmp_path / "fuga.mid"

        MidiExportService().export("[0] C D E\n[4] G A H", settings, output_path)

        midi_file = mido.MidiFile(str(output_path))
        assert len(midi_file.tracks) == 3  # tempo + V0 + V1

    def test_export_aceita_caminho_como_string(
        self, tmp_path: Path, settings: PlaybackSettings
    ) -> None:
        output_path = str(tmp_path / "saida_str.mid")

        MidiExportService().export("C D E", settings, output_path)

        assert Path(output_path).exists()


class TestOrquestracaoComDubles:
    def test_chama_generate_com_texto_e_settings_recebidos(
        self, settings: PlaybackSettings, tmp_path: Path
    ) -> None:
        fake_generator = MagicMock()
        fake_exporter = MagicMock()
        service = MidiExportService(generator=fake_generator, exporter=fake_exporter)

        service.export("ABC", settings, tmp_path / "saida.mid")

        fake_generator.generate.assert_called_once_with("ABC", settings)

    def test_chama_export_com_a_composicao_gerada_e_o_caminho_informado(
        self, settings: PlaybackSettings, tmp_path: Path
    ) -> None:
        fake_generator = MagicMock()
        fake_composition = MagicMock()
        fake_generator.generate.return_value = fake_composition
        fake_exporter = MagicMock()
        output_path = tmp_path / "saida.mid"

        service = MidiExportService(generator=fake_generator, exporter=fake_exporter)
        service.export("ABC", settings, output_path)

        fake_exporter.export.assert_called_once_with(fake_composition, output_path)

    def test_erro_no_generator_se_propaga(self, settings: PlaybackSettings, tmp_path: Path) -> None:
        fake_generator = MagicMock()
        fake_generator.generate.side_effect = ValueError("texto inválido")
        service = MidiExportService(generator=fake_generator, exporter=MagicMock())

        with pytest.raises(ValueError, match="texto inválido"):
            service.export("ABC", settings, tmp_path / "saida.mid")

    def test_erro_no_exporter_se_propaga(self, settings: PlaybackSettings, tmp_path: Path) -> None:
        fake_exporter = MagicMock()
        fake_exporter.export.side_effect = OSError("disco cheio")
        service = MidiExportService(generator=MagicMock(), exporter=fake_exporter)

        with pytest.raises(OSError, match="disco cheio"):
            service.export("ABC", settings, tmp_path / "saida.mid")
