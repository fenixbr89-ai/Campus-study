# Campus Study V1 — colocar no ar

Este pacote foi preparado para rodar sem dependência de plataformas externas.

## O que você precisa

- Um servidor Linux/VPS com Docker e Docker Compose.
- Um domínio apontando para o servidor (opcional no primeiro teste).
- Uma `GEMINI_API_KEY` se quiser usar o Campus AI.

## 1. Preparar a configuração

Na pasta do projeto:

```bash
python3 scripts/prepare_production.py
```

O script gera automaticamente `JWT_SECRET` e `CPF_PEPPER`, cria uma senha inicial forte se você não informar uma, e pede somente os dados necessários do primeiro SUPERADMIN.

## 2. Subir o sistema

```bash
docker compose up -d --build
```

O site ficará disponível na porta 80 do servidor.

## 3. Criar o primeiro administrador

Depois que o MongoDB estiver saudável:

```bash
docker compose exec backend python seed.py
```

Use o CPF e a senha definidos durante a preparação.

## 4. HTTPS e domínio

Para produção pública, coloque HTTPS na frente do serviço (por exemplo, com Caddy, Nginx Proxy Manager ou um proxy da própria hospedagem) e altere `CORS_ORIGINS` para o domínio HTTPS.

## 5. Importante

- Não publique `src/backend/.env`.
- Não coloque a chave Gemini no frontend.
- O MongoDB não é exposto diretamente à internet pelo `docker-compose.yml`.
- Faça backup do volume `campus_mongo` antes de qualquer manutenção destrutiva.


## Frontend no Vercel

O projeto inclui `vercel.json` para encaminhar `/api/*` ao backend do Render. Isso mantém as chamadas da API no mesmo domínio do frontend e permite que a sessão por cookie funcione corretamente.
