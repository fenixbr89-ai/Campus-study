import asyncio
import base64
import io
import json
import os
import re

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from lib.auth import current_user, require_feature_access, admin_user
from lib.content import topic_context, youtube_id
from lib.db import db
from lib.security import now_utc


router = APIRouter(prefix="/ai", tags=["AI"])


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.8-flash",
).strip()
GEMINI_FALLBACK_MODEL = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-3.7-flash").strip()
GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image").strip()
AI_REQUEST_TIMEOUT = float(os.environ.get("AI_REQUEST_TIMEOUT", "18"))
AI_MAX_RETRIES = max(1, min(int(os.environ.get("AI_MAX_RETRIES", "1")), 2))
AI_MAX_OUTPUT_TOKENS = max(256, min(int(os.environ.get("AI_MAX_OUTPUT_TOKENS", "768")), 2048))
GEMINI_HTTP_CLIENT = httpx.AsyncClient(
    timeout=AI_REQUEST_TIMEOUT,
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10, keepalive_expiry=30),
)


@router.on_event("shutdown")
async def _close_gemini_client():
    await GEMINI_HTTP_CLIENT.aclose()
MAX_CHAT_FILE_BYTES = 10 * 1024 * 1024
MAX_CHAT_TEXT_CHARS = 80_000
ALLOWED_CHAT_MIME = {"application/pdf", "text/plain", "text/markdown", "application/rtf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword", "image/png", "image/jpeg", "image/webp", "image/gif"}


class ChatRequest(BaseModel):
    message: str


class ContentRequest(BaseModel):
    content: str


class QuantityRequest(BaseModel):
    content: str
    quantity: int = Field(default=10, ge=1, le=100)


class AutoGenerateRequest(BaseModel):
    topic_id: str | None = None
    discipline_id: str | None = None
    course_id: str | None = None
    count: int = Field(default=15, ge=5, le=30)


AUTO_PACK_SCHEMA = {
    "type": "object",
    "properties": {
        "study_material": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["title", "body"]
        },
    },
    "required": ["study_material"]
}


def _clean_ai_text(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    text = re.sub(
        r"```(?:[\w+-]+)?",
        "",
        text,
    )

    text = text.replace("**", "")
    text = text.replace("__", "")

    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE,
    )

    text = re.sub(
        r"^\s*[-*+]\s+",
        "",
        text,
        flags=re.MULTILINE,
    )

    text = text.replace("`", "")

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def _require_api_key():
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Campus IA não está configurado no servidor. Configure GEMINI_API_KEY no Render.",
        )


def _context(content: str) -> str:
    content = (content or "").strip()

    if not content:
        return ""

    return f"""

CONTEÚDO FORNECIDO PELO ESTUDANTE:

{content}
"""


async def _call_gemini(
    model: str,
    prompt: str,
    *,
    json_schema: dict | None = None,
    google_search: bool = False,
    max_output_tokens: int | None = None,
    extra_parts: list[dict] | None = None,
    request: Request | None = None,
) -> tuple[str | None, str | None, int | None, dict | None]:

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}, *(extra_parts or [])]}],
        "generationConfig": {
            "temperature": 0.35,
            "maxOutputTokens": max_output_tokens or AI_MAX_OUTPUT_TOKENS,
        },
    }
    if json_schema:
        payload["generationConfig"].update({
            "responseMimeType": "application/json",
            "responseSchema": json_schema,
        })
    if google_search:
        payload["tools"] = [{"google_search": {}}]

    try:
        client = GEMINI_HTTP_CLIENT
        task = asyncio.create_task(client.post(url, headers=headers, json=payload))
        while not task.done():
            if request is not None and await request.is_disconnected():
                task.cancel()
                raise asyncio.CancelledError()
            await asyncio.sleep(0.1)
        response = await task

        status = response.status_code

        if status >= 400:
            return None, response.text, status, None

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            return None, "Nenhuma resposta retornada.", status, data

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        texts = []

        for part in parts:
            if isinstance(part, dict):
                value = part.get("text")

                if value:
                    texts.append(value)

        result = "\n".join(texts).strip()

        if not result:
            return None, "Resposta vazia.", status, data

        return result, None, status, data

    except Exception as exc:
        return None, str(exc), None, None


