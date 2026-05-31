# Testes Manuais da Interface Grafica

Registro dos cenarios testados manualmente na interface grafica do Gerador de Musica por Texto.

Ambiente: Python 3.12, Tkinter, sem FluidSynth instalado (exceto onde indicado).

---

## Criterios de avaliacao

- **Passou**: comportamento correspondeu ao esperado.
- **Falhou**: comportamento divergiu do esperado.

---

## 1. Inicializacao

| # | Cenario | Acao | Resultado esperado | Resultado |
|---|---|---|---|---|
| 1.1 | Abertura da janela | Executar `python gui.py` | Janela abre com titulo "INF01120 - Gerador de Musica por Texto", campo de texto vazio, BPM 180, oitava 4, instrumento Piano, botao pause desabilitado, status "Pronto" | Passou |
| 1.2 | Janela nao redimensionavel | Tentar arrastar as bordas da janela | Tamanho permanece fixo | Passou |

---

## 2. Campo de texto

| # | Cenario | Acao | Resultado esperado | Resultado |
|---|---|---|---|---|
| 2.1 | Digitacao livre | Digitar texto no campo | Caracteres aparecem normalmente | Passou |
| 2.2 | Colar texto | Colar um texto longo com Ctrl+V | Texto colado integralmente, sem truncamento | Passou |
| 2.3 | Multiplas linhas | Pressionar Enter para quebrar linha | Quebra de linha inserida normalmente | Passou |
| 2.4 | Limpar texto preenchido | Preencher o campo e clicar em "Limpar Texto" | Campo fica vazio | Passou |
| 2.5 | Limpar texto ja vazio | Clicar em "Limpar Texto" com campo vazio | Nenhum erro, campo continua vazio | Passou |

---

## 3. Painel de configuracoes

| # | Cenario | Acao | Resultado esperado | Resultado |
|---|---|---|---|---|
| 3.1 | Selecao de instrumento | Abrir o combobox e selecionar cada instrumento | Lista exibe todos os instrumentos; selecao reflete no widget | Passou |
| 3.2 | BPM minimo | Ajustar o spinbox de BPM para 20 | Valor aceito sem erro | Passou |
| 3.3 | BPM maximo | Ajustar o spinbox de BPM para 300 | Valor aceito sem erro | Passou |
| 3.4 | Oitava minima | Ajustar o spinbox de oitava para 0 | Valor aceito sem erro | Passou |
| 3.5 | Oitava maxima | Ajustar o spinbox de oitava para 9 | Valor aceito sem erro | Passou |
| 3.6 | Slider de volume no minimo | Arrastar o slider ate o limite esquerdo | Valor chega a 0 | Passou |
| 3.7 | Slider de volume no maximo | Arrastar o slider ate o limite direito | Valor chega a 127 | Passou |

---

## 4. Validacoes ao clicar em play

| # | Cenario | Acao | Resultado esperado | Resultado |
|---|---|---|---|---|
| 4.1 | Play com campo vazio | Deixar o campo vazio e clicar em play | Dialogo de aviso "Texto vazio" aparece; reproducao nao inicia; status permanece "Pronto" | Passou |
| 4.2 | Play com apenas espacos | Inserir somente espacos e clicar em play | Mesmo comportamento do campo vazio | Passou |
| 4.3 | Play sem FluidSynth | Inserir texto valido e clicar em play sem FluidSynth instalado | Dialogo de erro "Erro de audio" aparece; reproducao nao inicia; status permanece "Pronto" | Passou |

---

## 5. Reproducao (requer FluidSynth e SoundFont configurados)

| # | Cenario | Acao | Resultado esperado | Resultado |
|---|---|---|---|---|
| 5.1 | Play com texto valido | Inserir "ABCDEFGH" e clicar em play | Reproducao inicia; status muda para "Reproduzindo..."; botao play desabilita; botao pause habilita; cronometro avanca; barra de progresso avanca | Passou |
| 5.2 | Fim natural da reproducao | Aguardar a musica terminar | Botao play reabilita; botao pause desabilita; status volta para "Pronto"; cronometro volta para 00:00; barra de progresso volta a zero | Passou |
| 5.3 | Pause durante reproducao | Clicar em pause enquanto a musica toca | Reproducao para; status muda para "Pausado"; icone do botao muda para "▶▶" | Passou |
| 5.4 | Retomar apos pause | Clicar no botao pause novamente enquanto pausado | Reproducao reinicia do inicio; status volta para "Reproduzindo..."; cronometro reinicia | Passou |
| 5.5 | Play com texto longo | Inserir um texto com mais de 200 caracteres e clicar em play | Reproducao inicia normalmente; progresso e cronometro refletem a duracao maior | Passou |
| 5.6 | Play com texto apenas de simbolos e numeros | Inserir "123!@#$%" e clicar em play | Reproducao inicia (caracteres sem nota geram pausas); nenhum erro | Passou |
| 5.7 | Fechar janela durante reproducao | Clicar no X da janela enquanto a musica toca | Reproducao para; recursos de audio sao liberados; janela fecha sem erro | Passou |

---

## 6. Barra de status

| # | Cenario | Resultado esperado | Resultado |
|---|---|---|---|
| 6.1 | Estado inicial | Exibe "Pronto" | Passou |
| 6.2 | Durante reproducao | Exibe "Reproduzindo..." | Passou |
| 6.3 | Apos pause | Exibe "Pausado" | Passou |
| 6.4 | Apos fim da musica | Volta para "Pronto" | Passou |
| 6.5 | Apos erro de audio | Permanece "Pronto" | Passou |
