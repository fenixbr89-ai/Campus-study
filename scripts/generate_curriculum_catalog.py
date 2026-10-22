#!/usr/bin/env python3
"""Regenerate static study catalog from backend's single curriculum source."""
import ast, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'src' / 'backend'
sys.path.insert(0, str(BACKEND))
from curriculum_data import CURRICULA, COURSE_METADATA, study_topics, make_topic_titles_unique

# Keep the INEP-specific topic list curated in seed.py.
seed_tree = ast.parse((BACKEND / 'seed.py').read_text(encoding='utf-8'))
enem_topic_map = {}
for node in seed_tree.body:
    targets = node.targets if isinstance(node, ast.Assign) else ([node.target] if isinstance(node, ast.AnnAssign) else [])
    if any(isinstance(t, ast.Name) and t.id == 'ENEM_TOPIC_MAP' for t in targets):
        enem_topic_map = ast.literal_eval(node.value)
        break
if not enem_topic_map:
    raise SystemExit('ENEM_TOPIC_MAP não foi encontrada no seed.py')
rows = []
for course, periods in CURRICULA.items():
    meta = COURSE_METADATA[course]
    raw_topics = {}
    for period, disciplines in periods.items():
        raw_topics[period] = {}
        for discipline in disciplines:
            topics = enem_topic_map.get(discipline, []) if course == 'ENEM' else []
            if not topics:
                topics = study_topics(course, discipline, period)
            raw_topics[period][discipline] = list(dict.fromkeys(topics))
    finalized_topics = make_topic_titles_unique(raw_topics)
    for period, disciplines in finalized_topics.items():
        for discipline, topics in disciplines.items():
            for topic in topics:
                rows.append({
                    'curso': course,
                    'periodo': int(period),
                    'disciplina': discipline,
                    'assunto': topic,
                    'instituicao_referencia': meta['institution'],
                    'versao_matriz': meta['version'],
                    'fonte_oficial': meta['url'],
                    'status_curricular': meta['status'],
                })
(ROOT / 'docs' / 'CATALOGO_DE_ASSUNTOS.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'{len(rows)} registros; {len(CURRICULA)} cursos; fontes em {len(COURSE_METADATA)} cursos')