async def _generate(
    prompt: str,
    *,
    clean_text: bool = True,
    extra_parts: list[dict] | None = None,
    request: Request | None = None,
) -> str:
    _require_api_key()
    last_error = None
    last_status = None
    models = [GEMINI_MODEL]
    if GEMINI_MODEL != GEMINI_FALLBACK_MODEL:
        models.append(GEMINI_FALLBACK_MODEL)
    for model in models:
        for attempt in range(AI_MAX_RETRIES):
            result, error, status, _ = await _call_gemini(model, prompt, extra_parts=extra_parts, request=request)
            if result:
                return _clean_ai_text(result) if clean_text else result
            last_error, last_status = error, status
            if status in {400, 404} and model != models[-1]:
                break
            if status in {429, 500, 502, 503, 504} and attempt < AI_MAX_RETRIES - 1:
                await asyncio.sleep(0.75 * (attempt + 1))
                continue
            break
    if last_status in {400, 401, 403}:
        raise HTTPException(503, f"Campus IA indisponível: {(last_error or 'configuração inválida')[:500]}")
    raise HTTPException(503, "O serviço de IA está temporariamente indisponível. Tente novamente em alguns segundos.")



def _looks_like_image_request(message: str) -> bool:
    value = (message or "").lower()
    triggers = ("gere uma imagem", "gerar uma imagem", "crie uma imagem", "criar uma imagem",
                "faça uma imagem", "fazer uma imagem", "gere um mapa mental", "crie um mapa mental",
                "crie um mapa conceitual", "crie um diagrama", "crie um infográfico",
                "gere um infográfico", "faça um diagrama", "imagem explicativa")
    return any(trigger in value for trigger in triggers)


async def _save_generated_image(data: bytes, mime_type: str, filename: str) -> str:
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
    file_id = await bucket.upload_from_stream(filename, data, metadata={"content_type": mime_type, "generated_by": "campus-ai"})
    return f"/api/uploads/{file_id}"


async def _generate_image(prompt: str) -> tuple[str, str | None]:
    _require_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_IMAGE_MODEL}:generateContent"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
               "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}}
    response = await GEMINI_HTTP_CLIENT.post(url, headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}, json=payload)
    if response.status_code >= 400:
        raise HTTPException(503, f"Geração de imagem indisponível: {response.text[:500]}")
    data = response.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", []) if data.get("candidates") else []
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            raw = base64.b64decode(inline["data"])
            ext = "jpg" if "jpeg" in mime else "webp" if "webp" in mime else "png"
            return await _save_generated_image(raw, mime, f"campus-ai-generated.{ext}"), part.get("text")
    raise HTTPException(503, "O modelo de geração de imagens não retornou uma imagem.")


async def _read_chat_file(file: UploadFile) -> tuple[list[dict], str]:
    filename = file.filename or "arquivo"
    mime = (file.content_type or "").lower()
    if mime not in ALLOWED_CHAT_MIME:
        raise HTTPException(415, f"Formato não suportado: {filename}.")
    data = await file.read()
    if len(data) > MAX_CHAT_FILE_BYTES:
        raise HTTPException(413, f"O arquivo {filename} excede o limite de 10 MB.")
    if mime.startswith("image/"):
        return ([{"inlineData": {"mimeType": mime, "data": base64.b64encode(data).decode("ascii")}}], f"Imagem anexada: {filename}")
    if mime == "application/pdf":
        from pypdf import PdfReader
        try:
            reader = PdfReader(io.BytesIO(data))
            extracted = "\\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as exc:
            raise HTTPException(422, f"Não foi possível ler o PDF {filename}.") from exc
    elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document
            doc = Document(io.BytesIO(data))
            extracted = "\\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            raise HTTPException(422, f"Não foi possível ler o DOCX {filename}.") from exc
    elif mime == "application/msword":
        raise HTTPException(415, "Arquivos .DOC antigos não são suportados. Salve como .DOCX ou PDF.")
    else:
        extracted = data.decode("utf-8", errors="replace")
    extracted = extracted.strip()
    if not extracted:
        raise HTTPException(422, f"Não foi possível extrair texto de {filename}.")
    return [], f"Conteúdo do arquivo {filename}:\\n{extracted[:MAX_CHAT_TEXT_CHARS]}"


