#!/usr/bin/env python3
"""Static curriculum audit for the canonical catalog and its backend copy."""
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_CATALOG = ROOT / "docs" / "CATALOGO_DE_ASSUNTOS.json"
BACKEND_CATALOG = ROOT / "src" / "backend" / "data" / "curriculum_catalog.json"
DOC_SOURCES = ROOT / "docs" / "CURRICULOS_E_FONTES.json"
BACKEND_SOURCES = ROOT / "src" / "backend" / "data" / "curriculum_sources.json"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().casefold()
    return " ".join(value.replace("-", " ").split())


def main() -> int:
    errors: list[str] = []
    try:
        rows = json.loads(DOC_CATALOG.read_text(encoding="utf-8"))
        packaged_rows = json.loads(BACKEND_CATALOG.read_text(encoding="utf-8"))
        sources = json.loads(DOC_SOURCES.read_text(encoding="utf-8"))
        packaged_sources = json.loads(BACKEND_SOURCES.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERRO: arquivo curricular/JSON inválido: {exc}")
        return 1

    if rows != packaged_rows:
        errors.append("O catálogo em docs diverge do catálogo copiado para o backend.")
    if sources != packaged_sources:
        errors.append("Os metadados de fontes divergem entre docs e backend.")

    courses = {r.get("curso") for r in rows}
    known_sources = {s.get("curso") for s in sources}
    if courses != known_sources:
        errors.append(f"Cobertura de fontes incompleta: cursos sem metadados={sorted(courses-known_sources)}; metadados sem curso={sorted(known_sources-courses)}")

    periods: dict[str, set[int]] = defaultdict(set)
    disciplines: dict[tuple[str, str], set[int]] = defaultdict(set)
    topic_periods: dict[tuple[str, str], set[int]] = defaultdict(set)
    topics_per_discipline: dict[tuple[str, int, str], set[str]] = defaultdict(set)
    subjects_per_period: dict[tuple[str, int], set[str]] = defaultdict(set)

    generic_phrases = (
        "principais teorias e metodos", "aplicacoes praticas e analise de casos",
        "conceitos e terminologia", "bases cientificas e terminologia profissional",
        "mecanismos avaliacao e metodos", "revisao critica e resolucao de questoes",
        "fundamentos teoricos e legislacao", "ferramentas de analise e planejamento",
        "decisoes indicadores e legislacao", "fundamentos cientificos e modelos",
        "aplicacoes em casos e pratica supervisionada",
    )
    for r in rows:
        try:
            course = str(r["curso"])
            period = int(r["periodo"])
            discipline = str(r["disciplina"]).strip()
            topic = str(r["assunto"]).strip()
        except Exception:
            errors.append(f"Registro malformado: {r!r}")
            continue
        if not course or not discipline or not topic or period < 1:
            errors.append(f"Valores obrigatórios inválidos: {r!r}")
            continue
        periods[course].add(period)
        disciplines[(course, norm(discipline))].add(period)
        topic_periods[(course, norm(topic))].add(period)
        topics_per_discipline[(course, period, discipline)].add(norm(topic))
        subjects_per_period[(course, period)].add(norm(discipline))
        if any(phrase in norm(topic) for phrase in generic_phrases):
            errors.append(f"Assunto genérico não curado: {course} / {discipline} / {topic}")

    duplicate_subjects = [(course, discipline, sorted(ps)) for (course, discipline), ps in disciplines.items() if len(ps) > 1]
    for course, discipline, ps in duplicate_subjects:
        errors.append(f"Disciplina repetida entre períodos: {course} / {discipline} / {ps}")

    duplicate_topics = [(course, topic, sorted(ps)) for (course, topic), ps in topic_periods.items() if len(ps) > 1]
    for course, topic, ps in duplicate_topics:
        errors.append(f"Assunto exato repetido entre períodos: {course} / {topic} / {ps}")

    for course, nums in periods.items():
        if course == "ENEM":
            if nums != {1}:
                errors.append(f"ENEM deve ficar em uma categoria técnica única, sem períodos universitários; encontrados {sorted(nums)}")
            continue
        if nums != set(range(1, max(nums) + 1)):
            errors.append(f"Sequência de períodos incompleta em {course}: {sorted(nums)}")

    for course, source in {s["curso"]: s for s in sources}.items():
        if not source.get("url_fonte", "").startswith("https://"):
            errors.append(f"Fonte sem URL HTTPS para {course}")
        if not source.get("status_validacao"):
            errors.append(f"Status de verificação ausente para {course}")

    topic_total = len(rows)
    discipline_period_total = len(topics_per_discipline)
    print("Campus Study — auditoria estática do catálogo")
    print(f"Cursos: {len(courses)} | Disciplinas/curso/período: {discipline_period_total} | Assuntos: {topic_total}")
    print(f"Duplicatas exatas de disciplina entre períodos: {len(duplicate_subjects)}")
    print(f"Duplicatas exatas de assuntos entre períodos: {len(duplicate_topics)}")
    print(f"Cursos com metadados de fontes: {len(known_sources)}")
    if errors:
        print("ERROS:")
        for error in errors[:100]:
            print("-", error)
        if len(errors) > 100:
            print(f"... e mais {len(errors) - 100} erros")
        return 1
    print("OK: catálogo e pacote do backend consistentes, sem duplicatas exatas e sem placeholders genéricos antigos.")
    print("Nota: esta auditoria técnica não comprova que cada matriz corresponda integralmente ao PPC oficial; consulte CURRICULOS_E_FONTES.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
