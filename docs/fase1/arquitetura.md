A arquitetura foi organizada como um pipeline de processamento.

---

## 2. Fluxo Geral do Sistema

O funcionamento do sistema segue o seguinte fluxo:

1. O usuário insere um texto e configura parâmetros iniciais (BPM, volume, instrumento, oitava).
2. Os parâmetros são validados.
3. Um estado musical inicial é criado.
4. O texto é interpretado caractere por caractere.
5. Eventos musicais são gerados.
6. Os eventos são enviados para o sistema de reprodução sonora.

---

## 3. Estrutura de Módulos

O sistema foi dividido em módulos principais, cada um com responsabilidade bem definida.

### 3.1 Configuração
Responsável por armazenar e validar parâmetros iniciais.

- PlaybackSettings

---

### 3.2 Estado de Execução
Responsável por manter o estado atual da música durante a interpretação.

- EstadoMusical

---

### 3.3 Domínio Musical
Representa os elementos fundamentais da música gerada.

- EventoMusical (classe base)
- EventoNota
- EventoPausa
- EventoTrocaInstrumento
- EventoMudancaVolume

---

### 3.4 Interpretação (Parser)
Responsável por converter o texto em eventos musicais.

- InterpretadorTexto

---

### 3.5 Orquestração
Responsável por coordenar o fluxo do sistema.

- GeradorSequencia

---

### 3.6 Reprodução (Player)
Responsável por executar os eventos musicais.

- GeradorSom

---

### 3.7 Interface com Usuário
Responsável pela interação com o usuário.

- Interface gráfica (TextArea, sliders, botões)

---

## 4. Diagrama Conceitual (Fluxo)

Representação simplificada da arquitetura:

UI
↓
GeradorSequenciaMusical
↓
InterpretadorTexto
↓
EventosMusicais
↓
GeradorSom

---

## 5. Descrição das Responsabilidades

### PlaybackSettings
Armazena e valida os parâmetros iniciais definidos pelo usuário.

---

### EstadoMusical
Mantém o estado atual da execução, incluindo instrumento, volume, oitava e última nota tocada.

---

### InterpretadorTexto
Percorre o texto de entrada e aplica regras de mapeamento para gerar eventos musicais.

---

### EventoMusical e subclasses
Representam ações musicais que podem ser executadas, como tocar uma nota, pausar ou alterar parâmetros.

---

### GeradorSequenciaMusical
Coordena todo o fluxo do sistema, integrando interpretação, estado e execução sonora.

---

### GeradorSom
Executa os eventos musicais utilizando uma biblioteca de áudio.

---

## 6. Decisões de Projeto

### Uso de Eventos Musicais
O sistema utiliza uma abordagem baseada em eventos para representar ações musicais.  
Isso permite:
- maior extensibilidade
- facilidade de testes
- desacoplamento entre interpretação e execução

---

### Separação de Responsabilidades
Cada classe possui uma única responsabilidade, facilitando manutenção e evolução do sistema.

---

### Uso de Estado Explícito
O EstadoMusical centraliza todas as informações dinâmicas da execução, evitando variáveis globais e facilitando o controle do fluxo.

---

### Arquitetura em Pipeline
O sistema foi estruturado como um pipeline:
entrada → interpretação → geração → execução

Isso facilita a compreensão e a evolução do sistema.

---

## 7. Extensibilidade

A arquitetura foi projetada para facilitar futuras mudanças, como:

- inclusão de novas regras de mapeamento
- novos tipos de eventos musicais
- suporte a diferentes bibliotecas de áudio
- exportação para arquivos MIDI

---

## 8. Considerações Finais

A arquitetura prioriza clareza, modularidade e facilidade de evolução, atendendo aos requisitos do trabalho prático.

O foco principal não é apenas a execução correta, mas a organização e qualidade do código.
