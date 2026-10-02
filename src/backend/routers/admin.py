"""Admin panel API — every route requires role admin/superadmin (checked server-side)."""

import math
import re
import uuid
import io
import json
import zipfile

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from lib.auth import admin_user, log_admin
from lib.content import denormalize_content, period_name, period_slug, slugify
from lib.db import db
from lib.security import hash_password, mask_email, now_utc, validate_password_strength, verify_password
from lib.settings import get_settings
from lib.stripe import get_stripe_config, save_stripe_config, stripe_request
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from models.schemas import (
    AdminLog, AdminStats, AdminUser,
    AdminUserPatch, ChangePasswordIn, Content, ContentIn, ContentPage, ContentType, Course, CourseIn,
    Discipline, DisciplineIn, Message, NamedCount, Period, PeriodIn, Settings, SettingsIn, StatusPatch, Submission,
    SubmissionPatch, Topic, TopicIn, TopContent,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_user)])
P = {"_id": 0}


@router.get("/stats", response_model=AdminStats)
async def stats():
    from datetime import timedelta
    since = now_utc() - timedelta(days=30)
    by_type = await db.contents.aggregate([{"$group": {"_id": "$type", "n": {"$sum": 1}}}]).to_list(20)
    searches = await db.search_logs.find({}, P).sort("count", -1).limit(10).to_list(10)
    top = await db.contents.find({}, P).sort("views", -1).limit(10).to_list(10)
    return AdminStats(
        users=await db.users.count_documents({}), active_users=await db.users.count_documents({"last_login_at": {"$gte": since}}),
courses=await db.courses.count_documents({}), periods=await db.periods.count_documents({}),
        disciplines=await db.disciplines.count_documents({}), topics=await db.topics.count_documents({}),
        contents_by_type={b["_id"]: b["n"] for b in by_type},
        pending_submissions=await db.submissions.count_documents({"status": {"$in": ["pendente", "em_analise"]}}),
        exams=await db.exams.count_documents({}),
        top_searches=[NamedCount(label=s["term"], count=s["count"]) for s in searches],
        top_contents=[TopContent(id=c["id"], title=c["title"], type=c["type"], views=c.get("views", 0)) for c in top if c.get("views")])


# ---------- hierarchy ----------
async def _unique_slug(coll, base: str, scope: dict, exclude_id: str | None = None) -> str:
    slug, n = base, 2
    while await coll.find_one({**scope, "slug": slug, **({"id": {"$ne": exclude_id}} if exclude_id else {})}):
        slug, n = f"{base}-{n}", n + 1
    return slug


async def _sync_periods(course: dict) -> None:
    for n in range(1, course["num_periods"] + 1):
        if not await db.periods.find_one({"course_id": course["id"], "number": n}):
            await db.periods.insert_one(Period(course_id=course["id"], number=n, name=period_name(n), slug=period_slug(n)).model_dump())


@router.get("/courses", response_model=list[Course])
async def a_courses():
    return await db.courses.find({}, P).sort("name", 1).to_list(1000)


@router.post("/courses", response_model=Course)
async def a_course_create(body: CourseIn, admin: dict = Depends(admin_user)):
    course = Course(**body.model_dump(), slug=await _unique_slug(db.courses, slugify(body.name), {}))
    await db.courses.insert_one(course.model_dump())
    await _sync_periods(course.model_dump())
    await log_admin(admin, "criou", "curso", course.id)
    return course


@router.put("/courses/{cid}", response_model=Course)
async def a_course_update(cid: str, body: CourseIn, admin: dict = Depends(admin_user)):
    old = await db.courses.find_one({"id": cid}, P)
    if not old:
        raise HTTPException(404, "Curso não encontrado.")
    slug = old["slug"] if old["name"] == body.name else await _unique_slug(db.courses, slugify(body.name), {}, cid)
    course = Course(**body.model_dump(), id=cid, slug=slug)
    await db.courses.replace_one({"id": cid}, course.model_dump())
    await _sync_periods(course.model_dump())
    await db.contents.update_many({"course_id": cid}, {"$set": {"course_name": body.name}})
    await log_admin(admin, "editou", "curso", cid)
    return course


@router.delete("/courses/{cid}", response_model=Message)
async def a_course_delete(cid: str, admin: dict = Depends(admin_user)):
    if await db.disciplines.find_one({"course_id": cid}):
        raise HTTPException(409, "Remova as disciplinas deste curso antes de excluí-lo (ou arquive o curso).")
    await db.periods.delete_many({"course_id": cid})
    await db.courses.delete_one({"id": cid})
    await log_admin(admin, "excluiu", "curso", cid)
    return Message(message="Curso excluído.")


