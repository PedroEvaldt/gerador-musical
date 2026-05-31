# Suposicoes da Interface Grafica

- A interface nao possui logica de interpretacao musical; delega integralmente ao nucleo da Fase 1.
- O progresso exibido na barra e no cronometro e uma estimativa calculada a partir da duracao total da composicao, nao uma leitura da posicao real do player.
- A funcao de pause interrompe a reproducao e, ao retomar, reinicia do inicio, pois o `PlaybackService` nao oferece seek.
- Um novo `FluidSynthPlayer` e criado a cada acionamento do botao play. Recursos do player anterior sao liberados pelo `PlaybackService` correspondente quando a reproducao termina ou e encerrada.
- O dicionario `INSTRUMENTS` usa indices General MIDI literais (0–127), seguindo a mesma convencao adotada no nucleo da Fase 1.
- O slider de volume mapeia diretamente para o campo `initial_volume` de `PlaybackSettings`, cujo range valido e 0–127.
- O campo de texto aceita qualquer sequencia de caracteres Unicode. A filtragem e interpretacao dos caracteres sao responsabilidade do `TextInterpreter`.
- A janela nao e redimensionavel para manter o layout previsivel sem uso de geometria responsiva.
- A barra de status e atualizada na thread principal do Tkinter por meio de `after()`, garantindo seguranca de thread sem necessidade de locks adicionais na GUI.
- Erros de configuracao invalida e erros de inicializacao do FluidSynth sao apresentados ao usuario por meio de caixas de dialogo e nao interrompem o processo.
- O arquivo SoundFont nao faz parte do repositorio. O caminho deve ser informado por `SOUNDFONT_PATH` ou por argumento explicito do player, conforme definido no contrato de integracao da Fase 1.