@router.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(400, "Envie uma mensagem em JSON ou use o endpoint /ai/chat-with-files para anexos.") from exc
    message = str(body.get("message", "")).strip()
    if not message:
        raise HTTPException(400, "Digite uma mensagem.")
    if _looks_like_image_request(message):
        image_url, note = await _generate_image(message)
        answer = note or "Imagem gerada pelo Campus IA."
        return {"success": True, "answer": answer, "message": answer, "image_url": image_url, "model": GEMINI_IMAGE_MODEL}
    prompt = f"""
Você é o Campus AI, assistente de inteligência artificial integrado à plataforma Campus Study.
Ajude estudantes com dúvidas, estudos, explicações, exercícios e organização acadêmica.
Responda em português do Brasil, de forma clara, natural e objetiva.
Se a pergunta for simples, responda de forma curta e direta.
Não use Markdown, crases, hashtags ou blocos de código.

MENSAGEM DO ESTUDANTE:
{message}
"""
    response = await _generate(prompt, request=request)
    return {"success": True, "message": response, "answer": response, "model": GEMINI_MODEL}


@router.post("/chat-with-files")
async def chat_with_files(
    request: Request,
    message: str = Form(""),
    files: list[UploadFile] = File(default=[]),
):
    message = message.strip()
    if not message:
        raise HTTPException(400, "Digite uma pergunta sobre o anexo.")
    if len(files) > 5:
        raise HTTPException(400, "Envie no máximo 5 arquivos por pergunta.")
    parts: list[dict] = []
    extracted: list[str] = []
    for file in files:
        file_parts, text_part = await _read_chat_file(file)
        parts.extend(file_parts)
        extracted.append(text_part)
    prompt = f"""
Você é o Campus AI do Campus Study.
Responda à pergunta do estudante usando os anexos como fonte principal.
Se o anexo não contiver informação suficiente, diga isso claramente.
Explique de forma didática, objetiva e em português do Brasil.
Não use Markdown, crases, hashtags ou blocos de código.

PERGUNTA:
{message}

ANEXOS DE TEXTO:
{chr(10).join(extracted)[:MAX_CHAT_TEXT_CHARS]}
"""
    response = await _generate(prompt, extra_parts=parts, request=request)
    return {"success": True, "answer": response, "message": response, "model": GEMINI_MODEL}


@router.post("/image")
async def generate_image_endpoint(body: ContentRequest):
    prompt = body.content.strip()
    if not prompt:
        raise HTTPException(400, "Descreva a imagem que deseja gerar.")
    image_url, note = await _generate_image(prompt)
    return {"success": True, "image_url": image_url, "answer": note or "Imagem gerada.", "model": GEMINI_IMAGE_MODEL}


@router.post("/summary")
async def summary(request: ContentRequest):

    content = request.content.strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Informe o conteúdo para resumir.",
        )

    prompt = f"""
Você é o Campus AI.

Faça um resumo didático do conteúdo abaixo.

Explique os conceitos mais importantes de maneira clara
e adequada para um estudante.

Use texto simples.

NÃO use Markdown.
NÃO use **.
NÃO use *.
NÃO use #.
NÃO use crases.

{_context(content)}
"""

    response = await _generate(prompt)

    return {
        "success": True,
        "summary": response,
        "answer": response,
        "message": response,
        "model": GEMINI_MODEL,
    }


@router.post("/questions")
async def questions(request: QuantityRequest):

    content = request.content.strip()
    quantity = max(1, min(request.quantity, 100))

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Informe o conteúdo para gerar questões.",
        )

    prompt = f"""
Você é o Campus AI.

Crie {quantity} questões para estudo com base no conteúdo
fornecido.

Para cada questão apresente:

Questão:
pergunta

Resposta:
resposta correta

Explicação:
explicação

Use texto simples.

NÃO use Markdown.
NÃO use **.
NÃO use *.
NÃO use #.
NÃO use crases.

{_context(content)}
"""

    response = await _generate(prompt)

    return {
        "success": True,
        "questions": response,
        "answer": response,
        "message": response,
        "model": GEMINI_MODEL,
    }



@router.post("/mindmap")
async def mindmap(request: ContentRequest):

    content = request.content.strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Informe o conteúdo para gerar o mapa mental.",
        )

    prompt = f"""
Você é o Campus AI.

Transforme o conteúdo abaixo em uma estrutura textual
de mapa mental.

Organize os conceitos de forma lógica e didática.

Use texto simples.

NÃO use Markdown.
NÃO use **.
NÃO use *.
NÃO use #.
NÃO use crases.

{_context(content)}
"""

    response = await _generate(prompt)

    return {
        "success": True,
        "mindmap": response,
        "answer": response,
        "message": response,
        "model": GEMINI_MODEL,
    }