@router.get("/periods", response_model=list[Period])
async def a_periods(course_id: str):
    return await db.periods.find({"course_id": course_id}, P).sort("number", 1).to_list(50)


@router.post("/periods", response_model=Period)
async def a_period_create(body: PeriodIn, admin: dict = Depends(admin_user)):
    if await db.periods.find_one({"course_id": body.course_id, "number": body.number}):
        raise HTTPException(409, "Este período já existe no curso.")
    p = Period(course_id=body.course_id, number=body.number, name=body.name or period_name(body.number), slug=period_slug(body.number))
    await db.periods.insert_one(p.model_dump())
    await log_admin(admin, "criou", "período", p.id)
    return p


@router.put("/periods/{pid}", response_model=Period)
async def a_period_update(pid: str, body: PeriodIn, admin: dict = Depends(admin_user)):
    if not await db.periods.find_one({"id": pid}):
        raise HTTPException(404, "Período não encontrado.")
    p = Period(course_id=body.course_id, number=body.number, name=body.name or period_name(body.number), slug=period_slug(body.number), id=pid)
    await db.periods.replace_one({"id": pid}, p.model_dump())
    await db.contents.update_many({"period_id": pid}, {"$set": {"period_name": p.name}})
    await log_admin(admin, "editou", "período", pid)
    return p


@router.delete("/periods/{pid}", response_model=Message)
async def a_period_delete(pid: str, admin: dict = Depends(admin_user)):
    if await db.disciplines.find_one({"period_id": pid}):
        raise HTTPException(409, "Remova as disciplinas deste período antes de excluí-lo.")
    await db.periods.delete_one({"id": pid})
    await log_admin(admin, "excluiu", "período", pid)
    return Message(message="Período excluído.")


@router.get("/disciplines", response_model=list[Discipline])
async def a_disciplines(period_id: str):
    return await db.disciplines.find({"period_id": period_id}, P).sort("name", 1).to_list(1000)


async def _discipline(body: DisciplineIn, did: str | None) -> Discipline:
    period = await db.periods.find_one({"id": body.period_id}, P)
    if not period:
        raise HTTPException(404, "Período não encontrado.")
    slug = await _unique_slug(db.disciplines, slugify(body.name), {"period_id": body.period_id}, did)
    return Discipline(**body.model_dump(), course_id=period["course_id"], slug=slug, **({"id": did} if did else {}))


@router.post("/disciplines", response_model=Discipline)
async def a_disc_create(body: DisciplineIn, admin: dict = Depends(admin_user)):
    d = await _discipline(body, None)
    await db.disciplines.insert_one(d.model_dump())
    await log_admin(admin, "criou", "disciplina", d.id)
    return d


@router.put("/disciplines/{did}", response_model=Discipline)
async def a_disc_update(did: str, body: DisciplineIn, admin: dict = Depends(admin_user)):
    if not await db.disciplines.find_one({"id": did}):
        raise HTTPException(404, "Disciplina não encontrada.")
    d = await _discipline(body, did)
    await db.disciplines.replace_one({"id": did}, d.model_dump())
    await log_admin(admin, "editou", "disciplina", did)
    return d


@router.delete("/disciplines/{did}", response_model=Message)
async def a_disc_delete(did: str, admin: dict = Depends(admin_user)):
    if await db.topics.find_one({"discipline_id": did}):
        raise HTTPException(409, "Remova os assuntos desta disciplina antes de excluí-la.")
    await db.disciplines.delete_one({"id": did})
    await log_admin(admin, "excluiu", "disciplina", did)
    return Message(message="Disciplina excluída.")


@router.get("/topics", response_model=list[Topic])
async def a_topics(discipline_id: str):
    return await db.topics.find({"discipline_id": discipline_id}, P).sort("name", 1).to_list(1000)


async def _topic(body: TopicIn, tid: str | None) -> Topic:
    disc = await db.disciplines.find_one({"id": body.discipline_id}, P)
    if not disc:
        raise HTTPException(404, "Disciplina não encontrada.")
    slug = await _unique_slug(db.topics, slugify(body.name), {"discipline_id": body.discipline_id}, tid)
    return Topic(**body.model_dump(), course_id=disc["course_id"], period_id=disc["period_id"], slug=slug, **({"id": tid} if tid else {}))


@router.post("/topics", response_model=Topic)
async def a_topic_create(body: TopicIn, admin: dict = Depends(admin_user)):
    t = await _topic(body, None)
    await db.topics.insert_one(t.model_dump())
    await log_admin(admin, "criou", "assunto", t.id)
    return t


