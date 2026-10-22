# Campus Study — Living Spec

## What it is
University study platform (pt-BR) for Brazilian undergrads: video lessons, scientific
articles, summaries, questions, flashcards, mind maps, and "Campus AI" (LLM chat),
organized by course → period → discipline → topic. Acesso gratuito a todas as funcionalidades, sem planos pagos.

## Stack
- backend/ FastAPI + motor (Mongo `campus_study`), routes all on `api_router` (/api) in
  server.py incl. routers: auth, admin, catalog, study, ai. JWT httpOnly-cookie sessions,
  CPF-based identity (hash+pepper). `python seed.py` seeds admin + 23 courses + content.
- frontend/ Vite + React 19 + TS strict, TanStack Query, routes in src/App.tsx.
  Landing/auth at /, /entrar, /criar-conta; app shell (AppLayout) at /inicio, /cursos,
  /campus-ai, /simulados, /flashcards, /mapas-mentais, /biblioteca, /progresso, /perfil,
  /admin; legal at /termos-de-uso, /politica-de-privacidade.

## Roles
- Admin: full content CRUD via /admin. Seed: see memory/test_credentials.md.
- Student: free forever plan; register with CPF + email + password.

## Footer / identity (2026-09 update)
- Landing hero badge (Auth.tsx, data-testid="access-quote"):
  “A educação é a arma mais poderosa que você pode usar para mudar o mundo.” — Nelson Mandela
  (replaced "A Netflix dos materiais universitários" — no Netflix references remain anywhere).
- Footer credit block (Brand.tsx `FooterCredit`, data-testid="footer-credit"), rendered by
  the shared `Footer` (AppLayout + Legal) and on the landing page bottom, centered:
  App criado em 2026 / CEO E FUNDADOR / @Kayke_henrique1 → https://www.instagram.com/kayke_henrique1
  (external link, target=_blank). Mobile keeps pb-28 above the fixed bottom nav (no overlap);
  desktop bottom padding is 20px so the block sits ~16–20px from the page edge.

## Notes
- The delivered zip ships src/lib/*.ts and vite.config.ts RESTORED (the uploaded
  campus-study-complete.zip had them renamed as .trashed-* — app could not build).
- Backend deps added to venv: pypdf (already in requirements.txt).