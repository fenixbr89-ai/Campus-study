# Publicação e aplicação do catálogo curricular

## Frontend no Vercel
- Raiz do repositório: raiz deste ZIP.
- Build command: `npm run build`.
- Output directory: `src/frontend/dist` (configurado em `vercel.json`).
- O build instala dependências travadas com `npm ci` e executa TypeScript + Vite.

## Backend — obrigatório para atualizar o catálogo real
A mudança do catálogo está em `src/backend/curriculum_data.py` e `src/backend/seed.py`; publicar apenas o frontend não atualiza o banco. O backend precisa ser implantado no serviço que atende a API (`https://campus-study-8bti.onrender.com/api`, conforme a configuração atual).

Antes de aplicar a migração:
1. Faça backup do banco MongoDB.
2. Implante o backend atualizado.
3. Confirme nos logs que `seed_curriculum()` terminou sem erro.
4. Confira `/api/courses` e algumas disciplinas de cada curso.
5. Teste que itens arquivados não aparecem no catálogo público e que registros continuam preservados no banco.

O seed atualiza e reativa itens que pertencem à matriz configurada; disciplinas fora da matriz ou no período errado são arquivadas, e assuntos antigos em disciplinas ativas também são arquivados. Não há exclusão definitiva desses registros.

## Verificações locais
- `python3 scripts/generate_curriculum_catalog.py`: regenera `docs/CATALOGO_DE_ASSUNTOS.json` a partir da fonte única de dados.
- `python3 scripts/audit_curriculum.py`: valida cursos, períodos, fontes e ausência de nomes exatos de disciplina/assunto repetidos entre períodos.
- `python3 -m py_compile src/backend/seed.py src/backend/curriculum_data.py src/backend/routers/ai.py src/backend/routers/study.py src/backend/routers/catalog.py`: valida sintaxe Python.
- `python3 scripts/validate_student_experience.py`: valida estática de rotas e funções já existentes.
- `npm run build`: valida compilação completa do frontend. Requer que `npm ci` consiga baixar todas as dependências.

## Limite curricular
A auditoria estrutural não é uma certificação acadêmica. ENEM usa a matriz de referência do INEP; Odontologia, Medicina e Enfermagem têm matrizes específicas referenciadas. Os demais cursos mantêm fonte institucional identificada, porém marcados como referência parcial quando não houve transcrição integral de cada componente obrigatório e ementa oficial. Marketing é uma trilha independente, não matriz oficial de graduação. Consulte `AUDITORIA_CURRICULAR.md` antes de divulgar qualquer grade como oficial.
