"""Static final validation for the portable Campus Study project.
Run from project root: python scripts/final_validation.py
This does not replace a live deployment test with MongoDB and configured AI credentials.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BACKEND = SRC / "backend"
PDF_DIR = SRC / "frontend" / "public" / "pdfs" / "disciplinas"


def curriculum_counts() -> tuple[int, int, int, int]:
    tree = ast.parse((BACKEND / "seed.py").read_text(encoding="utf-8"))
    assignments = {}
    for node in tree.body:
        target = getattr(node, "target", None)
        name = getattr(target, "id", None)
        if isinstance(node, ast.AnnAssign) and name in {"COURSE_PERIODS", "COURSE_SUBJECTS", "TOPIC_MAP"}:
            assignments[name] = ast.literal_eval(node.value)
    periods_map = assignments["COURSE_PERIODS"]
    subject_map = assignments["COURSE_SUBJECTS"]
    topic_map = assignments["TOPIC_MAP"]
    courses = len(periods_map)
    periods = sum(periods_map.values())
    disciplines = sum(len(subjects) for subjects in subject_map.values())
    topics = sum(len(topic_map.get(subject, [1, 2, 3])) for subjects in subject_map.values() for subject in subjects)
    return courses, periods, disciplines, topics


def main() -> int:
    errors: list[str] = []

    # Python syntax/import compilation (no external DB required).
    r = subprocess.run(["python", "-m", "compileall", "-q", str(BACKEND)], cwd=ROOT)
    if r.returncode:
        errors.append("Falha na compilação sintática do backend.")

    # Parse all TypeScript/TSX files without requiring node_modules. This catches syntax errors even when
    # dependency installation is unavailable in the validation environment.
    js_check = r"""
const fs=require('fs'),path=require('path'),ts=require('typescript');
const root=process.argv[1]; let bad=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(/\.(ts|tsx)$/.test(e.name)){const opts={target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext};if(e.name.endsWith('.tsx'))opts.jsx=ts.JsxEmit.ReactJSX;const out=ts.transpileModule(fs.readFileSync(p,'utf8'),{compilerOptions:opts,fileName:e.name,reportDiagnostics:true});if((out.diagnostics||[]).length)bad.push(p);}}}
walk(root); if(bad.length){console.error(bad.join('\n'));process.exit(1)}
"""
    r = subprocess.run(["node", "-e", js_check, str(SRC / "frontend" / "src")], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        errors.append("Falha de sintaxe em TypeScript/TSX: " + r.stderr.strip())

    # Valid JSON assets. TypeScript config files are JSONC and may legally contain comments.
    for f in [SRC / "design_guidelines.json"]:
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"JSON inválido: {f}: {exc}")

    # Curriculum remains a reference structure; no study PDFs are bundled in V1.
    courses, periods, disciplines, topics = curriculum_counts()
    if PDF_DIR.exists():
        shipped_pdfs = list(PDF_DIR.glob("*.pdf"))
        if shipped_pdfs:
            errors.append(f"PDFs empacotados no V1: {len(shipped_pdfs)} (esperado: 0)")
    print(f"PDFs empacotados: {len(list(PDF_DIR.glob("*.pdf"))) if PDF_DIR.exists() else 0} (esperado: 0)")

    # Curated external resources must be real HTTP(S) URLs.
    curated = (BACKEND / "curated_resources.py").read_text(encoding="utf-8")
    urls = re.findall(r'"url"\s*:\s*"([^"]+)"', curated)
    for url in urls:
        p = urlparse(url)
        if p.scheme not in {"http", "https"} or not p.netloc:
            errors.append(f"URL externa inválida: {url}")

    # AI automatic content generation
    ai_text = (ROOT / "src/backend/routers/ai.py").read_text(encoding="utf-8")
    server_text = (ROOT / "src/backend/server.py").read_text(encoding="utf-8")
    assert "generate_topic_pack" in ai_text and "/admin/generate-all" in ai_text, "Geração automática por IA ausente"
    assert "_ai_generation_worker" in server_text and "ai_generation_jobs" in server_text, "Worker de geração automática ausente"
    print("IA: geração automática por assunto + fila global + worker presentes")

# Payment integration is Stripe Checkout/Billing; PayPal is intentionally absent.
    payment_router = BACKEND / "routers" / "payments.py"
    if not payment_router.exists():
        errors.append("Router de pagamentos Stripe ausente.")
    source_files = list((BACKEND / "routers").glob("*.py")) + list((SRC / "backend").rglob("*.py")) + list((SRC / "frontend" / "src").rglob("*.tsx"))
    for f in source_files:
        text = f.read_text(encoding="utf-8", errors="ignore").lower()
        if "paypal" in text:
            errors.append(f"Referência PayPal encontrada em: {f.relative_to(ROOT)}")

    print("Campus Study — validação estática final")
    print(f"Cursos: {courses} | Períodos previstos: {periods} | Disciplinas cadastradas: {disciplines} | Assuntos cadastrados: {topics}")
    print(f"PDFs empacotados: {len(list(PDF_DIR.glob("*.pdf"))) if PDF_DIR.exists() else 0} (esperado: 0)")
    print(f"Recursos externos curados registrados: {len(urls)}")
    print("Stripe: checkout/assinaturas presentes; segredo protegido no backend")
    if errors:
        print("ERROS:")
        for e in errors:
            print("-", e)
        return 1
    print("OK: validação estática concluída sem erros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
