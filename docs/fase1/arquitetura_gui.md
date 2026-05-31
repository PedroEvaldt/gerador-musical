# Arquitetura da Interface Grafica

A interface grafica foi implementada como uma camada de apresentacao independente, sem logica de negocio propria. Toda a geracao e reproducao musical continua sendo responsabilidade do nucleo existente.

---

## 1. Posicao na Arquitetura Geral

A interface ocupa o topo do pipeline ja estabelecido:

```
MusicGeneratorApp (gui.py)
↓
SequenceGenerator
↓
TextInterpreter
↓
MusicalComposition
↓
PlaybackService → FluidSynthPlayer
```

A GUI coleta texto e configuracoes do usuario, delega a geracao ao `SequenceGenerator` e o controle de reproducao ao `PlaybackService`. Nao conhece regras de interpretacao, eventos musicais nem detalhes do player de audio.

---

## 2. Estrutura do Modulo

O modulo e composto por um unico arquivo:

```
src/
└── gui.py          ← interface grafica (MusicGeneratorApp + constante INSTRUMENTS)
```

Os testes ficam em:

```
tests/
└── unit/
    └── test_gui.py
```

---

## 3. Componentes

### 3.1 MusicGeneratorApp

Classe principal da interface. Herda de `tk.Tk` e e responsavel por:

- Construir todos os widgets da janela.
- Reagir a acoes do usuario (play, pause, limpar texto).
- Delegar ao `SequenceGenerator` a geracao da composicao.
- Delegar ao `PlaybackService` o controle da reproducao.
- Atualizar a barra de progresso e o cronometro enquanto a musica toca.
- Liberar recursos de audio ao fechar a janela.

### 3.2 Constante INSTRUMENTS

Dicionario que mapeia nomes legiveis de instrumentos para indices General MIDI (0–127). Centraliza o mapeamento e desacopla os widgets do dominio numerico do MIDI.

---

## 4. Widgets e Responsabilidades

| Widget | Tipo | Responsabilidade |
|---|---|---|
| Campo de texto | `tk.Text` | Recebe o texto a ser convertido em musica |
| Instrumento inicial | `ttk.Combobox` | Seleciona o instrumento de entrada por nome |
| BPM | `tk.Spinbox` | Define os beats por minuto (20–300) |
| Oitava padrao | `tk.Spinbox` | Define a oitava inicial (0–9) |
| Volume inicial | `tk.Scale` | Define o volume inicial (0–127) |
| Botao play | `tk.Button` | Inicia a reproducao |
| Botao pause | `tk.Button` | Pausa ou retoma a reproducao |
| Botao limpar | `tk.Button` | Apaga o campo de texto |
| Cronometro | `tk.Label` | Exibe o tempo decorrido no formato MM:SS |
| Barra de progresso | `ttk.Progressbar` | Indica o andamento estimado da reproducao |
| Barra de status | `tk.Label` | Exibe o estado atual ("Pronto", "Reproduzindo...", "Pausado") |

---

## 5. Fluxo de Reproducao

1. O usuario insere texto e ajusta as configuracoes.
2. Ao clicar em play, `_on_play()` e invocado.
3. `_build_settings()` constroi um `PlaybackSettings` a partir dos widgets.
4. `SequenceGenerator.generate()` produz uma `MusicalComposition`.
5. Um `FluidSynthPlayer` e criado e entregue a um novo `PlaybackService`.
6. `PlaybackService.start()` inicia a reproducao em uma thread interna e retorna imediatamente, sem bloquear a UI.
7. A GUI inicia um loop de atualizacao com `after()` a cada 200 ms para atualizar cronometro e barra de progresso.
8. Ao parar (pause ou fim), os botoes retornam ao estado inicial.

---

## 6. Decisoes de Projeto

### Thread de audio separada

`PlaybackService.start()` ja executa a reproducao em uma thread interna. A GUI nunca bloqueia a thread principal do Tkinter, garantindo que a janela continue responsiva durante a musica.

### Progresso estimado

A barra de progresso e o cronometro sao estimados a partir da duracao calculada da composicao (total de beats × segundos por beat). Nao ha leitura de posicao real do player, pois o `AudioPlayer` nao expoe essa informacao.

### Sem estado de seek

O `PlaybackService` nao oferece seek. A funcao de pause interrompe a reproducao e, ao retomar, reinicia do inicio. Esse comportamento e consistente com o contrato da Fase 1.

### Isolamento da logica de negocio

A GUI nao contem regras de interpretacao musical. Qualquer mudanca nas regras de mapeamento de caracteres, nos eventos ou no player e transparente para a interface.

---

## 7. Extensibilidade

A arquitetura da GUI permite evoluir sem alterar o nucleo:

- Novos instrumentos podem ser adicionados ao dicionario `INSTRUMENTS` sem mudar nenhum outro componente.
- Suporte a seek pode ser implementado adicionando o metodo correspondente ao `AudioPlayer` e conectando ao slider de progresso.
- Exportacao MIDI pode ser adicionada como um novo botao que chama um servico independente.
- Temas visuais podem ser alterados centralizando as cores em constantes no topo do arquivo.
