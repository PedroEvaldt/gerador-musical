# 📌 Git Workflow — Regras de Branches e Commits


### 📌 Estrutura

<tipo>/<descricao>

---

### 🎯 Tipos de branch

- feature/ → nova funcionalidade  
- bugfix/ → correção de bug  
- hotfix/ → correção urgente em produção  
- refactor/ → melhoria interna  
- chore/ → configuração / infra  
- docs/ → documentação  

---

### 📏 Regras

- Usar kebab-case (hífen)
- Usar letras minúsculas
- Não usar espaços ou caracteres especiais
- Nome deve ser curto e descritivo

---

### ✅ Exemplos

feature/login  
feature/add-user-authentication  
bugfix/fix-navbar-error  
refactor/api-cleanup  

---

## 🧱 2. Nomenclatura de Commits

### 📌 Estrutura

<tipo>: descricao

Exemplo:

feat: adiciona login com JWT

---

### 🎯 Tipos de commit

- feat → nova funcionalidade  
- fix → correção de bug  
- refactor → melhoria interna  
- chore → config / infra  
- docs → documentação  
- test → testes  

---

### 📏 Regras

- Começar com o tipo
- Usar verbo no imperativo (ex: "adiciona", "corrige")
- Mensagem curta e clara (~50 caracteres)
- Um commit = uma única responsabilidade
- Opcional: adicionar descrição detalhada no corpo

---

### ✅ Exemplos

feat: adiciona endpoint de login  
fix: corrige erro de autenticação  
refactor: melhora estrutura do serviço  
chore: configura docker  

---

## 🔄 3. Pipeline de Trabalho

### 📌 Fluxo padrão

main  
↓  
nova branch  
↓  
commits pequenos  
↓  
rebase com main  
↓  
push  
↓  
pull request  
↓  
review  
↓  
merge  
↓  
delete branch  

---

### 🚀 Passo a passo

1. Atualizar a main

git switch main  
git pull origin main  

---

2. Criar nova branch

git switch -c feature/nome-da-feature  

---

3. Fazer commits

git add .  
git commit -m "feat: adiciona funcionalidade"  

---

4. Atualizar com a main (rebase)

Opcional: Fazer stash dos commits para manter um histórico mais limpo
git pull origin main --rebase  

---

5. Enviar branch

git push origin feature/nome-da-feature  

---

6. Criar Pull Request

- Revisão de código  
- Testes  
- Validação  

---

7. Merge (preferencial)

Squash and merge  

---

8. Deletar branch

git branch -d feature/nome-da-feature  

---

## ⚠️ Boas Práticas Essenciais

- main deve estar sempre estável  
- Branches devem ser curtas (1–3 dias)  
- Commits devem ser pequenos e claros  
- Sempre usar Pull Request  
- Integrar frequentemente com a main  

---
