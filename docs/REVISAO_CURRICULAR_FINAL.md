# Revisão curricular — Campus Study

## Alterações incluídas

- O catálogo em `docs/CATALOGO_DE_ASSUNTOS.json` é idêntico à cópia `src/backend/data/curriculum_catalog.json`, que é carregada pelo seed do backend. Isso impede que o PDF/JSON e a plataforma exibam catálogos diferentes.
- Foram substituídos os tópicos-placeholder por roteiros de estudo mais específicos, associados ao campo de cada disciplina.
- A auditoria confirma zero nomes de disciplinas repetidos entre períodos do mesmo curso, após normalização de acentos, caixa, espaços e hífens.
- A auditoria confirma zero assuntos com nome exatamente igual aparecendo em períodos diferentes do mesmo curso.
- Foram reorganizados os períodos finais de Nutrição (10), Sistemas de Informação (9) e Ciências Contábeis (9), separando estágios e TCC nos períodos finais de referência.
- O ENEM tem matérias e assuntos sem período universitário visível. O campo técnico interno `periodo=1` permanece apenas por compatibilidade com o banco atual.
- A migração do seed arquiva disciplinas e assuntos antigos fora da estrutura nova, sem apagar seus registros; o seed cria/reacende os registros correspondentes ao catálogo atual.

## Limite acadêmico importante

O teste de duplicação é uma verificação de catálogo, não prova que toda matriz corresponde integralmente ao PPC oficial de cada universidade. Neste pacote, Odontologia usa como referência específica o PPC 2023 da UFG e o ENEM usa a matriz de referência do INEP. Para os demais cursos, foram registrados links oficiais ou o portal institucional como ponto de consulta, mas a transcrição integral de todas as disciplinas, períodos e ementas não foi concluída. Consulte `CURRICULOS_E_FONTES.json` para o status individual de cada curso. Os assuntos são roteiros de estudo relacionados à disciplina, não ementas oficiais completas.

## Contagem técnica

- Cursos: 24
- Combinações curso/disciplina/período: 810
- Registros de assuntos: 3246
- Períodos universitários cadastrados (ENEM excluído): 216

## Status por curso

| Curso | Períodos na base | Estado da fonte curricular |
|---|---:|---|
| ENEM | — | Matriz de referência do INEP identificada; os tópicos do catálogo são uma síntese para estudo, não uma lista exaustiva do exame. |
| Administração | 8 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Agronomia | 10 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Arquitetura e Urbanismo | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Biomedicina | 8 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Ciência da Computação | 8 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Ciências Contábeis | 9 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Direito | 10 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Educação Física | 8 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Enfermagem | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Engenharia Civil | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Engenharia Elétrica | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Engenharia Mecânica | 10 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Farmácia | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Fisioterapia | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Jornalismo | 8 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Marketing | 8 | A matriz e a instituição federal de referência precisam ser confirmadas; a grade permanece como roteiro preliminar de estudo. |
| Medicina | 12 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Medicina Veterinária | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Nutrição | 10 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Odontologia | 10 | PPC da UFG (2023) identificado como referência; as disciplinas estão estruturadas no pacote e os tópicos são roteiros de estudo, não a transcrição integral de todas as ementas. |
| Pedagogia | 8 | Portal institucional da UFG identificado como ponto de consulta; a matriz específica, a versão vigente e as ementas não foram transcritas e conferidas integralmente. |
| Psicologia | 10 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
| Sistemas de Informação | 9 | Página oficial do curso identificada como fonte de consulta; a transcrição integral dos períodos e ementas ainda precisa ser conferida contra a versão curricular vigente. |
