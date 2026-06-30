"""
Serviço de exportação MIDI.
Arquivo: src/music_generator/gui/midi_export_service.py

Orquestra a geração da composição polifônica a partir do texto e a
exportação para um arquivo .mid, sem depender de Tkinter. Recebe o
gerador de sequência e o exportador MIDI por injeção de dependência,
o que permite substituí-los por dublês de teste ou implementações
alternativas sem alterar este serviço (princípio Aberto/Fechado).
"""

from pathlib import Path

from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.midi.midi_exporter import MidiExporter


class MidiExportService:
    """Gera a composição a partir do texto e a exporta para um arquivo MIDI."""

    def __init__(
        self,
        generator: PolyphonicSequenceGenerator | None = None,
        exporter: MidiExporter | None = None,
    ) -> None:
        self._generator = generator or PolyphonicSequenceGenerator()
        self._exporter = exporter or MidiExporter()

    def export(
        self,
        text: str,
        settings: PlaybackSettings,
        output_path: str | Path,
    ) -> None:
        """Gera a composição a partir de *text* e *settings* e salva em *output_path*."""
        composition = self._generator.generate(text, settings)
        self._exporter.export(composition, output_path)
