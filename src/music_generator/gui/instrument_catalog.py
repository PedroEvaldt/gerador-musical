"""
Catálogo de instrumentos General MIDI.
Arquivo: src/music_generator/gui/instrument_catalog.py

Isola a lista de instrumentos (nome legível -> número de programa GM)
atrás de uma interface pequena, para que a GUI dependa apenas do
contrato `InstrumentCatalog` e não de um dicionário global concreto.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence


class InstrumentCatalog(ABC):
    """Fonte de instrumentos disponíveis para seleção na interface."""

    @abstractmethod
    def names(self) -> Sequence[str]:
        """Retorna os nomes legíveis dos instrumentos, em ordem de exibição."""
        raise NotImplementedError

    @abstractmethod
    def default_name(self) -> str:
        """Retorna o nome do instrumento selecionado por padrão."""
        raise NotImplementedError

    @abstractmethod
    def midi_program(self, name: str) -> int:
        """Converte um nome legível no número de programa General MIDI (0-127)."""
        raise NotImplementedError


class InMemoryInstrumentCatalog(InstrumentCatalog):
    """Catálogo fixo com os 128 instrumentos do padrão General MIDI."""

    # Mapeamento de nome legível → índice MIDI General MIDI
    _INSTRUMENTS: dict[str, int] = {
        # Pianos (0–7)
        "Piano Acústico (Grand)": 0,
        "Piano Acústico (Bright)": 1,
        "Piano Elétrico Grande": 2,
        "Honky-Tonk Piano": 3,
        "Piano Elétrico 1 (Rhodes)": 4,
        "Piano Elétrico 2 (Chorus)": 5,
        "Cravo": 6,
        "Clavicórdio": 7,
        # Instrumentos de Teclas Cromáticas (8–15)
        "Celesta": 8,
        "Glockenspiel": 9,
        "Caixinha de Música": 10,
        "Vibrafone": 11,
        "Marimba": 12,
        "Xilofone": 13,
        "Sinos Tubulares": 14,
        "Dulcimer": 15,
        # Órgãos (16–23)
        "Órgão Hammond": 16,
        "Órgão Percussivo": 17,
        "Órgão de Rock": 18,
        "Órgão de Igreja": 19,
        "Órgão de Reed": 20,
        "Acordeão": 21,
        "Harmônica": 22,
        "Bandoneón": 23,
        # Guitarras (24–31)
        "Violão (Nylon)": 24,
        "Violão (Aço)": 25,
        "Guitarra Jazz": 26,
        "Guitarra Limpa": 27,
        "Guitarra Muted": 28,
        "Guitarra Overdrive": 29,
        "Guitarra Distorção": 30,
        "Guitarra Harmonics": 31,
        # Baixos (32–39)
        "Contrabaixo Acústico": 32,
        "Baixo Elétrico (Dedos)": 33,
        "Baixo Elétrico (Palheta)": 34,
        "Baixo Fretless": 35,
        "Baixo Slap 1": 36,
        "Baixo Slap 2": 37,
        "Baixo Synth 1": 38,
        "Baixo Synth 2": 39,
        # Cordas (40–47)
        "Violino": 40,
        "Viola": 41,
        "Violoncelo": 42,
        "Contrabaixo": 43,
        "Cordas Tremolo": 44,
        "Cordas Pizzicato": 45,
        "Harpa Orquestral": 46,
        "Tímpano": 47,
        # Ensemble de Cordas (48–55)
        "Ensemble de Cordas 1": 48,
        "Ensemble de Cordas 2": 49,
        "Cordas Synth 1": 50,
        "Cordas Synth 2": 51,
        "Coro Ahh": 52,
        "Voz Ooh": 53,
        "Voz Synth": 54,
        "Hit Orquestral": 55,
        # Metais (56–63)
        "Trompete": 56,
        "Trombone": 57,
        "Tuba": 58,
        "Trompete Muted": 59,
        "Trompa Francesa": 60,
        "Seção de Metais": 61,
        "Trompete Synth": 62,
        "Trombone Synth": 63,
        # Reed (64–71)
        "Soprano Sax": 64,
        "Alto Sax": 65,
        "Tenor Sax": 66,
        "Barítono Sax": 67,
        "Oboé": 68,
        "Corne Inglês": 69,
        "Fagote": 70,
        "Clarinete": 71,
        # Palhetas / Flautas (72–79)
        "Piccolo": 72,
        "Flauta": 73,
        "Recorder": 74,
        "Flauta Pan": 75,
        "Garrafa Soprada": 76,
        "Shakuhachi": 77,
        "Assobio": 78,
        "Ocarina": 79,
        # Synth Lead (80–87)
        "Lead Quadrado": 80,
        "Lead Serrilhado": 81,
        "Lead Calliope": 82,
        "Lead Chiff": 83,
        "Lead Charang": 84,
        "Lead Voz": 85,
        "Lead Fifths": 86,
        "Lead Bass + Lead": 87,
        # Synth Pad (88–95)
        "Pad New Age": 88,
        "Pad Warm": 89,
        "Pad Polysynth": 90,
        "Pad Choir": 91,
        "Pad Bowed": 92,
        "Pad Metallic": 93,
        "Pad Halo": 94,
        "Pad Sweep": 95,
        # Synth FX (96–103)
        "FX Rain": 96,
        "FX Soundtrack": 97,
        "FX Crystal": 98,
        "FX Atmosphere": 99,
        "FX Brightness": 100,
        "FX Goblins": 101,
        "FX Echoes": 102,
        "FX Sci-Fi": 103,
        # Étnico (104–111)
        "Sitar": 104,
        "Banjo": 105,
        "Shamisen": 106,
        "Koto": 107,
        "Kalimba": 108,
        "Gaita de Foles": 109,
        "Fiddle": 110,
        "Shanai": 111,
        # Percussivo (112–119)
        "Sino Tinkle": 112,
        "Agogô": 113,
        "Steel Drum": 114,
        "Woodblock": 115,
        "Taiko Drum": 116,
        "Tom Melódico": 117,
        "Bombo Synth": 118,
        "Prato Synth": 119,
        # Efeitos Sonoros (120–127)
        "Guitarra Fret Noise": 120,
        "Breath Noise": 121,
        "Litoral": 122,
        "Pássaros": 123,
        "Telefone": 124,
        "Helicóptero": 125,
        "Aplausos": 126,
        "Tiro de Pistola": 127,
    }

    def names(self) -> Sequence[str]:
        return list(self._INSTRUMENTS.keys())

    def default_name(self) -> str:
        return next(iter(self._INSTRUMENTS))

    def midi_program(self, name: str) -> int:
        try:
            return self._INSTRUMENTS[name]
        except KeyError as exc:
            raise ValueError(f"Instrumento desconhecido: {name!r}") from exc
