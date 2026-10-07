"""Offline validation for Prompt 2 student experience changes.
Does not require MongoDB, npm packages, credentials or network access.
"""
from pathlib import Path
import ast, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
errors=[]

for p in (ROOT/'src/backend').rglob('*.py'):
    try: ast.parse(p.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f"Python inválido: {p}: {exc}")

manifest = ROOT/'src/frontend/public/manifest.webmanifest'
try:
    data=json.loads(manifest.read_text(encoding='utf-8'))
    for key in ('name','short_name','start_url','display','icons','lang'):
        if key not in data: errors.append(f"Manifest sem {key}")
    if data.get('display') != 'standalone': errors.append('Manifest não usa standalone')
except Exception as exc: errors.append(f'Manifest inválido: {exc}')

sw=(ROOT/'src/frontend/public/sw.js').read_text(encoding='utf-8')
for token in ('campus-study-shell-v2','/api/','skipWaiting','clients.claim'):
    if token not in sw: errors.append(f'Service Worker sem requisito: {token}')

study=(ROOT/'src/backend/routers/study.py').read_text(encoding='utf-8')
if 'user_achievements' not in (ROOT/'src/backend/lib/db.py').read_text(encoding='utf-8'):
    errors.append('Persistência de conquistas ausente.')

for route in ('/academic-dashboard','/academic-performance','/question-reviews','/topic-favorites'):
    if route not in study: errors.append(f'Rota ausente: {route}')

app=(ROOT/'src/frontend/src/App.tsx').read_text(encoding='utf-8')
for route in ('/revisao','/progresso','/biblioteca'):
    if route not in app: errors.append(f'Rota frontend ausente: {route}')

for token in ('<Route path="/status" element={<StatusPage />} />', '<Route path="/suporte" element={auth(<SupportPage />)} />'):
    if token not in app: errors.append(f'Rota frontend ausente: {token}')

student=(ROOT/'src/frontend/src/pages/StudentTools.tsx').read_text(encoding='utf-8')
for token in ('QuestionReviewPage','Pesquisa avançada','Todos os tipos'):
    if token not in student: errors.append(f'Experiência estudante ausente: {token}')

app_layout=(ROOT/'src/frontend/src/components/AppLayout.tsx').read_text(encoding='utf-8')
if app_layout.count('/study-sessions/${session.id}/heartbeat') != 1:
    errors.append('Heartbeat de estudo deve ocorrer exatamente uma vez por ciclo.')
if 'event_kind' not in (ROOT/'src/backend/routers/study.py').read_text(encoding='utf-8'):
    errors.append('Sessão de estudo não registra contexto de atividade.')
manifest_data = data if isinstance(data, dict) else {}
if manifest_data.get('start_url') != '/inicio':
    errors.append('Manifest deve abrir o app em /inicio.')
root_package=json.loads((ROOT/'package.json').read_text(encoding='utf-8'))
if 'npm --prefix src/frontend ci' not in root_package.get('scripts',{}).get('build',''):
    errors.append('Build raiz deve usar npm ci no frontend.')

home=(ROOT/'src/frontend/src/pages/Home.tsx').read_text(encoding='utf-8')
for token in ('academic-dashboard','Visão acadêmica','Por quê:'):
    if token not in home: errors.append(f'Dashboard acadêmico incompleto: {token}')

if errors:
    print('\n'.join(errors)); sys.exit(1)
print('STUDENT_EXPERIENCE_STATIC_OK')
