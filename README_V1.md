# Campus Study V1 — independente

Esta versão foi preparada para rodar sem serviços de construção/edição específicos de plataformas de IA.

## O que mudou

## Controle de assinatura e acesso

- Todo novo cadastro recebe 30 dias de acesso completo gratuito, contados a partir da criação da conta.
- O período gratuito é controlado pelo backend, não apenas pela interface.
- Depois do término dos 30 dias, sem assinatura Premium ativa, a conta passa automaticamente para as regras do Free.
- Assinaturas Premium são confirmadas pelo Stripe via webhook.
- Se uma renovação falhar, o Stripe pode manter a assinatura em `past_due` durante as tentativas de cobrança; depois que a assinatura perde o acesso Premium, o backend deixa de concedê-lo e a conta volta ao Free.
- Quando uma cobrança volta a ser paga e a assinatura retorna a `active`, o webhook atualiza novamente o acesso Premium.
- Se a assinatura for cancelada de forma definitiva, o acesso Premium é revogado.


- Frontend React/Vite sem pacotes de plataforma externa.
- Backend FastAPI sem integrações específicas de plataforma.
- Campus AI usa API real de Gemini ou OpenAI diretamente pelo backend.
- E-mail de recuperação usa Resend ou SMTP configurado pelo administrador.
- Login administrativo alinhado para CPF + senha.
- Endpoint `/api/health` para monitoramento.
- Dockerfiles e `docker-compose.yml` para hospedagem.
- Nenhum PDF/material antigo é empacotado.
- O checkout Stripe é configurável pelo Admin; a chave secreta fica apenas no backend e as assinaturas Premium são confirmadas por webhook.

## Antes de colocar no ar

1. Copie `src/backend/.env.example` para `src/backend/.env`.
2. Gere valores fortes e únicos para `JWT_SECRET` e `CPF_PEPPER`.
3. Configure `MONGO_URL` e `DB_NAME`.
4. Configure `GEMINI_API_KEY` e mantenha `AI_PROVIDER=gemini` para usar o Gemini.
5. Configure um provedor de e-mail (`resend` ou `smtp`) se quiser recuperação de senha por e-mail.
6. Preencha `ADMIN_CPF`, `ADMIN_EMAIL` e `ADMIN_PASSWORD` para criar o primeiro administrador.
7. Execute o seed uma vez para criar a estrutura acadêmica e o administrador.

## Docker

Na pasta raiz:

```bash
docker compose build
docker compose up -d
```

Depois, inicialize o catálogo:

```bash
docker compose exec backend python seed.py
```

O site ficará no endereço do servidor na porta 80 e o backend será acessível internamente pelo frontend.

## Desenvolvimento sem Docker

Backend:

```bash
cd src/backend
python -m venv .venv
# ative a venv
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Frontend:

```bash
cd src/frontend
npm install
npm run dev
```

O Vite já está configurado para encaminhar `/api` para `localhost:8001`.

## Importante sobre a IA

A chave do Gemini fica somente no backend. Nunca coloque `GEMINI_API_KEY` no frontend ou no APK.

## Importante sobre produção

O `docker-compose.yml` é uma base de implantação. Para um domínio público, use HTTPS e configure `COOKIE_SECURE=true`. Não publique o arquivo `.env` nem as chaves de API.

## Validação

Execute na raiz:

```bash
python scripts/final_validation.py
```

A validação estática não substitui um teste real com MongoDB e chaves de API configuradas.


## Pagamentos Stripe

O projeto usa Stripe Checkout em modo de assinatura mensal/anual. A configuração é feita em Administração → Pagamentos: publique a chave pública, a chave secreta, os Price IDs mensal/anual e o segredo do webhook. O segredo é armazenado criptografado no backend e não é enviado ao frontend.

O webhook deve apontar para `/api/payments/stripe/webhook` no endereço público do backend. O Campus Study mantém a autenticação do usuário separada do processamento do pagamento; o acesso Premium só é concedido quando a assinatura é confirmada pelo webhook.

## Conteúdo manual pelo Admin

Em Administração → Conteúdos, o administrador pode cadastrar videoaulas por URL, PDFs por URL ou fazer upload de PDF de até 20 MB, além de resumos, questões, mapas, artigos, livros e materiais com links. O upload de PDF usa GridFS no MongoDB para não depender do disco efêmero do servidor.

## Publicação

O `package.json` na raiz permite que o Vercel execute o build do frontend em `src/frontend`. O `vercel.json` mantém `/api/*` apontando para o backend Render configurado no projeto e também faz fallback das rotas do React para `index.html`. Se o backend for hospedado em outro endereço, altere apenas o destino `/api/:path*` no `vercel.json`.

## Geração automática de conteúdo por IA — V1

A V1 inclui um motor de geração automática baseado no Gemini 3.8 Flash. Ele pode pesquisar fontes públicas na web, gerar material didático original e questões e armazenar esses conteúdos por assunto.

- O estudante não precisa cadastrar conteúdo manualmente para cada assunto.
- Ao abrir um assunto e acessar Materiais, o sistema pode gerar o pacote automaticamente quando ainda não existir.
- Simulados Premium podem ser gerados por assunto, disciplina ou curso. Se não houver questões suficientes, o backend gera e armazena um banco automaticamente antes de montar o simulado.
- O Admin possui uma ação para enfileirar a geração de todo o catálogo. O worker do backend processa os 2.371 assuntos de forma independente, retomando os itens pendentes após reinício do servidor.
- A pesquisa usa Google Search grounding para fundamentar a geração em fontes encontradas na web. Fontes retornadas são registradas junto ao conteúdo quando possível.
- Conteúdo gerado é original; o sistema não baixa nem reproduz livros/apostilas protegidos por direitos autorais.

A chave `GEMINI_API_KEY` permanece somente no backend. O modelo pode ser alterado por `GEMINI_MODEL`.
Para recursos multimodais, configure também `GEMINI_IMAGE_MODEL` (geração de imagens), `AI_REQUEST_TIMEOUT` e `AI_MAX_RETRIES`.
A Campus IA aceita imagens, PDF, TXT e DOCX no endpoint de anexos; arquivos são validados no backend e a chave nunca é enviada ao navegador.
Voz de entrada e leitura da resposta usam as APIs de voz do navegador; a integração Live não é necessária para o fluxo básico.
