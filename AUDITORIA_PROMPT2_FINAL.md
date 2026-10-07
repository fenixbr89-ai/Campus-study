# CAMPUS STUDY — Prompt 2 / Experiência do Estudante

## Estado
Esta versão foi construída sobre o projeto do Prompt 1. O projeto existente foi preservado; não houve recriação do sistema.

## Implementado

### Dashboard acadêmico
- Novo endpoint `/api/academic-dashboard`.
- Curso atual quando definido no perfil.
- Período inferido a partir do progresso acadêmico persistido.
- Progresso por assuntos.
- Questões respondidas, taxa de acerto, simulados, minutos, sequência e pontos.
- Posição mensal no ranking quando o usuário participa.
- Recomendações baseadas em assuntos ainda não concluídos, com motivo explícito.
- Nova seção "Visão acadêmica" no início.

### Revisão de questões / repetição espaçada
- Nova coleção `question_reviews`.
- Marcação "Revisar depois" dentro do simulado.
- Persistência por usuário.
- Página `/revisao`.
- Filtro de questões para hoje/todas.
- Registro de acerto/erro.
- Intervalo inicial e expansão simples até 60 dias.
- Exclusão da revisão.
- Questões não são inventadas e os dados vêm do simulado persistido.

### Favoritos
- Favoritos de conteúdos existentes foram preservados.
- Novo favorito de assunto.
- Nova coleção `topic_favorites`.
- Botão de favorito na página do assunto.
- Aba "Assuntos favoritos" na Biblioteca.

### Anotações
- Fluxo existente preservado.
- Nova anotação pode ser vinculada a assunto.
- Edição preserva o vínculo existente.

### Busca
- Pesquisa global transformada em experiência de pesquisa avançada.
- Filtros de curso, período, disciplina, assunto e tipo de conteúdo.
- Reutilização das APIs de filtros já existentes.
- Resultados de catálogo continuam separados dos registros pessoais/global search.

### Mobile e acessibilidade
- Alvos de toque mínimos em telas pequenas.
- `:focus-visible` explícito.
- Suporte a `prefers-reduced-motion`.
- Navegação horizontal existente foi preservada onde necessária para mobile.
- Não foi feita reescrita do frontend.

### PWA
- Manifest existente preservado e validado.
- Identidade Campus Study preservada.
- Instalação Android/Chrome via `beforeinstallprompt` quando disponível.
- Instruções específicas para iPhone/iPad.
- Modo standalone deixa de mostrar instalação novamente.
- Service Worker atualizado para cache versionado `campus-study-shell-v2`.
- API/autenticação continuam fora do cache.

### LGPD / conta
- `question_reviews` e `topic_favorites` adicionados à exportação de dados.
- As mesmas coleções entram na exclusão da conta.

## Preservado
- Autenticação existente.
- Perfil.
- Admin e permissões.
- Cursos/períodos/disciplinas/assuntos.
- Conteúdos.
- Biblioteca e favoritos de conteúdo.
- Simulados.
- Plano de estudos.
- Tempo de estudo real.
- Meta diária.
- Ranking mensal.
- PWA existente.
- Remoções anteriores de Calendar e Weekly Goals.

## Arquivos principais alterados
- `src/backend/models/schemas.py`
- `src/backend/lib/db.py`
- `src/backend/routers/study.py`
- `src/backend/routers/auth.py`
- `src/frontend/src/App.tsx`
- `src/frontend/src/components/AppLayout.tsx`
- `src/frontend/src/components/PwaInstallPrompt.tsx`
- `src/frontend/src/pages/Home.tsx`
- `src/frontend/src/pages/StudentTools.tsx`
- `src/frontend/src/pages/Study.tsx`
- `src/frontend/src/pages/Catalog.tsx`
- `src/frontend/src/pages/Account.tsx`
- `src/frontend/src/lib/types.ts`
- `src/frontend/src/index.css`
- `src/frontend/public/sw.js`
- `scripts/validate_student_experience.py`

## Banco
Novas coleções:
- `question_reviews`
- `topic_favorites`

Índices adicionados para isolamento por usuário e consultas de revisão.

## Variáveis de ambiente
Nenhuma variável nova é necessária para esta etapa.

## Testes executados
- `scripts/validate_student_experience.py` → **PASS**
- Python AST/compilação de todos os arquivos backend → **PASS**
- Transpile/sintaxe de todos os 48 arquivos `.ts/.tsx` → **PASS**
- Manifest JSON → **PASS**
- Service Worker `node --check` → **PASS**
- Verificação estática de rotas novas → **PASS**

## Testes que não puderam ser aprovados neste ambiente

### Integração backend
O suite existente `tests/test_stage2.py` não pôde ser considerado aprovado porque:
1. o ambiente não possui `pytest-xdist`, exigido pelo `pytest.ini` original;
2. ao executar uma configuração serial equivalente, os testes tentaram acessar o backend em `localhost:8001`, mas não havia servidor/MongoDB disponível e as conexões foram recusadas.

Não foi alterado o `pytest.ini` para mascarar essa limitação.

### Build frontend
`npm ci` foi tentado uma única vez e excedeu o limite de transporte do ambiente. Como não há `node_modules` instalado, não é correto declarar `npm run build` como aprovado.

A validação de sintaxe/transpile dos 48 arquivos TypeScript/TSX passou, mas isso **não substitui** o build real do Vite/TypeScript.

## Resultado
Código estático: **OK**.
Build de produção: **não validado neste ambiente**.
Integração MongoDB/Render/Vercel: **não validada neste ambiente**.

## Próxima validação recomendada
Em ambiente com dependências instaláveis e MongoDB disponível:
1. `npm ci --no-audit --no-fund` em `src/frontend`;
2. `npm run typecheck`;
3. `npm run build`;
4. executar a suíte `src/backend/tests` com o Mongo/servidor de teste configurado;
5. testar instalação PWA em Chrome Android e Safari iOS;
6. testar simulados em viewport mobile;
7. testar `/academic-dashboard`, `/revisao`, favoritos de assunto e busca filtrada com usuário real.

Não há alegação de que essas integrações foram aprovadas neste ambiente.
