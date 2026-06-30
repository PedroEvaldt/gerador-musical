"""
Exportador MIDI — converte PolyphonicComposition em arquivo .mid.
Arquivo: src/music_generator/infrastructure/midi/midi_exporter.py
"""

from pathlib import Path

import mido

from music_generator.domain.events import BpmChangeEvent, NoteEndEvent, NoteStartEvent
from music_generator.domain.polyphony import MELODIC_CHANNELS, PolyphonicComposition


class MidiExporter:
    """Exporta uma PolyphonicComposition para um arquivo .mid usando mido."""

    # Resolução padrão: 480 ticks por semínima (quarter note)
    TICKS_PER_BEAT: int = 480

    def export(self, composition: PolyphonicComposition, output_path: str | Path) -> None:
        """
        Gera um arquivo MIDI a partir da composição e grava em *output_path*.

        A lógica espelha o FluidSynthPlayer:
        - Cada voz ocupa um canal MIDI distinto (MELODIC_CHANNELS).
        - Mudanças de BPM viram mensagens de tempo (set_tempo).
        - Note-on / note-off são colocados na faixa da voz correspondente.
        """
        mid = mido.MidiFile(ticks_per_beat=self.TICKS_PER_BEAT)

        # Uma faixa de tempo global para mensagens de set_tempo
        tempo_track = mido.MidiTrack()
        mid.tracks.append(tempo_track)

        current_bpm = composition.initial_bpm
        tempo_track.append(
            mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(current_bpm), time=0)
        )

        # Uma faixa por voz
        num_voices = len(composition.voices)
        voice_tracks: list[mido.MidiTrack] = []
        for voice in composition.voices:
            track = mido.MidiTrack()
            mid.tracks.append(track)
            voice_tracks.append(track)

            # Configura o instrumento inicial da voz (program_change)
            channel = MELODIC_CHANNELS[voice.voice_index % len(MELODIC_CHANNELS)]
            track.append(
                mido.Message(
                    "program_change",
                    channel=channel,
                    program=voice.settings.initial_instrument,
                    time=0,
                )
            )

        # Acumula mensagens por voz como (absolute_tick, mido.Message)
        # para depois calcular delta-times dentro de cada faixa.
        voice_messages: list[list[tuple[int, mido.Message]]] = [
            [] for _ in range(num_voices)
        ]

        # Converte absolute_beat → absolute_tick usando BPM acumulado.
        # Como o MIDI usa ticks absolutos e mido espera delta-times,
        # precisamos converter sabendo que o BPM pode mudar ao longo da
        # timeline. Aqui fazemos uma passagem linear acumulando o tick.
        beat_to_tick_ratio = float(self.TICKS_PER_BEAT)  # ticks / beat (inicial)

        for scheduled in composition.timeline:
            absolute_tick = int(scheduled.absolute_beat * beat_to_tick_ratio)
            event = scheduled.event

            if isinstance(event, BpmChangeEvent):
                # Mensagem de tempo vai para a faixa 0 (tempo_track)
                tempo_track.append(
                    mido.MetaMessage(
                        "set_tempo",
                        tempo=mido.bpm2tempo(event.bpm),
                        time=absolute_tick,  # será convertido para delta abaixo
                    )
                )
                continue

            voice_idx = scheduled.voice_index
            if voice_idx >= num_voices:
                continue

            channel = MELODIC_CHANNELS[voice_idx % len(MELODIC_CHANNELS)]

            if isinstance(event, NoteStartEvent):
                note = event.note
                voice_messages[voice_idx].append(
                    (
                        absolute_tick,
                        mido.Message(
                            "note_on",
                            channel=channel,
                            note=note.midi_number,
                            velocity=note.volume,
                            time=0,  # delta calculado depois
                        ),
                    )
                )

            elif isinstance(event, NoteEndEvent):
                note = event.note
                voice_messages[voice_idx].append(
                    (
                        absolute_tick,
                        mido.Message(
                            "note_off",
                            channel=channel,
                            note=note.midi_number,
                            velocity=0,
                            time=0,  # delta calculado depois
                        ),
                    )
                )

        # Converte absolute_tick → delta_time e adiciona às faixas
        self._flush_absolute_to_delta(tempo_track)
        for voice_idx, messages in enumerate(voice_messages):
            track = voice_tracks[voice_idx]
            prev_tick = 0
            for abs_tick, msg in sorted(messages, key=lambda x: x[0]):
                delta = abs_tick - prev_tick
                track.append(msg.copy(time=delta))
                prev_tick = abs_tick
            track.append(mido.MetaMessage("end_of_track", time=0))

        mid.save(str(output_path))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _flush_absolute_to_delta(self, track: mido.MidiTrack) -> None:
        """
        Converte a faixa de tempo: os MetaMessages foram adicionados com
        o campo *time* contendo o tick absoluto; aqui transformamos em deltas.
        """
        prev = 0
        for msg in track:
            abs_tick = msg.time
            msg.time = abs_tick - prev
            prev = abs_tick
        track.append(mido.MetaMessage("end_of_track", time=0))
