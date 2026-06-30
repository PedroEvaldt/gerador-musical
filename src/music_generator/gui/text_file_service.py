"""
Serviço de arquivos de texto.
Arquivo: src/music_generator/gui/text_file_service.py

Encapsula a leitura e escrita de arquivos .txt usados como entrada/saída
do campo de texto da interface. Não depende de Tkinter nem de nenhuma
biblioteca de interface gráfica — pode ser testado isoladamente.
"""

from pathlib import Path


class TextFileService:
    """Lê e escreve o conteúdo do campo de texto em arquivos .txt."""

    def read(self, file_path: str | Path) -> str:
        """Lê e retorna o conteúdo de um arquivo de texto em UTF-8."""
        return Path(file_path).read_text(encoding="utf-8")

    def write(self, file_path: str | Path, content: str) -> None:
        """Escreve *content* em *file_path*, sobrescrevendo o arquivo existente."""
        Path(file_path).write_text(content, encoding="utf-8")