@router.put("/topics/{tid}", response_model=Topic)
async def a_topic_update(tid: str, body: TopicIn, admin: dict = Depends(admin_user)):
    if not await db.topics.find_one({"id": tid}):
        raise HTTPException(404, "Assunto não encontrado.")
    t = await _topic(body, tid)
    await db.topics.replace_one({"id": tid}, t.model_dump())
    await log_admin(admin, "editou", "assunto", tid)
    return t


@router.delete("/topics/{tid}", response_model=Message)
async def a_topic_delete(tid: str, admin: dict = Depends(admin_user)):
    if await db.contents.find_one({"topic_id": tid}):
        raise HTTPException(409, "Remova os materiais deste assunto antes de excluí-lo.")
    await db.topics.delete_one({"id": tid})
    await log_admin(admin, "excluiu", "assunto", tid)
    return Message(message="Assunto excluído.")


# ---------- contents ----------
@router.get("/contents", response_model=ContentPage)
async def a_contents(type: str = "", q: str = "", status: str = "", link_status: str = "", page: int = 1):
    flt: dict = {}
    if type:
        flt["type"] = type
    if status:
        flt["status"] = status
    if link_status:
        flt["data.link_status"] = link_status
    if q:
        flt["$or"] = [{"title": {"$regex": re.escape(q), "$options": "i"}}, {"data.url": {"$regex": re.escape(q), "$options": "i"}},
                      {"topic_name": {"$regex": re.escape(q), "$options": "i"}}]
    size = 20
    total = await db.contents.count_documents(flt)
    docs = await db.contents.find(flt, {"_id": 0, "search_text": 0}).sort("updated_at", -1).skip((max(page, 1) - 1) * size).limit(size).to_list(size)
    return ContentPage(items=docs, total=total, page=page, pages=max(1, math.ceil(total / size)))


@router.post("/contents", response_model=Content)
async def a_content_create(body: ContentIn, admin: dict = Depends(admin_user)):
    doc = await denormalize_content({**body.model_dump(), "id": str(uuid.uuid4()), "views": 0, "locked": False, "created_at": now_utc()})
    await db.contents.insert_one(doc)
    await log_admin(admin, "criou", f"conteúdo ({body.type})", doc["id"])
    return Content(**{k: v for k, v in doc.items() if k not in ("_id", "search_text")})


@router.put("/contents/{cid}", response_model=Content)
async def a_content_update(cid: str, body: ContentIn, admin: dict = Depends(admin_user)):
    old = await db.contents.find_one({"id": cid}, P)
    if not old:
        raise HTTPException(404, "Conteúdo não encontrado.")
    data = body.model_dump()
    if body.type == "video" and old["data"].get("url") != body.data.get("url"):
        data["data"]["link_status"] = "verificar"
        data["data"].pop("thumbnail", None) if old["data"].get("thumbnail") == body.data.get("thumbnail") else None
    doc = await denormalize_content({**data, "id": cid, "views": old.get("views", 0), "locked": False, "created_at": old["created_at"]})
    await db.contents.replace_one({"id": cid}, doc)
    await log_admin(admin, "editou", f"conteúdo ({body.type})", cid)
    return Content(**{k: v for k, v in doc.items() if k not in ("_id", "search_text")})


@router.patch("/contents/{cid}/status", response_model=Message)
async def a_content_status(cid: str, body: StatusPatch, admin: dict = Depends(admin_user)):
    res = await db.contents.update_one({"id": cid}, {"$set": {"status": body.status, "updated_at": now_utc()}})
    if not res.matched_count:
        raise HTTPException(404, "Conteúdo não encontrado.")
    await log_admin(admin, f"alterou status para {body.status}", "conteúdo", cid)
    return Message(message="Status atualizado.")


@router.delete("/contents/{cid}", response_model=Message)
async def a_content_delete(cid: str, admin: dict = Depends(admin_user)):
    await db.contents.delete_one({"id": cid})
    await db.favorites.delete_many({"content_id": cid})
    await log_admin(admin, "excluiu", "conteúdo", cid)
    return Message(message="Conteúdo excluído.")


async def _check_video(doc: dict) -> str:
    url = doc["data"].get("url", "")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://www.youtube.com/oembed", params={"url": url, "format": "json"})
        status = "funcionando" if r.status_code == 200 else "indisponivel" if r.status_code in (400, 401, 403, 404) else "verificar"
    except httpx.HTTPError:
        status = "verificar"
    await db.contents.update_one({"id": doc["id"]}, {"$set": {"data.link_status": status, "data.checked_at": now_utc().isoformat()}})
    return status