@router.post("/study-plan")
async def study_plan(request: ContentRequest):

    content = request.content.strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Informe os dados para criar o plano.",
        )

    prompt = f"""
Você é o Campus AI.

Crie um plano de estudos prático com base nas informações
fornecidas.

Inclua:

Objetivos
Conteúdos
Ordem de estudo
Revisões
Exercícios
Rotina sugerida

Use texto simples.

NÃO use Markdown.
NÃO use **.
NÃO use *.
NÃO use #.
NÃO use crases.

{_context(content)}
"""

    response = await _generate(prompt)

    return {
        "success": True,
        "plan": response,
        "study_plan": response,
        "answer": response,
        "message": response,
        "model": GEMINI_MODEL,
    }


@router.post("/simulado")
async def simulado(request: QuantityRequest):

    content = request.content.strip()
    quantity = max(1, min(request.quantity, 100))

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Informe o conteúdo para gerar o simulado.",
        )

    prompt = f"""
Você é o Campus AI.

Crie um simulado com {quantity} questões.

Retorne SOMENTE JSON válido.

Formato:

{{
  "questions": [
    {{
      "question": "Pergunta",
      "options": [
        "Alternativa A",
        "Alternativa B",
        "Alternativa C",
        "Alternativa D"
      ],
      "answer": 0,
      "explanation": "Explicação"
    }}
  ]
}}

O campo answer deve ser o índice da alternativa correta,
começando em 0.

Não escreva nada antes ou depois do JSON.

{_context(content)}
"""

    response = await _generate(
        prompt,
        clean_text=False,
    )

    cleaned = response.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        parsed = json.loads(cleaned)

    except json.JSONDecodeError:

        return {
            "success": True,
            "simulado": response,
            "exam": response,
            "answer": response,
            "message": response,
            "model": GEMINI_MODEL,
        }

    return {
        "success": True,
        "simulado": parsed,
        "exam": parsed,
        "answer": parsed,
        "message": parsed,
        "model": GEMINI_MODEL,
    }


async def _call_gemini_json(prompt: str) -> dict:
    _require_api_key()
    last_error = None
    for attempt in range(4):
        result, error, status, _meta = await _call_gemini(
            GEMINI_MODEL,
            prompt,
            json_schema=AUTO_PACK_SCHEMA,
        )
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError as exc:
                last_error = str(exc)
        else:
            last_error = error
        if status in {429, 500, 502, 503, 504} and attempt < 3:
            await asyncio.sleep(2 * (attempt + 1))
            continue
        break
    raise HTTPException(503, f"Não foi possível gerar o conteúdo automaticamente: {last_error or 'erro desconhecido'}")


async def _create_original_pdf(ctx: dict, material: dict) -> str:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=48, bottomMargin=48, title=material.get("title", "Campus Study"))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CampusTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=18, leading=22, spaceAfter=16)
    body_style = ParagraphStyle("CampusBody", parent=styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=9)
    story = [Paragraph(material.get("title") or f"Guia de estudo: {ctx['topic']['name']}", title_style), Paragraph(f"{ctx['course']['name']} · {ctx['period']['name']} · {ctx['discipline']['name']}", body_style), Spacer(1, 8)]
    for paragraph in re.split(r"\n\s*\n", material.get("body", "")):
        clean = paragraph.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if clean:
            story.append(Paragraph(clean.replace("\n", "<br/>"), body_style))
    doc.build(story)
    buffer.seek(0)
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
    file_id = await bucket.upload_from_stream(f"campus-study-{ctx['topic']['slug']}.pdf", buffer.read(), metadata={"content_type": "application/pdf", "generated_by": "campus-ai", "topic_id": ctx["topic"]["id"]})
    return str(file_id)


