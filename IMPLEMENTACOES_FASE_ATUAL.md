# Campus Study — motor automático da biblioteca

## Implementado
- Endpoint persistente para iniciar o preenchimento de todo o catálogo: `/admin/resources/sync-all/start`.
- O processamento roda em segundo plano no backend após o administrador iniciar a operação.
- O job é persistido em `resource_sync_jobs`, com status, total, processados, recursos publicados, erros e último assunto.
- Endpoint de acompanhamento: `/admin/resources/sync-status`.
- Endpoint de nova execução/recuperação: `/admin/resources/sync-all/resume`.
- A publicação é idempotente: URLs já existentes no mesmo assunto não são duplicadas.
- Para cada assunto, o motor tenta pesquisar separadamente PDFs, vídeos, artigos, resumos e mapas em português.
- O motor preserva materiais existentes.
- A tela administrativa agora mostra barra de progresso, quantidade processada, recursos publicados e erros.

## Importante
- A busca externa continua sujeita à disponibilidade das fontes e aos limites dos sites.
- O motor não inventa URLs nem copia PDFs protegidos; guarda o link para a fonte original.
- O processamento pode ser retomado/reexecutado sem duplicar URLs já cadastradas.
- Mapas mentais e simulados gerados por IA continuam disponíveis nas ferramentas do Campus AI; esta fase automatiza principalmente a curadoria e publicação de recursos externos.

## Modelo Free/Premium — fase de teste
- Todos os novos cadastros recebem 30 dias de acesso completo grátis.
- Contas antigas sem `trial_started_at` recebem um período de 30 dias iniciado no primeiro login após esta versão.
- Após o trial, o plano Free mantém cursos, períodos, disciplinas, videoaulas, PDFs, livros, resumos e flashcards; Questões e Simulados ficam disponíveis apenas conforme a configuração Premium do administrador.
- Após o trial, simulados, mapas mentais e artigos científicos exigem Premium.
- Premium mensal: R$ 19,90.
- Premium anual: R$ 150,00.
- A cobrança usa Stripe Checkout/Billing e o acesso Premium é sincronizado por webhooks; as chaves e preços são configurados pelo administrador.
- O administrador pode conceder acesso Premium temporário pela estrutura existente de `access_grants` usando o recurso `plataforma`, `premium` ou `todos`.
