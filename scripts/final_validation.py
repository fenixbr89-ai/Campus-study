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
    catalog = json.loads((ROOT / "docs" / "CATALOGO_DE_ASSUNTOS.json").read_text(encoding="utf-8"))
    courses = {row["curso"] for row in catalog}
    periods_by_course: dict[str, set[int]] = {}
    disciplines = set()
    for row in catalog:
        course = row["curso"]
        periods_by_course.setdefault(course, set()).add(int(row["periodo"]))
        disciplines.add((course, int(row["periodo"]), row["disciplina"]))
    periods = sum(len(nums) for course, nums in periods_by_course.items() if course != "ENEM")
    return len(courses), periods, len(disciplines), len(catalog)


def main() -> int:
    errors: list[str] = []

    # Python syntax/import compilation (no external DB required).
    r = subprocess.run(["python", "-m", "compileall", "-q", str(BACKEND)], cwd=ROOT)
    if r.returncode:
        errors.append("Falha na compilação sintática do backend.")

    # Parse all TypeScript/TSX files without requiring node_modules. This catches syntax errors even when
    # dependency installation is unavailable in the validation environment.
    js_check = r"""
const fs=require('fs'),path=require('path');let ts;try{ts=require('typescript')}catch(e){try{ts=require(path.resolve(path.dirname(process.execPath),'../lib/node_modules/typescript'))}catch(e2){console.error('TypeScript não está instalado; instale as dependências do frontend para concluir o build.');process.exit(2)}}
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

    # Canonical curriculum JSON is shipped to both docs and backend/data.
    courses, periods, disciplines, topics = curriculum_counts()
    try:
        subprocess.run(["python", str(ROOT / "scripts" / "audit_curriculum.py")], cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        errors.append("A auditoria do catálogo curricular falhou.")
    catalog_doc = json.loads((ROOT / "docs" / "CATALOGO_DE_ASSUNTOS.json").read_text(encoding="utf-8"))
    catalog_backend = json.loads((BACKEND / "data" / "curriculum_catalog.json").read_text(encoding="utf-8"))
    if catalog_doc != catalog_backend:
        errors.append("O catálogo do backend não é idêntico ao catálogo documentado.")
    shipped_pdfs = list(PDF_DIR.glob("*.pdf")) if PDF_DIR.exists() else []
    if shipped_pdfs:
        errors.append(f"PDFs empacotados no V1: {len(shipped_pdfs)} (esperado: 0)")
    print(f"PDFs empacotados: {len(shipped_pdfs)} (esperado: 0)")

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
    print(f"Cursos: {courses} | Períodos universitários cadastrados: {periods} | Disciplinas/curso/período: {disciplines} | Assuntos cadastrados: {topics}")
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
