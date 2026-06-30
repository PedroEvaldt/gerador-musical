"""
Testes unitários do MidiExporter.

Estratégia:
    - Gera composições reais via PolyphonicSequenceGenerator (mesmo padrão
      usado em test_polyphonic_generator.py) e exporta para um arquivo .mid
      temporário, depois inspeciona o resultado com mido.
"""

from pathlib import Path

import mido
import pytest

from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.domain.polyphony import MELODIC_CHANNELS
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.midi.midi_exporter import MidiExporter


def generate(text: str, settings: PlaybackSettings | None = None):
    return PolyphonicSequenceGenerator().generate(text, settings)


def export_to_tmp(composition, tmp_path: Path, filename: str = "saida.mid") -> Path:
    output_path = tmp_path / filename
    MidiExporter().export(composition, output_path)
    return output_path


# ===========================================================================
# 1. Geração de arquivo
# ===========================================================================


class TestArquivoGerado:
    def test_export_cria_arquivo_no_caminho_informado(self, tmp_path: Path) -> None:
        composition = generate("C D E")
        output_path = export_to_tmp(composition, tmp_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_aceita_caminho_como_string(self, tmp_path: Path) -> None:
        composition = generate("C D E")
        output_path = str(tmp_path / "saida_str.mid")

        MidiExporter().export(composition, output_path)

        assert Path(output_path).exists()

    def test_arquivo_gerado_e_um_midi_valido(self, tmp_path: Path) -> None:
        composition = generate("C D E")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))

        assert midi_file.ticks_per_beat == MidiExporter.TICKS_PER_BEAT


# ===========================================================================
# 2. Estrutura de faixas (tracks)
# ===========================================================================


class TestEstruturaDeFaixas:
    def test_uma_faixa_de_tempo_mais_uma_por_voz(self, tmp_path: Path) -> None:
        composition = generate("C D E\nF G H")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))

        # Faixa 0 é a faixa de tempo global; uma faixa por voz depois dela.
        assert len(midi_file.tracks) == 1 + len(composition.voices)

    def test_faixa_de_tempo_contem_set_tempo_inicial(self, tmp_path: Path) -> None:
        settings = PlaybackSettings(
            bpm=140, initial_volume=80, default_octave=4, initial_instrument=0
        )
        composition = generate("C D E", settings)
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        tempo_track = midi_file.tracks[0]

        set_tempo_msgs = [msg for msg in tempo_track if msg.type == "set_tempo"]
        assert len(set_tempo_msgs) >= 1
        assert set_tempo_msgs[0].tempo == mido.bpm2tempo(140)

    def test_cada_faixa_termina_com_end_of_track(self, tmp_path: Path) -> None:
        composition = generate("C D E\nF G H")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))

        for track in midi_file.tracks:
            assert track[-1].type == "end_of_track"


# ===========================================================================
# 3. Canais e instrumentos por voz
# ===========================================================================


class TestCanaisEInstrumentos:
    def test_cada_voz_usa_um_canal_melodico_distinto(self, tmp_path: Path) -> None:
        composition = generate("C D E\nF G H\nA H C")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        voice_tracks = midi_file.tracks[1:]

        canais_usados = []
        for track in voice_tracks:
            note_on_msgs = [msg for msg in track if msg.type == "note_on"]
            canais_usados.append(note_on_msgs[0].channel)

        assert canais_usados == [
            MELODIC_CHANNELS[voice.voice_index % len(MELODIC_CHANNELS)]
            for voice in composition.voices
        ]
        assert len(set(canais_usados)) == len(canais_usados)

    def test_program_change_reflete_instrumento_inicial_da_voz(
        self, tmp_path: Path
    ) -> None:
        composition = generate("C D E\nF G H")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        voice_tracks = midi_file.tracks[1:]

        for voice, track in zip(composition.voices, voice_tracks):
            program_change_msgs = [
                msg for msg in track if msg.type == "program_change"
            ]
            assert len(program_change_msgs) == 1
            assert program_change_msgs[0].program == voice.settings.initial_instrument

    def test_canal_9_de_percussao_nunca_e_usado(self, tmp_path: Path) -> None:
        # MELODIC_CHANNELS já exclui o canal 9; aqui validamos que o
        # arquivo exportado de fato respeita essa reserva.
        text = "\n".join(["C D E"] * 15)  # usa o máximo de vozes permitido
        composition = generate(text)
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))

        for track in midi_file.tracks[1:]:
            for msg in track:
                if msg.type in ("note_on", "note_off", "program_change"):
                    assert msg.channel != 9


# ===========================================================================
# 4. Notas e temporização
# ===========================================================================


class TestNotasETemporizacao:
    def test_quantidade_de_note_on_e_note_off_e_igual(self, tmp_path: Path) -> None:
        composition = generate("C D E F")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        track = midi_file.tracks[1]

        note_on_count = sum(1 for msg in track if msg.type == "note_on")
        note_off_count = sum(1 for msg in track if msg.type == "note_off")

        assert note_on_count == note_off_count == 4

    def test_numero_midi_e_velocidade_da_nota_sao_preservados(
        self, tmp_path: Path
    ) -> None:
        settings = PlaybackSettings(
            bpm=120, initial_volume=100, default_octave=4, initial_instrument=0
        )
        composition = generate("C", settings)
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        track = midi_file.tracks[1]
        note_on = next(msg for msg in track if msg.type == "note_on")

        expected_note = composition.voices[0].events[0]
        assert note_on.note == expected_note.midi_number
        assert note_on.velocity == expected_note.volume

    def test_atraso_inicial_da_voz_desloca_o_primeiro_note_on(
        self, tmp_path: Path
    ) -> None:
        composition = generate("C\n[4] D")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        track_v1 = midi_file.tracks[2]

        # Soma dos deltas até o primeiro note_on equivale ao atraso em ticks.
        ticks_acumulados = 0
        for msg in track_v1:
            ticks_acumulados += msg.time
            if msg.type == "note_on":
                break

        assert ticks_acumulados == 4 * MidiExporter.TICKS_PER_BEAT

    def test_mudanca_de_bpm_gera_set_tempo_na_faixa_de_tempo(
        self, tmp_path: Path
    ) -> None:
        composition = generate("[0] > C D E F")
        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        tempo_track = midi_file.tracks[0]

        set_tempo_msgs = [msg for msg in tempo_track if msg.type == "set_tempo"]
        # Tempo inicial + ao menos uma mudança causada por '>'.
        assert len(set_tempo_msgs) >= 2


# ===========================================================================
# 5. Casos com múltiplas vozes (fuga)
# ===========================================================================


class TestComposicaoPolifonica:
    def test_exporta_composicao_com_tres_vozes_sem_erro(self, tmp_path: Path) -> None:
        texto_fuga = "[0] C D Eb F G\n[6] G A H C D\n[12] Eb F G Ab H"
        composition = generate(texto_fuga)

        output_path = export_to_tmp(composition, tmp_path)

        midi_file = mido.MidiFile(str(output_path))
        assert len(midi_file.tracks) == 1 + len(composition.voices) == 4

    def test_evento_sem_voz_correspondente_e_ignorado_sem_erro(
        self, tmp_path: Path
    ) -> None:
        # Composição com uma única voz não deve gerar erro mesmo que a
        # timeline contenha eventos de BPM globais (voice_index igual ao
        # da única voz existente).
        composition = generate("[0] > C D")

        output_path = export_to_tmp(composition, tmp_path)

        assert output_path.exists()
