# Auditoria curricular — Campus Study

**Build de revisão: 2026-10-21**

## Resultado das verificações automatizadas

O catálogo estático foi regenerado a partir da fonte única `src/backend/curriculum_data.py` e pode ser auditado com `python scripts/audit_curriculum.py`.

- Cursos/listas: **24** (ENEM, 22 graduações/trilhas universitárias e a trilha independente de Marketing).
- Disciplinas atribuídas a curso e período: **1.131**.
- Registros disciplina/assunto: **4.563**.
- Nomes de disciplinas repetidos entre períodos do mesmo curso após normalização: **0**.
- Títulos de assuntos exatamente repetidos em períodos diferentes do mesmo curso após normalização: **0**.
- Períodos vazios ou não consecutivos na fonte de dados: **0**.

A auditoria verifica repetição exata, estrutura e presença de referência. Ela **não consegue provar equivalência semântica entre ementas**; assuntos parecidos com títulos distintos precisam de revisão humana e das ementas oficiais.

## Referências e grau de validação

Os campos `instituicao_referencia`, `versao_matriz`, `fonte_oficial` e `status_curricular` acompanham cada registro do catálogo.

- **ENEM — referência oficial:** organização por matérias e tópicos de revisão inspirados nas áreas/competências do INEP. Não utiliza períodos universitários na interface. Os tópicos são roteiros de estudo, não uma transcrição oficial completa de todos os itens possíveis do exame.
- **Odontologia — matriz oficial referenciada:** UFG, matriz ODON-BI-2, ingresso 2023-1. Optativas não estão na grade-base. Os tópicos são guias didáticos e não ementas literais.
- **Medicina — matriz oficial referenciada:** UFG, matriz MED-BI-3, ingresso 2022-1. A matriz tem módulos integrados e estágios; os tópicos didáticos são resumos de estudo.
- **Enfermagem — matriz oficial referenciada:** UFG, matriz ENF-BI-2, ingresso 2017-1. A página da matriz é identificada no código; conferir eventual revisão de PPC antes de equivalência acadêmica.
- **19 cursos — referência institucional parcial:** a fonte institucional/versão está identificada, mas a lista de todos os componentes obrigatórios por período não foi transcrita e conferida integralmente do PPC vigente. Esses cursos aparecem identificados como referências parciais. Não devem ser anunciados como matrizes oficiais integralmente validadas.
- **Marketing — trilha não oficial:** conteúdo formativo independente, expressamente não apresentado como graduação federal ou matriz oficial.

## Política para assuntos de estudo

Os assuntos são roteiros didáticos para organizar o estudo por disciplina. Foram adicionados tópicos específicos para sequências curriculares importantes (por exemplo, Dentística I/II, Diagnóstico Bucal I–IV, Farmacologia I/II, séries clínicas, disciplinas I/II e projetos/TCC). Quando um título de assunto colidia dentro do mesmo curso, o catálogo o contextualiza pela disciplina para evitar uma falsa impressão de cópia literal.

Isso não equivale a afirmar que os assuntos reproduzem as ementas oficiais linha por linha. A fonte oficial da disciplina continua sendo a referência para objetivos, bibliografia e conteúdos obrigatórios.

## Migração dos dados existentes

O `seed_curriculum()` atualiza cursos, disciplinas e tópicos da matriz configurada. Disciplinas antigas ou no período errado são arquivadas em vez de apagadas; assuntos antigos não pertencentes à disciplina ativa também são arquivados. Registros antigos e materiais vinculados são preservados para recuperação. A alteração só chega ao catálogo real quando o backend atualizado é implantado e a migração termina com sucesso.

## Fontes oficiais principais

- ENEM/INEP: https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/matrizes-de-referencia-enem
- Odontologia/UFG — ODON-BI-2, 2023-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/114575212
- Medicina/UFG — MED-BI-3, 2022-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/114161758
- Enfermagem/UFG — ENF-BI-2, 2017-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6311487
- Farmácia/UFG — FARM-BI-2, 2017-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6311434
- Fisioterapia/UFG — FISIO-BI-1, 2022-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/111082559
- Direito/UFG — DIRE-BN-2, 2024-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118130122
- Psicologia/UFG — PSICO-BI-3, 2024-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118142450
- Nutrição/UFG — NUT-BM-3, 2023-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/114711230
- Ciência da Computação/UFG — CICOMP-BI-4, 2024-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/118188393
- Ciências Contábeis/UFG — CICONT-BM-3, 2015-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/2112068
- Sistemas de Informação/UFG — SIINF-BN-2, 2017-1: https://sigaa.sistemas.ufg.br/sigaa/link/public/curso/curriculo/6214319
- Portal UFG de matrizes e ementas: https://prograd.ufg.br/n/16175-ementas-e-matrizes

**Limitação de publicação:** esta revisão remove repetições exatas e fixa as distribuições em uma única fonte, mas não substitui o trabalho de conferência integral de todos os PPCs/ementários. A build completa do frontend também precisa ser executada em um ambiente que consiga instalar as dependências do npm.
