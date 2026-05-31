# Contrato de Integracao com a Interface

O nucleo da Fase 1 expoe uma API simples para a futura interface grafica. A interface deve coletar texto e configuracoes, chamar o gerador de sequencia e controlar a reproducao por meio do servico de playback.

```python
from music_generator.application.playback_service import PlaybackService
from music_generator.application.sequence_generator import SequenceGenerator
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer

text = "ABC"

settings = PlaybackSettings(
    bpm=120,
    initial_volume=80,
    default_octave=4,
    initial_instrument=0,
)

composition = SequenceGenerator().generate(text, settings)

player = FluidSynthPlayer()
playback_service = PlaybackService(player)
playback_service.start(composition)
```

## Controle de reproducao

- `playback_service.start(composition)`: inicia a reproducao em uma thread interna e retorna sem bloquear a thread da interface.
- `playback_service.stop()`: solicita interrupcao da reproducao atual.
- `playback_service.is_playing()`: retorna `True` enquanto existe uma reproducao em andamento.
- `playback_service.close()`: interrompe a reproducao e libera recursos do player.

## Dependencia de audio

`FluidSynthPlayer` usa `pyfluidsynth` com importacao tardia. O caminho do SoundFont deve ser informado por `SOUNDFONT_PATH` ou pelo argumento `soundfont_path`.

O nucleo de interpretacao (`SequenceGenerator`, `TextInterpreter`, regras e dominio) nao depende de FluidSynth e pode ser testado sem audio instalado.

## Contrato da Fase 2

A Fase 2 expoe um gerador separado para preservar a API da Fase 1:

```python
from music_generator.application.playback_service import PlaybackService
from music_generator.application.polyphonic_generator import PolyphonicSequenceGenerator
from music_generator.domain.settings import PlaybackSettings
from music_generator.infrastructure.audio.fluidsynth_player import FluidSynthPlayer

text = "CDE\n[4] > MbG"

settings = PlaybackSettings(
    bpm=120,
    initial_volume=80,
    default_octave=4,
    initial_instrument=0,
)

composition = PolyphonicSequenceGenerator().generate(text, settings)

player = FluidSynthPlayer()
playback_service = PlaybackService(player)
playback_service.start(composition)
```

`PolyphonicSequenceGenerator.generate()` retorna uma `PolyphonicComposition`
com:

- `voices`: sequencia imutavel de `MusicalVoice`, uma por linha de entrada;
- `timeline`: sequencia imutavel de `ScheduledMusicalEvent` ja ordenada;
- `initial_bpm`: BPM global inicial.

Cada `ScheduledMusicalEvent` possui:

- `absolute_beat`: posicao absoluta em beats;
- `voice_index`: indice da voz (`0` para `V0`, `1` para `V1`, etc.);
- `origin_order`: ordem do token dentro da voz;
- `event`: `BpmChangeEvent`, `NoteStartEvent` ou `NoteEndEvent`.

A ordenacao da timeline e:

1. beat absoluto;
2. mudancas de BPM antes de eventos de nota;
3. encerramentos de nota antes de novos inicios;
4. indice da voz;
5. ordem de origem.

O `PlaybackService` aceita tanto `MusicalComposition` quanto
`PolyphonicComposition`, mantendo a reproducao em thread interna para nao
bloquear a interface. `FluidSynthPlayer` usa canais melodicos distintos por voz
e reserva o canal MIDI 9 para percussao.

Limites e erros:

- no maximo 15 vozes melodicas por composicao;
- prefixos de atraso devem usar `[n]`, com `n` inteiro nao negativo;
- BPM global minimo e `10`;
- SoundFont e FluidSynth continuam dependencias externas da infraestrutura de audio.
