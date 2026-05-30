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
