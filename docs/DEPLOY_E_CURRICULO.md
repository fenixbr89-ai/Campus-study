# Publicação e aplicação do catálogo curricular

## Frontend no Vercel
- Raiz do repositório: raiz deste ZIP.
- Build command: `npm run build`.
- Output directory: `src/frontend/dist` (configurado em `vercel.json`).
- O build instala dependências travadas com `npm ci` e executa TypeScript + Vite.

## Backend — obrigatório para atualizar o catálogo real
A mudança do catálogo fica em `src/backend/seed.py`; publicar apenas o frontend não atualiza o banco. O backend precisa ser implantado no serviço que atende a API (`https://campus-study-8bti.onrender.com/api`, conforme a configuração atual).

Antes de aplicar a migração:
1. Faça backup do banco MongoDB.
2. Implante o backend atualizado.
3. Confirme nos logs que `seed_curriculum()` terminou sem erro.
4. Confira `/api/courses` e uma disciplina de cada curso.
5. Teste que os itens arquivados não aparecem no catálogo público e que os registros continuam preservados no banco.

O seed atualiza e reativa itens que pertencem à matriz configurada; disciplinas fora da matriz ou no período errado são arquivadas, e assuntos antigos em disciplinas ativas também são arquivados. Não há exclusão definitiva desses registros.

## Verificações locais
- `python3 scripts/audit_curriculum.py`: valida o catálogo estático e falha se uma disciplina normalizada aparecer em mais de um período do mesmo curso.
- `python3 -m py_compile src/backend/seed.py src/backend/routers/ai.py src/backend/routers/study.py src/backend/routers/catalog.py`: valida sintaxe Python.
- `npm run build`: valida compilação completa do frontend; requer que `npm ci` consiga baixar todas as dependências.

## Estado curricular
- ENEM: catálogo especial por matérias, sem períodos na interface, baseado em tópicos orientativos da matriz do INEP.
- Odontologia: referência do PPC 2023 da UFG.
- Demais cursos: alocação de disciplinas congelada para evitar redistribuição automática, sem duplicatas exatas detectadas; a conferência de cada matriz e ementa oficial continua pendente. Consulte `AUDITORIA_CURRICULAR.md`.