async def _insert_generated_pack(ctx: dict, pack: dict, sources: list[dict] | None = None) -> dict:
    now = now_utc()
    sources = sources or []
    topic = ctx["topic"]
    discipline = ctx["discipline"]
    period = ctx["period"]
    course = ctx["course"]
    base = {
        "course_id": course["id"], "period_id": period["id"], "discipline_id": discipline["id"],
        "course_name": course["name"], "period_name": period["name"], "discipline_name": discipline["name"],
        "topic_name": topic["name"], "path": f"/cursos/{course['slug']}/{period['slug']}/{discipline['slug']}/{topic['slug']}",
        "topic_id": topic["id"], "status": "publicado", "tags": ["ia-gerado", topic["name"], discipline["name"]],
        "created_at": now, "updated_at": now, "views": 0,
    }
    created = {"material": 0, "questao": 0}
    key = f"ai:{topic['id']}"
    material = pack.get("study_material") or {}
    if material.get("body") and not await db.contents.find_one({"topic_id": topic["id"], "type": "material", "data.ai_generation_key": key}):
        await db.contents.insert_one({**base, "id": str(uuid.uuid4()), "type": "material", "title": material.get("title") or f"Guia de estudo: {topic['name']}", "description": "Material didático gerado automaticamente pelo Campus Study.", "difficulty": "", "data": {"body": material["body"], "pdf_url": material.get("pdf_url", ""), "file_name": material.get("pdf_file_name", ""), "sources": sources, "ai_generated": True, "ai_generation_key": key}})
        created["material"] = 1
    for source in sources:
        url = (source.get("url") or "").strip()
        if not url:
            continue
        is_youtube = "youtube.com/" in url or "youtu.be/" in url
        kind = "video" if is_youtube else "artigo"
        if kind == "video" and not youtube_id(url):
            continue
        exists = await db.contents.find_one({"topic_id": topic["id"], "type": kind, "data.url": url})
        if exists:
            continue
        data = {"url": url, "ai_generated": True, "ai_generation_key": key, "source_verified_by_search": True}
        if kind == "video":
            vid = youtube_id(url)
            data.update({"video_id": vid, "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", "link_status": "funcionando"})
        await db.contents.insert_one({**base, "id": str(uuid.uuid4()), "type": kind, "title": source.get("title") or ("Videoaula recomendada" if is_youtube else "Fonte acadêmica"), "description": "Fonte encontrada automaticamente durante a pesquisa web.", "difficulty": "", "data": data})
    # Questions/simulados are intentionally not generated here. Their existing
    # dedicated flows remain available and are preserved.
    return created


async def _research_topic(ctx: dict) -> tuple[str, list[dict]]:
    prompt = f"""
Pesquise na web para fundamentar um conteúdo acadêmico em português do Brasil.
Curso: {ctx['course']['name']}
Disciplina: {ctx['discipline']['name']}
Assunto: {ctx['topic']['name']}

Priorize fontes institucionais, universidades, órgãos oficiais, periódicos científicos, bibliotecas acadêmicas e materiais educacionais abertos.
Procure também uma videoaula pública do YouTube quando houver uma opção claramente relacionada.
Não use pirataria, PDFs de livros protegidos por direitos autorais ou sites de download ilegal.
Resuma somente os fatos e conceitos relevantes e cite as fontes encontradas.
"""
    result, error, status, meta = await _call_gemini(GEMINI_MODEL, prompt, google_search=True)
    if not result:
        return "", []
    sources = []
    for chunk in (meta or {}).get("groundingMetadata", {}).get("groundingChunks", []):
        web = chunk.get("web") if isinstance(chunk, dict) else None
        if web and web.get("uri"):
            sources.append({"title": web.get("title", "Fonte pesquisada"), "url": web["uri"]})
    return result[:12000], sources[:20]


