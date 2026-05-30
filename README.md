# Gerador Musical

Implementacao do nucleo da Fase 1 de um gerador de sequencias musicais a partir de texto.

## Objetivo da Fase 1

O sistema recebe um texto e configuracoes musicais iniciais, percorre o texto caractere por caractere e gera uma composicao como uma sequencia ordenada de eventos musicais. Essa composicao pode ser reproduzida por um adaptador de audio baseado em FluidSynth.

## Arquitetura resumida

- `music_generator.domain`: configuracoes, estado musical, eventos e composicao.
- `music_generator.application`: regras de interpretacao, interpretador, gerador de sequencia e servico de playback.
- `music_generator.infrastructure.audio`: interface de player e adaptador concreto para FluidSynth.

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
