# CAMPUS STUDY — V1.4 CONSOLIDADA

## Alterações consolidadas

### Corrigido
- Exclusão de provas/planos com invalidação de caches e remoção dos registros relacionados.
- Ranking mensal baseado nos minutos reais registrados em `daily_stats`.
- Ranking com atualização a cada 5 segundos e atualização ao voltar para a janela.
- Campos numéricos editáveis sem o zero reaparecer enquanto o usuário apaga e digita.
- Biblioteca automática usando contexto Curso → Período → Disciplina → Assunto.
- Biblioteca com status, erros e preservação dos resultados já salvos.
- Geração automática verificando configuração da IA antes de iniciar.
- Proteção contra filas duplicadas de geração.
- Notificações baseadas em provas, tarefas, revisões, metas e tempo de estudo.

### Removido da interface
- Geração em lote em Admin → Configurações.
- Geração automática de conteúdo em Admin → Configurações.
- Campus IA da interface principal do estudante.

### Preservado
- Infraestrutura/backend do Campus IA.
- Integração Gemini.
- Simulados.
- Mapas mentais.
- Resumos.
- Anotações.
- Plano de estudos.
- Ranking.
- Cursos.
- Perfil.
- Progresso.
- Calendário.
- Revisões.
- Metas semanais.
- Autenticação e banco de dados.

### Deploy
- `vercel.json` aponta o build para `src/frontend/dist`.
- `/api/:path*` é encaminhado ao backend Render configurado no projeto.
- O fallback SPA aponta para `/index.html`.

## Validação realizada
- Backend Python: `compileall` concluído sem erros.
- Referências de Campus IA na interface principal: removidas; o arquivo `CampusAI.tsx` e a infraestrutura backend foram preservados.
- ZIP final: estrutura validada após empacotamento.

## Observação sobre build frontend
O build completo do frontend não foi certificado nesta execução porque a instalação das dependências (`npm install`) excedeu o limite de execução do ambiente. Isso não é tratado como erro de código; a validação Python e as verificações estáticas foram concluídas.