@router.post("/contents/{cid}/check-link", response_model=Message)
async def a_check_link(cid: str):
    doc = await db.contents.find_one({"id": cid, "type": "video"}, P)
    if not doc:
        raise HTTPException(404, "Vídeo não encontrado.")
    status = await _check_video(doc)
    return Message(message={"funcionando": "Vídeo funcionando.", "indisponivel": "Vídeo indisponível no YouTube — substitua o link.",
                            "verificar": "Não foi possível verificar agora."}[status])


@router.post("/videos/check-all", response_model=Message)
async def a_check_all():
    docs = await db.contents.find({"type": "video", "status": {"$ne": "arquivado"}}, P).to_list(500)
    results = [await _check_video(d) for d in docs]
    return Message(message=f"{len(results)} vídeos verificados: {results.count('funcionando')} funcionando, "
                           f"{results.count('indisponivel')} indisponíveis, {results.count('verificar')} a verificar.")



@router.post("/uploads")
async def a_upload_file(file: UploadFile = File(...), admin: dict = Depends(admin_user)):
    allowed = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Tipo de arquivo não permitido. Use PDF, PNG, JPG ou WebP.")
    data = await file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "O arquivo excede o limite de 20 MB.")
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
    file_id = await bucket.upload_from_stream(file.filename or "arquivo", data, metadata={"content_type": file.content_type, "uploaded_by": admin["id"]})
    await log_admin(admin, "enviou arquivo", "arquivo", str(file_id))
    return {"id": str(file_id), "url": f"/api/uploads/{file_id}", "name": file.filename or "arquivo", "content_type": file.content_type, "size": len(data)}


@router.get("/payments/stripe/subscriptions")
async def a_stripe_subscriptions():
    docs = await db.stripe_subscriptions.find({}, {"_id": 0}).sort("updated_at", -1).limit(500).to_list(500)
    return docs

@router.post("/payments/stripe/test", response_model=Message)
async def a_stripe_test(admin: dict = Depends(admin_user)):
    cfg = await get_stripe_config()
    if not cfg.get("enabled"):
        raise HTTPException(400, "Stripe está desativado nas configurações.")
    await stripe_request("GET", "/balance")
    await log_admin(admin, "testou conexão Stripe", "pagamentos")
    return Message(message="Conexão com o Stripe funcionando.")

@router.post("/payments/stripe/subscriptions/{subscription_id}/cancel", response_model=Message)
async def a_stripe_cancel(subscription_id: str, admin: dict = Depends(admin_user)):
    try:
        await stripe_request("DELETE", f"/subscriptions/{subscription_id}")
    except RuntimeError as exc:
        raise HTTPException(502, str(exc)) from exc
    await db.stripe_subscriptions.update_one({"subscription_id": subscription_id}, {"$set": {"status": "canceled", "updated_at": now_utc()}})
    await log_admin(admin, "cancelou assinatura Stripe", "pagamento", subscription_id)
    return Message(message="Assinatura cancelada no Stripe.")


# ---------- content ZIP importer ----------
def _safe_zip_name(name: str) -> str:
    name = name.replace("\\", "/").strip("/")
    if not name or name.startswith("../") or "/../" in name or name.startswith("/"):
        raise HTTPException(400, "ZIP contém caminho inválido.")
    return name

def _is_period_segment(value: str) -> bool:
    normalized = value.strip().lower().replace("º", "")
    return bool(re.match(r"^\d+([_\- ]*(periodo|período))?([_\- ].*)?$", normalized))

def _course_name_from_wrapper(wrapper: str) -> str:
    value = wrapper.replace("_", " ").strip()
    # Common exported ZIP wrappers: Campus-Study-Administracao-1Periodo-Matematica
    # Keep the actual course name while discarding the export prefix and period/topic suffix.
    value = re.sub(r"^campus[-_ ]*study[-_ ]*", "", value, flags=re.I)
    value = re.sub(r"[-_ ]+\d+[-_ ]*(?:periodo|período)(?:[-_ ].*)?$", "", value, flags=re.I)
    return value.strip(" -_") or wrapper.replace("_", " ").strip()

def _resolve_zip_hierarchy(parts: list[str]) -> tuple[str, str, str, str] | None:
    # Locate the first directory that clearly represents a period. Everything immediately
    # after it is discipline/topic; the directory immediately before it is the course.
    # This handles both Curso/1_Periodo/Disciplina/Assunto/arquivo and exported wrappers
    # such as Campus-Study-Curso-1Periodo-Assunto/1_Periodo/Disciplina/Assunto/arquivo.
    if len(parts) < 5:
        return None
    directories = parts[:-1]
    period_index = next((i for i, value in enumerate(directories) if _is_period_segment(value)), None)
    if period_index is not None and period_index >= 1 and len(directories) >= period_index + 3:
        course = directories[period_index - 1]
        period, discipline, topic = directories[period_index:period_index + 3]
        if course.lower().startswith(("campus-study", "campus_study", "campus study")):
            course = _course_name_from_wrapper(course)
        return course, period, discipline, topic

    # Legacy/fallback shape: use the final four directories.
    course, period, discipline, topic = directories[-4:]
    return course, period, discipline, topic

