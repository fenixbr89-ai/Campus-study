# Campus Study — validação e correções finais

## Correções concluídas nesta fase
- Identidade visual corrigida: fundo padrão do aplicativo e da área administrativa em verde claro/verde, sem o fundo escuro usado no mockup anterior.
- Área administrativa continua protegida por autorização no backend e agora também fica claramente acessível na navegação inferior quando o usuário autenticado é administrador.
- Motor de preenchimento automático da biblioteca ganhou **pausar, retomar e cancelar** reais.
- O estado da sincronização é persistido no banco por assunto (`processed_topic_ids`), evitando perder o progresso quando o processo é retomado.
- Se o backend reiniciar durante uma sincronização, o job é marcado como pausado para recuperação administrativa, em vez de permanecer falsamente como "em execução".
- Publicação manual de recursos externos exige URL HTTP/HTTPS e validação automática (`verified=true`); recursos não validados não são publicados pela tela de curadoria.
- Recursos externos publicados pelo motor registram fonte, idioma, acesso aberto quando identificado, verificação e data da verificação.
- A busca continua apontando para a fonte original; o sistema não copia/republica PDFs protegidos.
- O projeto não contém checkout, Stripe, assinatura ou cobrança de plataforma.
- `design_guidelines.json` foi corrigido e alinhado à identidade verde e às regras atuais do projeto.
- Foi incluído `scripts/final_validation.py` para repetir a validação estática antes de novas versões.

## Validação executada
- Backend Python: compilação sintática sem erros.
- TypeScript/TSX: análise de sintaxe de todos os arquivos sem erros, mesmo sem instalar `node_modules`.
- JSON de design: válido.
- 23 cursos.
- 212 períodos previstos pela estrutura de referência.
- 90 disciplinas cadastradas no currículo atual.
- 125 assuntos cadastrados no currículo atual.
- 90 PDFs internos correspondentes às 90 disciplinas: presentes e legíveis.
- 18 recursos externos curados registrados com URLs HTTP/HTTPS.
- Nenhuma implementação de pagamento/checkout encontrada no código de aplicação.

## Limitação da validação local
O ambiente de auditoria não possui uma instância MongoDB nem as dependências de `node_modules` instaladas, e não conseguiu resolver DNS para testes externos diretos. Portanto, esta versão foi validada estaticamente e por inspeção do código/arquivos. O teste final de ponta a ponta deve ser executado no ambiente de deploy com MongoDB e variáveis de ambiente configuradas.

## Regra importante sobre o catálogo
O currículo atual é uma **grade de referência**: são 23 cursos, 212 períodos previstos, 90 disciplinas e 125 assuntos explicitamente cadastrados no seed. Os demais períodos existem como estrutura, mas não devem ser apresentados como se tivessem disciplinas oficiais universais. Grades reais variam por instituição.

## Alteração final — biblioteca limpa
- Mantida toda a estrutura de cursos, períodos, disciplinas e assuntos.
- Removidos do seed todos os PDFs, resumos, questões, flashcards, mapas e recursos externos pré-publicados.
- A biblioteca inicia sem materiais e passa a ser preenchida manualmente ou pela IA administrativa após revisão.
- Para uma base MongoDB que já possua materiais antigos, executar uma única vez `python scripts/clear_study_contents.py`.
