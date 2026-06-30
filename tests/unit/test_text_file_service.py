"""
Testes unitários do TextFileService.
"""

from pathlib import Path

import pytest

from music_generator.gui.text_file_service import TextFileService


@pytest.fixture()
def service() -> TextFileService:
    return TextFileService()


class TestLeitura:
    def test_le_conteudo_de_arquivo_existente(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = tmp_path / "entrada.txt"
        arquivo.write_text("C D E F", encoding="utf-8")

        assert service.read(arquivo) == "C D E F"

    def test_le_aceitando_caminho_como_string(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = tmp_path / "entrada.txt"
        arquivo.write_text("G A H", encoding="utf-8")

        assert service.read(str(arquivo)) == "G A H"

    def test_le_preserva_quebras_de_linha(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = tmp_path / "fuga.txt"
        arquivo.write_text("C D E\nF G H", encoding="utf-8")

        assert service.read(arquivo) == "C D E\nF G H"

    def test_le_arquivo_inexistente_levanta_excecao(self, service: TextFileService, tmp_path: Path) -> None:
        with pytest.raises(OSError):
            service.read(tmp_path / "nao_existe.txt")


class TestEscrita:
    def test_escreve_conteudo_em_arquivo_novo(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = tmp_path / "saida.txt"

        service.write(arquivo, "A B C")

        assert arquivo.read_text(encoding="utf-8") == "A B C"

    def test_escreve_sobrescreve_arquivo_existente(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = tmp_path / "saida.txt"
        arquivo.write_text("conteúdo antigo", encoding="utf-8")

        service.write(arquivo, "conteúdo novo")

        assert arquivo.read_text(encoding="utf-8") == "conteúdo novo"

    def test_escreve_aceitando_caminho_como_string(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = str(tmp_path / "saida.txt")

        service.write(arquivo, "texto")

        assert Path(arquivo).read_text(encoding="utf-8") == "texto"

    def test_ida_e_volta_preserva_conteudo(self, service: TextFileService, tmp_path: Path) -> None:
        arquivo = tmp_path / "roundtrip.txt"
        texto_original = "[0] C D Eb F\n[4] > G A H"

        service.write(arquivo, texto_original)

        assert service.read(arquivo) == texto_original
