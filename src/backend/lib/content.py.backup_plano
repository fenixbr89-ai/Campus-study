"""Shared helpers for the academic hierarchy and content serialization."""

import re
import unicodedata

from fastapi import HTTPException

from lib.auth import full_access

from lib.db import db
from lib.security import now_utc



def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"


def period_name(number: int) -> str:
    return f"{number}º período"


def period_slug(number: int) -> str:
    return f"{number}-periodo"


def youtube_id(url: str) -> str | None:
    m = re.search(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})", url or "")
    return m.group(1) if m else None


async def topic_context(topic_id: str) -> dict:
    topic = await db.topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        raise HTTPException(404, "Assunto não encontrado.")
    disc = await db.disciplines.find_one({"id": topic["discipline_id"]}, {"_id": 0})
    period = await db.periods.find_one({"id": topic["period_id"]}, {"_id": 0})
    course = await db.courses.find_one({"id": topic["course_id"]}, {"_id": 0})
    if not (disc and period and course):
        raise HTTPException(404, "Estrutura acadêmica incompleta para este assunto.")
    return {"topic": topic, "discipline": disc, "period": period, "course": course}


def topic_path(ctx: dict) -> str:
    return f"/cursos/{ctx['course']['slug']}/{ctx['period']['slug']}/{ctx['discipline']['slug']}/{ctx['topic']['slug']}"


async def denormalize_content(doc: dict) -> dict:
    ctx = await topic_context(doc["topic_id"])
    doc.update({
        "course_id": ctx["course"]["id"], "period_id": ctx["period"]["id"], "discipline_id": ctx["discipline"]["id"],
        "course_name": ctx["course"]["name"], "period_name": ctx["period"]["name"],
        "discipline_name": ctx["discipline"]["name"], "topic_name": ctx["topic"]["name"], "path": topic_path(ctx),
    })
    if doc["type"] == "video":
        vid = youtube_id(doc["data"].get("url", ""))
        if not vid:
            raise HTTPException(400, "Informe uma URL válida do YouTube (youtube.com/watch?v=... ou youtu.be/...).")
        doc["data"]["video_id"] = vid
        if not doc["data"].get("thumbnail"):
            doc["data"]["thumbnail"] = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        doc["data"].setdefault("link_status", "verificar")
    doc["search_text"] = " ".join([doc["title"], doc.get("description", ""), " ".join(doc.get("tags", [])),
                                   doc["topic_name"], doc["discipline_name"], doc["course_name"],
                                   str(doc["data"].get("keywords", "")), str(doc["data"].get("authors", ""))])
    doc["updated_at"] = now_utc()
    return doc


def _feature_key_for_content(content_type: str) -> str | None:
    return {"video": "videoaulas", "pdf": "pdf", "material": "materiais", "resumo": "materiais", "livro": "materiais", "artigo": "artigos", "questao": "questoes"}.get(content_type)

def visible_content_query(user: dict | None) -> dict:
    if not user or full_access(user):
        return {}
    features = user.get("_feature_settings", {}).get("limitado", {})
    blocked = [t for t in ("video", "pdf", "material", "resumo", "livro", "artigo", "questao") if not features.get(_feature_key_for_content(t) or "", False)]
    return {"type": {"$nin": blocked}} if blocked else {}

def present_content(doc: dict, user: dict | None) -> dict:
    if user and not full_access(user):
        feature = _feature_key_for_content(doc.get("type", ""))
        if feature and not user.get("_feature_settings", {}).get("limitado", {}).get(feature, False):
            raise HTTPException(403, "Este recurso está disponível apenas no plano que inclui esta funcionalidade.")
    return {k: v for k, v in doc.items() if k not in ("_id", "search_text")}