def _parse_content_zip(raw: bytes) -> list[dict]:
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
        if zf.testzip() is not None:
            raise HTTPException(400, "O ZIP contém arquivo corrompido.")
    except zipfile.BadZipFile as exc:
        raise HTTPException(400, "Arquivo ZIP inválido.") from exc
    entries = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        path = _safe_zip_name(info.filename)
        parts = path.split("/")
        filename = parts[-1]
        hierarchy = _resolve_zip_hierarchy(parts)
        if hierarchy is None:
            continue
        course, period, discipline, topic = hierarchy
        lower = filename.lower()
        kind = None
        if lower == "material-principal.pdf": kind = "material"
        elif lower == "resumo.pdf": kind = "resumo"
        elif lower == "questoes.pdf": kind = "questao"
        elif lower == "questoes.json": kind = "questoes_json"
        elif lower == "videos.json": kind = "videos"
        elif lower == "artigos.json": kind = "artigos"
        if kind:
            entries.append({"path": path, "course": course, "period": period, "discipline": discipline,
                            "topic": topic, "filename": filename, "kind": kind, "size": info.file_size})
    if not entries:
        raise HTTPException(400, "Nenhum material reconhecido. Use a estrutura Curso/Período/Disciplina/Assunto.")
    return entries

@router.post("/content/import/preview")
async def import_content_preview(file: UploadFile = File(...), admin: dict = Depends(admin_user)):
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(400, "Envie um arquivo .zip.")
    raw = await file.read()
    if len(raw) > 100 * 1024 * 1024:
        raise HTTPException(413, "O ZIP excede o limite de 100 MB.")
    entries = _parse_content_zip(raw)
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_imports")
    import_id = str(uuid.uuid4())
    await bucket.upload_from_stream(import_id + ".zip", raw, metadata={"import_id": import_id, "admin_id": admin["id"], "temporary": True})
    grouped = {}
    for e in entries:
        key = "/".join([e["course"], e["period"], e["discipline"], e["topic"]])
        grouped.setdefault(key, []).append(e)
    preview = [{"path": key, "files": value} for key, value in grouped.items()]
    conflicts = []
    for e in entries:
        # Detect the deterministic PDF titles up front; JSON URL conflicts are checked on confirmation.
        if e["kind"] in {"material", "resumo", "questao"}:
            cslug = slugify(e["course"]); course = await db.courses.find_one({"slug": cslug}, P)
            if course:
                ps = period_slug(e["period"]); period = await db.periods.find_one({"course_id":course["id"],"slug":ps},P)
                if period:
                    disc = await db.disciplines.find_one({"period_id":period["id"],"slug":slugify(e["discipline"])},P)
                    if disc:
                        topic = await db.topics.find_one({"discipline_id":disc["id"],"slug":slugify(e["topic"])},P)
                        if topic:
                            title = {"material":"Material Principal","resumo":"Resumo","questao":"Questões"}[e["kind"]]
                            if await db.contents.find_one({"topic_id":topic["id"],"type":e["kind"],"title":title}):
                                conflicts.append(e["path"])
    await db.content_imports.insert_one({"id": import_id, "gridfs_name": import_id + ".zip", "filename": file.filename,
                                         "entries": entries, "created_at": now_utc(), "admin_id": admin["id"], "status": "preview"})
    await log_admin(admin, "gerou prévia de importação ZIP", "conteúdo", import_id)
    return {"import_id": import_id, "filename": file.filename, "entries": len(entries), "groups": preview, "conflicts": conflicts}

