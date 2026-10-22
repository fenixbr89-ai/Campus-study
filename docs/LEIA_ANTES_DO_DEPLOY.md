# Antes de publicar esta versão do Campus Study

## O que mudou no currículo

O catálogo atualizado está em `docs/CATALOGO_DE_ASSUNTOS.json` e em `src/backend/data/curriculum_catalog.json`. O backend agora usa a cópia em `src/backend/data`, que é incluída pela instrução `COPY src/backend ./backend` do `Dockerfile.backend`.

Ao iniciar, o backend executa o seed do catálogo. Ele cria/atualiza cursos, períodos, disciplinas e assuntos previstos e arquiva registros antigos que ficaram fora da estrutura nova, sem apagá-los definitivamente. Faça um backup do MongoDB antes de publicar qualquer migração.

## Publicação

1. Extraia este ZIP na raiz do repositório e envie os arquivos atualizados para o GitHub.
2. Faça o deploy do **backend** no serviço que atende `https://campus-study-8bti.onrender.com`. Publicar apenas o frontend no Vercel não atualiza o catálogo no banco, pois a API e o seed rodam no backend.
3. Faça também o deploy do frontend no Vercel, usando o `vercel.json` da raiz.
4. Após o backend iniciar e executar o seed, confira `/api/courses` e abra alguns cursos, períodos e assuntos. Confirme que ENEM está primeiro e não apresenta períodos universitários.
5. Antes de atualizar o banco de produção, tenha um backup recente para permitir recuperação se os dados atuais forem necessários.

## Testes que podem ser executados na raiz

```bash
python scripts/audit_curriculum.py
python scripts/final_validation.py
npm run build
```

A auditoria curricular verifica duplicatas exatas de disciplinas/assuntos entre períodos e garante que o JSON de docs seja igual ao arquivo embarcado no backend. Esses testes não substituem a comparação acadêmica da matriz inteira com o PPC vigente de cada curso.

## Status da validação acadêmica

O relatório `CURRICULOS_E_FONTES.json` registra a fonte e o estado individual de cada curso. Odontologia usa como referência específica o PPC 2023 da UFG; ENEM usa a matriz de referência do INEP. Para as demais graduações, a transcrição integral de todos os períodos e ementas oficiais ainda precisa ser conferida. Não anuncie esses catálogos como transcrições oficiais certificadas antes dessa conferência.
