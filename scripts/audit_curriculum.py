#!/usr/bin/env python3
"""Validate the static curriculum catalog against its single source of truth."""
import json
import re
import sys
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from curriculum_data import CURRICULA, COURSE_METADATA

rows = json.loads((ROOT / "docs/CATALOGO_DE_ASSUNTOS.json").read_text(encoding="utf-8"))

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().casefold()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", value).split())

errors = []
subjects_by_course = defaultdict(set)
subject_periods = defaultdict(set)
topic_periods = defaultdict(set)
course_periods = defaultdict(set)
metadata_by_course = {}
for course, meta in COURSE_METADATA.items():
    metadata_by_course[course] = meta
for row in rows:
    course = row.get("curso", "")
    period = int(row.get("periodo", 0))
    subject = row.get("disciplina", "")
    topic = row.get("assunto", "")
    if not all([course, period > 0, subject, topic, row.get("fonte_oficial"), row.get("status_curricular")]):
        errors.append(f"Registro incompleto: {row}")
    course_periods[course].add(period)
    subjects_by_course[course].add(normalize(subject))
    subject_periods[(course, normalize(subject))].add(period)
    topic_periods[(course, normalize(topic))].add(period)

subject_duplicates = [(course, subject, sorted(periods)) for (course, subject), periods in subject_periods.items() if len(periods) > 1]
topic_duplicates = [(course, topic, sorted(periods)) for (course, topic), periods in topic_periods.items() if len(periods) > 1]
if subject_duplicates:
    errors.extend([f"Disciplina repetida: {c} — {s} — períodos {p}" for c, s, p in subject_duplicates])
if topic_duplicates:
    errors.extend([f"Assunto repetido: {c} — {t} — períodos {p}" for c, t, p in topic_duplicates])
if set(CURRICULA) != set(COURSE_METADATA):
    errors.append("Cada curso precisa ter uma fonte/metadados curriculares.")
if {r.get("curso") for r in rows} != set(CURRICULA):
    errors.append("Catálogo JSON e fonte curricular não contêm o mesmo conjunto de cursos.")
for course, periods in CURRICULA.items():
    expected_periods = set(range(1, max(periods) + 1))
    if set(periods) != expected_periods:
        errors.append(f"Períodos não consecutivos: {course}: {sorted(periods)}")
    for period, subjects in periods.items():
        if len(subjects) != len(set(map(normalize, subjects))):
            errors.append(f"Disciplina duplicada no mesmo período: {course}, período {period}")
if course_periods.get("ENEM") != {1}:
    errors.append(f"ENEM deve permanecer em um único bloco, sem períodos universitários: {course_periods.get('ENEM')}")
if errors:
    print("FALHA NA AUDITORIA CURRICULAR")
    for err in errors[:100]: print("-", err)
    raise SystemExit(1)

statuses = Counter(meta["status"] for meta in COURSE_METADATA.values())
discipline_count = sum(len(subjects) for subjects in subjects_by_course.values())
topic_count = len(rows)
print("AUDITORIA ESTRUTURAL APROVADA")
print(f"Cursos: {len(CURRICULA)} | Disciplinas: {discipline_count} | Assuntos: {topic_count}")
print(f"Duplicatas de disciplinas entre períodos: {len(subject_duplicates)}")
print(f"Títulos de assuntos repetidos entre períodos: {len(topic_duplicates)}")
print("Status das grades:")
for status, count in sorted(statuses.items()): print(f"  {status}: {count}")
print("NOTA: aprovação estrutural não equivale à validação integral de todas as ementas oficiais.")