async def _find_or_create_hierarchy(course_name: str, period_name_value: str, discipline_name: str, topic_name: str):
    cs = slugify(course_name)
    course = await db.courses.find_one({"slug": cs}, P)
    if not course:
        course = {"id": str(uuid.uuid4()), "name": course_name.replace("_", " "), "slug": cs, "description": "",
                  "icon": "GraduationCap", "num_periods": 1, "status": "publicado"}
        await db.courses.insert_one(course)
    ps = slugify(period_name_value)
    period = await db.periods.find_one({"course_id": course["id"], "slug": ps}, P)
    if not period:
        nums = re.findall(r"\d+", period_name_value)
        number = int(nums[0]) if nums else (await db.periods.count_documents({"course_id": course["id"]}) + 1)
        period = {"id": str(uuid.uuid4()), "course_id": course["id"], "number": number,
                  "name": period_name_value.replace("_", " "), "slug": ps}
        await db.periods.insert_one(period)
    if int(course.get("num_periods", 0) or 0) < int(period["number"]):
        await db.courses.update_one(
            {"id": course["id"]},
            {"$set": {"num_periods": int(period["number"]), "updated_at": now_utc()}},
        )
        course["num_periods"] = int(period["number"])
    ds = slugify(discipline_name)
    discipline = await db.disciplines.find_one({"period_id": period["id"], "slug": ds}, P)
    if not discipline:
        discipline = {"id": str(uuid.uuid4()), "course_id": course["id"], "period_id": period["id"],
                      "name": discipline_name.replace("_", " "), "slug": ds, "description": "", "status": "publicado"}
        await db.disciplines.insert_one(discipline)
    ts = slugify(topic_name)
    topic = await db.topics.find_one({"discipline_id": discipline["id"], "slug": ts}, P)
    if not topic:
        topic = {"id": str(uuid.uuid4()), "course_id": course["id"], "period_id": period["id"],
                 "discipline_id": discipline["id"], "name": topic_name.replace("_", " "), "slug": ts,
                 "description": "", "status": "publicado"}
        await db.topics.insert_one(topic)
    return course, period, discipline, topic