async def generate_topic_pack(topic_id: str, *, force: bool = False) -> dict:
    ctx = await topic_context(topic_id)
    key = f"ai:{topic_id}"
    existing_material = await db.contents.find_one({"topic_id": topic_id, "type": "material", "data.ai_generation_key": key}, {"_id": 0, "id": 1})
    if existing_material and not force:
        return {"status": "ready", "created": {"material": 0, "questao": 0}, "existing": 1}
    research, sources = await _research_topic(ctx)
    prompt = f"""
Você é o motor acadêmico do Campus Study. Gere conteúdo educacional ORIGINAL, claro e verificável para este assunto.
Curso: {ctx['course']['name']}
Período: {ctx['period']['name']}
Disciplina: {ctx['discipline']['name']}
Assunto: {ctx['topic']['name']}
Descrição disponível: {ctx['topic'].get('description','')}

PESQUISA WEB REALIZADA PELO SISTEMA:
{research}

FONTES ENCONTRADAS:
{json.dumps(sources, ensure_ascii=False)}

Regras:
1. Não invente leis, fórmulas, definições, dados ou referências.
2. Priorize conceitos acadêmicos estáveis e, quando houver fatos específicos, use conhecimento verificável.
3. Crie um guia de estudo original, sem copiar livros, apostilas ou sites.
4. Não gere simulados, banco de questões ou flashcards neste fluxo; essas funcionalidades possuem seus próprios endpoints.
5. Todo conteúdo deve estar em português do Brasil.
6. Retorne exclusivamente o JSON conforme o schema solicitado.
"""
    pack = await _call_gemini_json(prompt)
    material = pack.get("study_material") or {}
    if not isinstance(material, dict) or not str(material.get("body", "")).strip():
        raise HTTPException(503, "A IA retornou conteúdo vazio. Tente novamente.")
    pdf_id = await _create_original_pdf(ctx, material)
    pack["study_material"]["pdf_url"] = f"/api/uploads/{pdf_id}"
    pack["study_material"]["pdf_file_name"] = f"Campus Study - {ctx['topic']['name']}.pdf"
    created = await _insert_generated_pack(ctx, pack, sources)
    return {"status": "generated", "created": created, "pdf_generated": True}


@router.post("/topic-pack/{topic_id}")
async def topic_pack(topic_id: str, user: dict = Depends(current_user)):
    require_feature_access(user, "materiais")
    result = await generate_topic_pack(topic_id)
    return {"success": True, **result, "model": GEMINI_MODEL}


@router.post("/generate")
async def generate_for_scope(body: AutoGenerateRequest, user: dict = Depends(current_user)):
    require_feature_access(user, "materiais")
    if body.topic_id:
        return {"success": True, "scope": "topic", **await generate_topic_pack(body.topic_id)}
    if body.discipline_id:
        topics = await db.topics.find({"discipline_id": body.discipline_id, "status": "publicado"}, {"id": 1}).sort("name", 1).limit(10).to_list(10)
    elif body.course_id:
        topics = await db.topics.find({"course_id": body.course_id, "status": "publicado"}, {"id": 1}).sort("name", 1).limit(10).to_list(10)
    else:
        raise HTTPException(400, "Informe topic_id, discipline_id ou course_id.")
    results = []
    for t in topics:
        results.append({"topic_id": t["id"], **await generate_topic_pack(t["id"])})
    return {"success": True, "scope": "discipline" if body.discipline_id else "course", "results": results, "model": GEMINI_MODEL}


@router.post("/admin/generate-all")
async def queue_generate_all(admin: dict = Depends(admin_user)):
    _require_api_key()
    active = await db.ai_generation_jobs.find_one({"status": {"$in": ["queued", "running"]}}, {"_id": 0})
    if active:
        return {"success": True, "job_id": active["id"], "total": active.get("total", 0), "status": active.get("status"), "message": "Já existe uma geração em andamento."}
    topics = await db.topics.find({"status": "publicado"}, {"id": 1}).to_list(10000)
    job = {"id": str(uuid.uuid4()), "status": "queued", "total": len(topics), "processed": 0, "failed": 0, "topic_ids": [t["id"] for t in topics], "created_at": now_utc(), "updated_at": now_utc(), "started_at": None, "finished_at": None, "error": ""}
    await db.ai_generation_jobs.insert_one(job)
    return {"success": True, "job_id": job["id"], "total": len(topics), "message": "Geração automática enfileirada. O servidor processará os assuntos sem exigir cadastro manual."}


@router.get("/admin/generate-all/status")
async def generation_status(admin: dict = Depends(admin_user)):
    job = await db.ai_generation_jobs.find_one({}, {"_id": 0}, sort=[("created_at", -1)])
    base = {"status": "idle", "total": 0, "processed": 0, "failed": 0, "configured": bool(GEMINI_API_KEY)}
    if not job:
        return base
    return {**base, **job, "configured": bool(GEMINI_API_KEY)}


@router.get("/history")
async def history():

    return {
        "success": True,
        "history": [],
    }


@router.get("/simulados")
async def simulados():

    return {
        "success": True,
        "simulados": [],
    }
