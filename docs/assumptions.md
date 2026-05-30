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
- Funcionalidades da Fase 2 foram deliberadamente adiadas.