async def _store_import_content(bucket, topic: dict, kind: str, filename: str, data: bytes, meta: dict):
    if kind in {"material", "resumo", "questao"}:
        file_id = await bucket.upload_from_stream(filename, data, metadata={"content_type": "application/pdf", "topic_id": topic["id"], "imported": True})
        ctype = kind
        title = {"material": "Material Principal", "resumo": "Resumo", "questao": "Questões"}[kind]
        existing = await db.contents.find_one({"topic_id": topic["id"], "type": ctype, "title": title})
        if existing:
            return "duplicate"
        doc = {"id": str(uuid.uuid4()), "type": ctype, "topic_id": topic["id"], "title": title,
               "description": "", "tags": ["importado"], "difficulty": "", "status": "publicado", "views": 0, "locked": False,
               "created_at": now_utc(), "updated_at": now_utc(),
               "data": {"pdf_url": f"/api/uploads/{file_id}", "file_name": filename, "imported": True}}
        await db.contents.insert_one(await denormalize_content(doc))
        return "created"
    payload = json.loads(data.decode("utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{filename} deve conter uma lista JSON.")

    if kind == "questoes_json":
        created = 0
        for item in payload:
            if not isinstance(item, dict):
                continue
            statement = str(item.get("statement") or item.get("pergunta") or item.get("question") or "").strip()
            options = item.get("options") or item.get("alternativas")
            if not statement or not isinstance(options, list) or len(options) < 2:
                continue
            options = [str(x).strip() for x in options[:5]]
            if any(not x for x in options):
                continue
            correct = item.get("correct_index")
            if correct is None:
                correct = item.get("resposta_correta", item.get("correct"))
            if isinstance(correct, str):
                text = correct.strip()
                if text.upper() in {"A", "B", "C", "D", "E"}:
                    correct = ord(text.upper()) - ord("A")
                elif text.isdigit():
                    correct = int(text)
                else:
                    try:
                        correct = options.index(text)
                    except ValueError:
                        continue
            try:
                correct = int(correct)
            except (TypeError, ValueError):
                continue
            if correct < 0 or correct >= len(options):
                continue
            title = statement
            difficulty = str(item.get("difficulty") or item.get("dificuldade") or "")
            explanation = str(item.get("explanation") or item.get("explicacao") or "")
            duplicate = await db.contents.find_one({
                "topic_id": topic["id"], "type": "questao",
                "data.statement": statement,
            })
            if duplicate:
                continue
            doc = {
                "id": str(uuid.uuid4()), "type": "questao", "topic_id": topic["id"],
                "title": title, "description": "", "tags": ["importado"],
                "difficulty": difficulty if difficulty in {"", "facil", "medio", "dificil"} else "",
                "status": "publicado", "views": 0, "locked": False,
                "created_at": now_utc(), "updated_at": now_utc(),
                "data": {
                    "statement": statement, "options": options,
                    "correct_index": correct, "explanation": explanation,
                    "imported": True,
                },
            }
            await db.contents.insert_one(await denormalize_content(doc))
            created += 1
        return f"created:{created}"

    created = 0
    for item in payload:
        if not isinstance(item, dict) or not item.get("url") or not item.get("titulo"):
            continue
        ctype = "video" if kind == "videos" else "artigo"
        url = str(item["url"]).strip()
        if await db.contents.find_one({"topic_id": topic["id"], "type": ctype, "data.url": url}):
            continue
        title = str(item["titulo"]).strip()
        data_doc = dict(item)
        if kind == "artigos":
            data_doc.update({"url": url, "source": item.get("source") or item.get("fonte", ""),
                             "authors": item.get("authors") or item.get("autores", ""),
                             "year": str(item.get("year") or item.get("ano") or ""),
                             "journal": item.get("journal") or item.get("periodico") or "",
                             "doi": item.get("doi") or ""})
        else:
            data_doc.update({"url": url, "source": item.get("source") or item.get("fonte") or "YouTube"})
        doc = {"id": str(uuid.uuid4()), "type": ctype, "topic_id": topic["id"], "title": title,
               "description": str(item.get("descricao") or item.get("description") or ""), "tags": ["importado"],
               "difficulty": "", "status": "publicado", "views": 0, "locked": False,
               "created_at": now_utc(), "updated_at": now_utc(), "data": data_doc}
        await db.contents.insert_one(await denormalize_content(doc))
        created += 1
    return f"created:{created}"

@router.post("/content/import/{import_id}/confirm")
async def import_content_confirm(import_id: str, body: dict = {}, admin: dict = Depends(admin_user)):
    package = await db.content_imports.find_one({"id": import_id, "admin_id": admin["id"], "status": "preview"}, P)
    if not package:
        raise HTTPException(404, "Prévia de importação não encontrada ou já processada.")
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_imports")
    stream = await bucket.open_download_stream_by_name(package["gridfs_name"])
    raw = await stream.read()
    if not raw:
        raise HTTPException(404, "Arquivo temporário da importação não encontrado.")
    zf = zipfile.ZipFile(io.BytesIO(raw))
    files_map = {_safe_zip_name(i.filename): zf.read(i) for i in zf.infolist() if not i.is_dir()}
    storage = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
    results = []
    for e in package["entries"]:
        try:
            _, _, _, topic = await _find_or_create_hierarchy(e["course"], e["period"], e["discipline"], e["topic"])
            decision = str((body.get("decisions") or {}).get(e["path"], "keep")).lower()
            if decision not in {"keep", "replace", "cancel"}:
                decision = "keep"
            if decision == "cancel":
                results.append({"path": e["path"], "result": "cancelled"})
                continue
            if decision == "replace":
                ctype = {"material":"material","resumo":"resumo","questao":"questao","questoes_json":"questao"}.get(e["kind"])
                if ctype:
                    await db.contents.delete_many({"topic_id": topic["id"], "type": ctype, "title": {"$in": ["Material Principal","Resumo","Questões"]}})
                else:
                    ctype = "video" if e["kind"] == "videos" else "artigo"
                    # URLs are checked again during insertion.
            result = await _store_import_content(storage, topic, e["kind"], e["filename"], files_map[e["path"]], e)
            results.append({"path": e["path"], "result": result})
        except Exception as exc:
            results.append({"path": e["path"], "result": "error", "error": str(exc)[:300]})
    await db.content_imports.update_one({"id": import_id}, {"$set": {"status": "confirmed", "confirmed_at": now_utc(), "results": results}})
    await log_admin(admin, "confirmou importação ZIP", "conteúdo", import_id)
    return {"import_id": import_id, "results": results}

@router.delete("/content/import/{import_id}")
async def import_content_cancel(import_id: str, admin: dict = Depends(admin_user)):
    package = await db.content_imports.find_one({"id": import_id, "admin_id": admin["id"], "status": "preview"}, P)
    if not package:
        raise HTTPException(404, "Prévia de importação não encontrada.")
    await db.content_imports.update_one({"id": import_id}, {"$set": {"status": "cancelled", "cancelled_at": now_utc()}})
    return {"message": "Importação cancelada."}

# ---------- site editor ----------
@router.get("/site-config")
async def get_site_config():
    doc = await db.site_config.find_one({"id": "global"}, P)
    if not doc:
        doc = {"id": "global", "home_texts": {}, "sections": {}, "features": {}, "material_types": ["material","resumo","questao","video","artigo"]}
        await db.site_config.insert_one(doc)
    return doc

@router.put("/site-config")
async def update_site_config(body: dict, admin: dict = Depends(admin_user)):
    allowed = {"home_texts", "sections", "features", "material_types"}
    clean = {k: body[k] for k in allowed if k in body}
    await db.site_config.update_one({"id": "global"}, {"$set": clean, "$setOnInsert": {"id": "global"}}, upsert=True)
    await log_admin(admin, "editou configuração do site", "site", "global")
    return await get_site_config()


# ---------- users ----------
@router.get("/users", response_model=list[AdminUser])
async def a_users(q: str = ""):
    flt = {"name": {"$regex": re.escape(q), "$options": "i"}} if q else {}
    users = await db.users.find(flt, P).sort("created_at", -1).limit(200).to_list(200)
    out = []
    for u in users:
        out.append(AdminUser(id=u["id"], name=u["name"], email_masked=mask_email(u["email"]), role=u.get("role", "student"),
                             status=u.get("status", "ativo"), plan=("ilimitado" if u.get("admin_plan") in {"mensal", "ilimitado"} else "limitado"), created_at=u["created_at"], last_login_at=u.get("last_login_at")))
    return out


@router.patch("/users/{uid}", response_model=Message)
async def a_user_patch(uid: str, body: AdminUserPatch, admin: dict = Depends(admin_user)):
    if uid == admin["id"]:
        raise HTTPException(400, "Você não pode alterar a sua própria conta por aqui.")
    upd = body.model_dump(exclude_none=True)
    if "plan" in upd:
        upd["admin_plan"] = upd.pop("plan")
    if not upd:
        return Message(message="Nenhuma alteração necessária.")
    if "status" in upd:
        upd_inc = {"$inc": {"token_version": 1}} if upd["status"] == "bloqueado" else {}
    else:
        upd_inc = {}
    res = await db.users.update_one({"id": uid}, {"$set": upd, **upd_inc})
    if not res.matched_count:
        raise HTTPException(404, "Usuário não encontrado.")
    await log_admin(admin, f"atualizou {', '.join(f'{k}={v}' for k, v in upd.items())}", "usuário", uid)
    return Message(message="Usuário atualizado.")



# ---------- moderation & logs ----------
@router.get("/submissions", response_model=list[Submission])
async def a_submissions(status: str = ""):
    return await db.submissions.find({"status": status} if status else {}, P).sort("created_at", -1).to_list(500)


@router.patch("/submissions/{sid}", response_model=Message)
async def a_submission_patch(sid: str, body: SubmissionPatch, admin: dict = Depends(admin_user)):
    sub = await db.submissions.find_one({"id": sid}, P)
    if not sub:
        raise HTTPException(404, "Envio não encontrado.")
    if body.status == "publicado" and sub["status"] != "publicado":
        ctype = {"resumo": "resumo", "questao": "material", "material": "material"}[sub["kind"]]
        doc = await denormalize_content({"type": ctype, "title": sub["title"], "description": f"Enviado por {sub['user_name']}",
                                         "topic_id": sub["topic_id"], "tags": ["comunidade"], "difficulty": "", "status": "publicado",
                                         "data": {"body": sub["body"]}, "id": str(uuid.uuid4()), "views": 0, "locked": False,
                                         "created_at": now_utc()})
        await db.contents.insert_one(doc)
    await db.submissions.update_one({"id": sid}, {"$set": {"status": body.status, "reviewer_note": body.reviewer_note}})
    await log_admin(admin, f"moderou ({body.status})", "envio", sid)
    return Message(message="Envio atualizado.")


@router.get("/logs", response_model=list[AdminLog])
async def a_logs():
    return await db.admin_logs.find({}, P).sort("at", -1).limit(200).to_list(200)


# ---------- settings ----------
@router.get("/settings", response_model=Settings)
async def a_settings():
    return await get_settings()


@router.put("/settings", response_model=Settings)
async def a_settings_update(body: SettingsIn, admin: dict = Depends(admin_user)):
    await save_stripe_config(body.stripe.model_dump(), admin_id=admin["id"])
    doc = {
        "id": "global",
        "platform_name": body.platform_name,
        "support_email": str(body.support_email),
        "default_daily_goal_minutes": body.default_daily_goal_minutes,
        "allow_registration": body.allow_registration,
        "features": body.features.model_dump(),
        "updated_at": now_utc(),
        "updated_by": admin["name"],
    }
    await db.settings.update_one({"id": "global"}, {"$set": doc}, upsert=True)
    await log_admin(admin, "atualizou", "configurações")
    return await get_settings()


@router.post("/change-password", response_model=Message)
async def a_change_password(body: ChangePasswordIn, admin: dict = Depends(admin_user)):
    if body.new_password != body.new_password_confirm:
        raise HTTPException(400, "As senhas não coincidem.")
    validate_password_strength(body.new_password)
    user = await db.users.find_one({"id": admin["id"]})
    if not user or not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(400, "Senha atual incorreta.")
    await db.users.update_one({"id": admin["id"]}, {"$set": {"password_hash": hash_password(body.new_password)}})
    await log_admin(admin, "alterou a própria senha", "conta")
    return Message(message="Senha alterada com sucesso.")
