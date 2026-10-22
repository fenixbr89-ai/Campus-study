"""Static validation of the current Campus Study project.
This does not replace a full Vercel build or a live MongoDB/backend smoke test.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BACKEND = SRC / "backend"
PDF_DIR = SRC / "frontend" / "public" / "pdfs" / "disciplinas"
sys.path.insert(0, str(BACKEND))
from curriculum_data import CURRICULA, COURSE_METADATA

def main() -> int:
    errors: list[str] = []
    backend_files = list(BACKEND.rglob("*.py"))
    r = subprocess.run([sys.executable, "-m", "py_compile", *map(str, backend_files)], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        errors.append("Falha na compilação sintática do backend: " + (r.stderr or r.stdout))

    # Parse TypeScript/TSX using the TypeScript compiler API, if available in the environment.
    js_check = r"""
const fs=require('fs'),path=require('path');
let ts; try { ts=require('typescript'); } catch(e) { console.log('TYPESCRIPT_UNAVAILABLE'); process.exit(3); }
const root=process.argv[1]; let bad=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(/\.(ts|tsx)$/.test(e.name)){const opts={target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext};if(e.name.endsWith('.tsx'))opts.jsx=ts.JsxEmit.ReactJSX;const out=ts.transpileModule(fs.readFileSync(p,'utf8'),{compilerOptions:opts,fileName:e.name,reportDiagnostics:true});if((out.diagnostics||[]).length)bad.push(p+': '+(out.diagnostics||[]).map(x=>x.messageText).join('; '));}}}
walk(root); if(bad.length){console.error(bad.join('\n'));process.exit(1)}
"""
    r = subprocess.run(["node", "-e", js_check, str(SRC / "frontend" / "src")], cwd=ROOT, capture_output=True, text=True)
    ts_syntax_checked = r.returncode == 0
    if r.returncode not in (0, 3):
        errors.append("Falha de sintaxe TypeScript/TSX: " + r.stderr.strip())

    try:
        json.loads((SRC / "design_guidelines.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON inválido em src/design_guidelines.json: {exc}")

    rows = json.loads((ROOT / "docs/CATALOGO_DE_ASSUNTOS.json").read_text(encoding="utf-8"))
    courses = len(CURRICULA)
    periods = sum(len(p) for p in CURRICULA.values())
    discipline_pairs = {(r.get("curso"), r.get("periodo"), r.get("disciplina")) for r in rows}
    topics = len(rows)
    if {row.get("curso") for row in rows} != set(CURRICULA):
        errors.append("Catálogo JSON não contém exatamente os cursos da fonte curricular.")
    if set(CURRICULA) != set(COURSE_METADATA):
        errors.append("Há cursos sem metadados de fonte curricular.")
    if PDF_DIR.exists() and list(PDF_DIR.glob("*.pdf")):
        errors.append("O pacote inclui PDFs de disciplinas inesperados.")

    curated = (BACKEND / "curated_resources.py").read_text(encoding="utf-8")
    urls = re.findall(r'"url"\s*:\s*"([^"]+)"', curated)
    for url in urls:
        p = urlparse(url)
        if p.scheme not in {"http", "https"} or not p.netloc:
            errors.append(f"URL externa inválida: {url}")

    ai_text = (BACKEND / "routers" / "ai.py").read_text(encoding="utf-8")
    server_text = (BACKEND / "server.py").read_text(encoding="utf-8")
    if "generate_topic_pack" not in ai_text or "/admin/generate-all" not in ai_text:
        errors.append("Geração automática por IA ausente.")
    if "_ai_generation_worker" not in server_text or "ai_generation_jobs" not in server_text:
        errors.append("Worker de geração automática ausente.")
    if not (BACKEND / "routers" / "payments.py").exists():
        errors.append("Router de pagamentos ausente.")
    for f in list((BACKEND / "routers").glob("*.py")) + list((SRC / "frontend" / "src").rglob("*.tsx")):
        if "paypal" in f.read_text(encoding="utf-8", errors="ignore").lower():
            errors.append(f"Referência PayPal encontrada em: {f.relative_to(ROOT)}")

    audit = subprocess.run([sys.executable, "scripts/audit_curriculum.py"], cwd=ROOT, capture_output=True, text=True)
    if audit.returncode:
        errors.append("Auditoria do catálogo falhou: " + (audit.stdout + audit.stderr))

    print("Campus Study — validação estática final")
    print(f"Cursos: {courses} | Períodos/cursos: {periods} | Pares curso-período-disciplina: {len(discipline_pairs)} | Assuntos cadastrados: {topics}")
    print(f"Recursos externos curados: {len(urls)}")
    print("Python: sintaxe validada")
    print("TypeScript/TSX: sintaxe validada" if ts_syntax_checked else "TypeScript/TSX: não validado — TypeScript não está instalado no ambiente")
    print("Nota: essa validação estática não substitui o build do Vite/TypeScript nem teste de integração em ambiente publicado.")
    if errors:
        print("ERROS:")
        for e in errors: print("-", e)
        return 1
    print("OK: validações estáticas concluídas sem erros.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
