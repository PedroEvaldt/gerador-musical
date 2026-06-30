# Gerador Musical

Implementacao do nucleo da Fase 1 e do nucleo polifonico da Fase 2 de um
gerador de sequencias musicais a partir de texto.

## Objetivo da Fase 1

O sistema recebe um texto e configuracoes musicais iniciais, percorre o texto caractere por caractere e gera uma composicao como uma sequencia ordenada de eventos musicais. Essa composicao pode ser reproduzida por um adaptador de audio baseado em FluidSynth.

## Arquitetura resumida

- `music_generator.domain`: configuracoes, estado musical, eventos e composicao.
- `music_generator.application`: regras de interpretacao, interpretador, gerador de sequencia e servico de playback.
- `music_generator.infrastructure.audio`: interface de player e adaptador concreto para FluidSynth.
- `gui.py`: interface grafica Tkinter. Coleta texto e configuracoes, delega geracao e reproducao ao nucleo.


A interpretacao do texto nao importa FluidSynth e nao depende de interface grafica. O player recebe uma `MusicalComposition` ja gerada.

## Ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

## Instalacao

Dependencias de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
```

Dependencia opcional de audio:

```bash
python -m pip install -e ".[audio]"
```

FluidSynth tambem exige a biblioteca nativa instalada no sistema. O projeto nao baixa SoundFonts automaticamente e nao inclui arquivos `.sf2` no repositorio.

## SoundFont

Informe o caminho do arquivo `.sf2` com a variavel de ambiente:

```bash
export SOUNDFONT_PATH=/caminho/para/arquivo.sf2
```

Tambem e possivel passar o caminho diretamente para `FluidSynthPlayer(soundfont_path="...")`.

## Executar a interface grafica

```bash
cd src
python gui.py
```

A janela permite inserir texto, ajustar BPM, oitava, volume e instrumento inicial, e controlar a reproducao com os botoes play e pause.

## Executar testes

Testes unitarios:

```bash
pytest tests/unit
```

Todos os testes que nao forem pulados automaticamente:

```bash
pytest
```

Teste de integracao opcional com FluidSynth:

```bash
pytest tests/integration --run-integration
```

Esse teste so executa quando `SOUNDFONT_PATH`, `pyfluidsynth` e a biblioteca nativa FluidSynth estiverem disponiveis.

## Integracao com interface grafica

A interface deve criar `PlaybackSettings`, gerar a composicao com `SequenceGenerator` e controlar a reproducao com `PlaybackService`.

```python
from music_generator.application.playback_service import PlaybackService
from music_generator.application.sequence_generator import SequenceGenerator
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer

settings = PlaybackSettings(
    bpm=120,
    initial_volume=80,
    default_octave=4,
    initial_instrument=0,
)

composition = SequenceGenerator().generate("ABC", settings)
player = FluidSynthPlayer()
playback_service = PlaybackService(player)

playback_service.start(composition)
```

Use `playback_service.stop()` para interromper, `playback_service.is_playing()` para consultar o estado e `playback_service.close()` para liberar recursos.

## Fora do escopo da Fase 1

- Interface grafica.
- Abertura ou salvamento de arquivos TXT.
- Exportacao MIDI.
- Multiplas vozes.
- Atrasos com `[n]`.
- Alteracoes de BPM com `>` ou `<`.
- Funcionalidades da Fase 2.

## Nucleo da Fase 2

A Fase 2 foi adicionada sem substituir a API da Fase 1. Use
`PolyphonicSequenceGenerator` para interpretar cada linha como uma voz
independente:

```python
from music_generator.application.playback_service import PlaybackService
from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer

text = "CDE\n[4] > MbG"

composition = PolyphonicSequenceGenerator().generate(text)

player = FluidSynthPlayer()
playback_service = PlaybackService(player)
playback_service.start(composition)
```

Caracteristicas implementadas:

- vozes `V0`, `V1`, `V2`, ... por linha, preservando linhas vazias internas;
- ciclo inicial de oitava, volume e instrumento a cada quatro vozes;
- atraso inicial `[n]` por voz;
- token `Mb` para Mi bemol;
- estado local independente de volume, instrumento e oitava;
- comandos globais de BPM com `>` e `<`;
- timeline deterministica com beat absoluto, voz e ordem de origem;
- reproducao polifonica com canais MIDI melodicos distintos, reservando o canal 9.

## Exportacao MIDI

A composicao polifonica pode ser exportada para um arquivo `.mid` com
`MidiExporter`, sem depender de FluidSynth ou de qualquer biblioteca de audio:

```python
from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.infrastructure.midi.midi_exporter import MidiExporter

composition = PolyphonicSequenceGenerator().generate("CDE\n[4] > MbG")

MidiExporter().export(composition, "saida.mid")
```

Caracteristicas do exportador:

- uma faixa MIDI por voz, mais uma faixa global de tempo (`set_tempo`);
- cada voz usa um canal MIDI melodico distinto (`MELODIC_CHANNELS`), reservando o canal 9 para percussao, igual ao `FluidSynthPlayer`;
- `program_change` por voz refletindo o instrumento inicial de cada uma;
- mudancas de BPM (`>` e `<`) geram novas mensagens `set_tempo` na faixa de tempo;
- resolucao de 480 ticks por semínima (`MidiExporter.TICKS_PER_BEAT`).

## Interface grafica (Fase 2)

A interface (`gui.py`) ja consome o nucleo polifonico da Fase 2 e oferece:

- importar texto de um arquivo `.txt` e editar no campo de texto;
- salvar o conteudo do campo de texto em `.txt`, com escolha de nome e diretorio;
- exportar a composicao atual para `.mid`, com escolha de nome e diretorio;
- selecionar o instrumento inicial entre os 128 instrumentos do padrao General MIDI;
- ajustar BPM, oitava padrao e volume inicial antes de reproduzir ou exportar.
