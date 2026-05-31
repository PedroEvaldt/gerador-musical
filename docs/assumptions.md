# Suposicoes da Fase 1

- Cada nota e pausa dura inicialmente `1.0` beat.
- IDs dos instrumentos sao armazenados entre `0` e `127`.
- Numeros dos instrumentos do enunciado sao utilizados literalmente, sem subtrair `1`.
- Soma de instrumento com digito par e limitada a `127`.
- Oitavas aceitas ficam entre `0` e `9`.
- Repeticao considera somente o caractere imediatamente anterior do texto.
- Quebra de linha troca instrumento na Fase 1.
- Arquivo SoundFont nao faz parte do repositorio.
- Caminho do SoundFont e informado por `SOUNDFONT_PATH` ou por argumento explicito do player.
- A API da Fase 1 permanece disponivel via `SequenceGenerator`.

# Suposicoes da Fase 2

- O nucleo polifonico e exposto por `PolyphonicSequenceGenerator`, sem substituir
  `SequenceGenerator`.
- Uma entrada vazia gera uma composicao sem vozes.
- Linhas vazias internas sao vozes silenciosas; uma quebra final isolada nao
  cria voz extra porque a separacao usa `splitlines()`.
- Comandos locais de volume, instrumento e oitava nao consomem beat.
- Mudancas globais de BPM tambem nao consomem beat e sao resolvidas na timeline
  em ordem cronologica, depois por voz e ordem de origem.
- `>` e `<` armazenam comandos de delta durante a interpretacao; o BPM absoluto
  final e calculado pelo `TimelineScheduler`.
- Pausas avancam o relogio da voz, mas nao geram eventos na timeline de
  reproducao porque nao acionam MIDI diretamente.
- Eventos locais de comando permanecem em `MusicalVoice.events` para futura
  exportacao MIDI ou inspecao pela interface.
- O canal MIDI 9 e sempre reservado e nao e atribuido a vozes melodicas.
