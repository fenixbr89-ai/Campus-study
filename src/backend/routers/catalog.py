"""Public catalog: courses → periods → disciplines → topics → contents, plus global search."""

import math
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from lib.auth import optional_user, current_user
from lib.content import present_content, visible_content_query
from lib.db import db
from lib.security import now_utc
from models.schemas import (
    Content, Course, CourseDetail, Discipline, DisciplineDetail, Period, PeriodWithDisciplines, SearchOut, Topic,
    TopicDetail, TopicHit, GlobalSearchItem, GlobalSearchOut,
)

router = APIRouter(tags=["catalog"])
PUB = {"status": "publicado"}
P = {"_id": 0}


async def _course(slug: str) -> dict:
    c = await db.courses.find_one({"slug": slug, **PUB}, P)
    if not c:
        raise HTTPException(404, "Curso não encontrado.")
    return c


async def _chain(c: str, p: str, d: str) -> tuple[dict, dict, dict]:
    course = await _course(c)
    period = await db.periods.find_one({"course_id": course["id"], "slug": p}, P)
    if not period:
        raise HTTPException(404, "Período não encontrado.")
    disc = await db.disciplines.find_one({"period_id": period["id"], "slug": d, **PUB}, P)
    if not disc:
        raise HTTPException(404, "Disciplina não encontrada.")
    return course, period, disc


@router.get("/courses", response_model=list[Course])
async def list_courses():
    return await db.courses.find(PUB, P).sort("name", 1).to_list(500)


@router.get("/courses/{c}", response_model=CourseDetail)
async def course_detail(c: str):
    course = await _course(c)
    periods = await db.periods.find({"course_id": course["id"]}, P).sort("number", 1).to_list(50)
    discs = await db.disciplines.find({"course_id": course["id"], **PUB}, P).sort("name", 1).to_list(1000)
    out = [PeriodWithDisciplines(**p, disciplines=[Discipline(**d) for d in discs if d["period_id"] == p["id"]]) for p in periods]
    return CourseDetail(course=Course(**course), periods=out)


@router.get("/courses/{c}/{p}/{d}", response_model=DisciplineDetail)
async def discipline_detail(c: str, p: str, d: str, user: dict | None = Depends(optional_user)):
    course, period, disc = await _chain(c, p, d)
    topics = await db.topics.find({"discipline_id": disc["id"], **PUB}, P).sort("name", 1).to_list(500)
    return DisciplineDetail(course=Course(**course), period=Period(**period), discipline=Discipline(**disc),
                            topics=[Topic(**t) for t in topics], contents=[])


@router.get("/courses/{c}/{p}/{d}/{t}", response_model=TopicDetail)
async def topic_detail(c: str, p: str, d: str, t: str, user: dict | None = Depends(optional_user)):
    course, period, disc = await _chain(c, p, d)
    topic = await db.topics.find_one({"discipline_id": disc["id"], "slug": t, **PUB}, P)
    if not topic:
        raise HTTPException(404, "Assunto não encontrado.")
    docs = await db.contents.find({"topic_id": topic["id"], **PUB, **visible_content_query(user)}, P).sort("created_at", -1).to_list(500)
    completed, fav_ids = False, []
    if user:
        completed = bool(await db.progress.find_one({"user_id": user["id"], "topic_id": topic["id"]}))
        favs = await db.favorites.find({"user_id": user["id"]}, P).to_list(2000)
        fav_ids = [f["content_id"] for f in favs]
    return TopicDetail(course=Course(**course), period=Period(**period), discipline=Discipline(**disc),
                       topic=Topic(**topic), contents=[Content(**present_content(x, user)) for x in docs],
                       completed=completed, favorite_ids=fav_ids)


@router.get("/contents/{cid}", response_model=Content)
async def get_content(cid: str, user: dict | None = Depends(optional_user)):
    doc = await db.contents.find_one({"id": cid, **PUB}, P)
    if not doc:
        raise HTTPException(404, "Conteúdo não encontrado.")
    return Content(**present_content(doc, user))


@router.post("/contents/{cid}/view", response_model=Content)
async def view_content(cid: str, user: dict | None = Depends(optional_user)):
    doc = await db.contents.find_one_and_update({"id": cid, **PUB}, {"$inc": {"views": 1}}, projection=P)
    if not doc:
        raise HTTPException(404, "Conteúdo não encontrado.")
    return Content(**present_content(doc, user))


@router.get("/smart-search")
async def smart_search(q: str = "", user: dict | None = Depends(optional_user)):
    import unicodedata
    import re as _re
    raw = q.strip()[:200]
    if not raw:
        raise HTTPException(400, "Digite o que você quer encontrar.")
    norm = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode().lower()
    norm = _re.sub(r"\s+", " ", norm).strip()
    period_match = _re.search(r"(?:^|\s)(\d{1,2})\s*(?:º|°|o|a)?\s*(?:periodo|semestre)(?:$|\s)", norm)
    period_number = int(period_match.group(1)) if period_match else None

    courses = await db.courses.find(PUB, P).to_list(500)
    best_course = None
    best_course_score = -1
    for cdoc in courses:
        name = unicodedata.normalize("NFKD", cdoc["name"]).encode("ascii", "ignore").decode().lower()
        score = 100 if norm == name else (80 if _re.search(rf"\b{_re.escape(name)}\b", norm) else (40 if all(tok in norm for tok in name.split() if len(tok)>2) else -1))
        if score > best_course_score:
            best_course, best_course_score = cdoc, score

    period_doc = None
    if best_course and period_number:
        period_doc = await db.periods.find_one({"course_id":best_course["id"],"number":period_number},P)

    discipline_docs = await db.disciplines.find(PUB if not best_course else {"course_id":best_course["id"], **PUB},P).to_list(5000)
    best_disc = None
    best_disc_score = -1
    for dd in discipline_docs:
        name = unicodedata.normalize("NFKD", dd["name"]).encode("ascii", "ignore").decode().lower()
        if norm == name:
            score=110
        elif _re.search(rf"\b{_re.escape(name)}\b", norm):
            score=100+min(len(name),30)
        elif all(tok in norm for tok in name.split() if len(tok)>2):
            score=60+min(len(name),20)
        else:
            score=-1
        if period_doc and dd.get("period_id") != period_doc["id"]:
            score -= 50
        if score > best_disc_score:
            best_disc,best_disc_score=dd,score

    if best_disc:
        topic_query = {"discipline_id": best_disc["id"], **PUB}
    elif best_course:
        topic_query = {"course_id": best_course["id"], **PUB}
    else:
        topic_query = PUB
    topic_docs = await db.topics.find(topic_query, P).to_list(20000)
    best_topic=None; best_topic_score=-1
    for td in topic_docs:
        name=unicodedata.normalize("NFKD",td["name"]).encode("ascii","ignore").decode().lower()
        if norm == name: score=120
        elif _re.search(rf"\b{_re.escape(name)}\b", norm): score=100+min(len(name),30)
        elif all(tok in norm for tok in name.split() if len(tok)>2): score=70+min(len(name),20)
        else: score=-1
        if period_doc and td.get("period_id") != period_doc["id"]: score -= 40
        if score>best_topic_score: best_topic,best_topic_score=td,score

    if best_topic and best_topic_score >= 70:
        cdoc = best_course or await db.courses.find_one({"id":best_topic["course_id"]},P)
        pdoc = await db.periods.find_one({"id":best_topic["period_id"]},P)
        ddoc = best_disc or await db.disciplines.find_one({"id":best_topic["discipline_id"]},P)
        return {"type":"topic","path":f"/cursos/{cdoc['slug']}/{pdoc['slug']}/{ddoc['slug']}/{best_topic['slug']}","query":raw,"course":cdoc["name"],"period":pdoc["name"],"discipline":ddoc["name"],"topic":best_topic["name"]}
    if best_disc and best_disc_score >= 70:
        cdoc = best_course or await db.courses.find_one({"id":best_disc["course_id"]},P)
        pdoc = period_doc or await db.periods.find_one({"id":best_disc["period_id"]},P)
        return {"type":"discipline","path":f"/cursos/{cdoc['slug']}/{pdoc['slug']}/{best_disc['slug']}","query":raw,"course":cdoc["name"],"period":pdoc["name"],"discipline":best_disc["name"],"topic":""}
    if best_course and best_course_score >= 40:
        return {"type":"course","path":f"/cursos/{best_course['slug']}","query":raw,"course":best_course["name"],"period":period_doc["name"] if period_doc else "","discipline":"","topic":""}
    return {"type":"search","path":f"/pesquisa?q={__import__('urllib.parse').parse.quote(raw)}","query":raw,"course":"","period":"","discipline":"","topic":""}

@router.get("/global-search", response_model=GlobalSearchOut)
async def global_search(q: str = "", user: dict = Depends(current_user)):
    term = q.strip()[:80]
    if not term:
        return GlobalSearchOut(query="", items=[], total=0)
    rx = re.escape(term)
    items: list[GlobalSearchItem] = []
    # Catalog lookups are bounded and use the same published data as the normal search.
    courses = await db.courses.find({"status": "publicado", "name": {"$regex": rx, "$options": "i"}}, P).sort("name", 1).limit(5).to_list(5)
    items.extend(GlobalSearchItem(id=c["id"], kind="curso", title=c["name"], path=f"/cursos/{c['slug']}") for c in courses)
    # Periods and disciplines are also first-class searchable catalog entries.
    matching_periods = await db.periods.find({"name": {"$regex": rx, "$options": "i"}}, P).sort("number", 1).limit(8).to_list(8)
    for period in matching_periods:
        course = await db.courses.find_one({"id": period.get("course_id"), "status": "publicado"}, P)
        if course:
            items.append(GlobalSearchItem(id=period["id"], kind="período", title=period["name"], subtitle=course["name"], path=f"/cursos/{course['slug']}/{period['slug']}"))
    matching_discs = await db.disciplines.find({"status": "publicado", "name": {"$regex": rx, "$options": "i"}}, P).sort("name", 1).limit(8).to_list(8)
    for disc in matching_discs:
        course = await db.courses.find_one({"id": disc.get("course_id"), "status": "publicado"}, P)
        period = await db.periods.find_one({"id": disc.get("period_id")}, P)
        if course and period:
            items.append(GlobalSearchItem(id=disc["id"], kind="disciplina", title=disc["name"], subtitle=f"{period['name']} · {course['name']}", path=f"/cursos/{course['slug']}/{period['slug']}/{disc['slug']}"))
    topics = await db.topics.find({"status": "publicado", "name": {"$regex": rx, "$options": "i"}}, P).sort("name", 1).limit(10).to_list(10)
    for t in topics:
        course = await db.courses.find_one({"id": t["course_id"]}, P); period = await db.periods.find_one({"id": t["period_id"]}, P); disc = await db.disciplines.find_one({"id": t["discipline_id"]}, P)
        if course and period and disc:
            items.append(GlobalSearchItem(id=t["id"], kind="assunto", title=t["name"], subtitle=f"{disc['name']} · {period['name']} · {course['name']}", path=f"/cursos/{course['slug']}/{period['slug']}/{disc['slug']}/{t['slug']}"))
    content_docs = await db.contents.find(
        {"status": "publicado", **visible_content_query(user), "$or": [
            {"search_text": {"$regex": rx, "$options": "i"}},
            {"title": {"$regex": rx, "$options": "i"}},
            {"description": {"$regex": rx, "$options": "i"}},
        ]},
        {"_id": 0, "id": 1, "title": 1, "path": 1, "type": 1, "created_at": 1, "views": 1}
    ).sort("views", -1).limit(12).to_list(12)
    items.extend(GlobalSearchItem(id=c["id"], kind="conteúdo", title=c["title"], subtitle=c.get("type", ""), path=c.get("path", ""), created_at=c.get("created_at")) for c in content_docs)
    notes = await db.notes.find({"user_id": user["id"], "$or": [{"title": {"$regex": rx, "$options": "i"}}, {"body": {"$regex": rx, "$options": "i"}}]}, P).sort("updated_at", -1).limit(8).to_list(8)
    items.extend(GlobalSearchItem(id=n["id"], kind="anotação", title=n["title"], subtitle=n["body"][:140], path="/anotacoes", created_at=n.get("updated_at")) for n in notes)
    fav_ids = [x["content_id"] for x in await db.favorites.find({"user_id": user["id"]}, P).limit(200).to_list(200)]
    if fav_ids:
        favs = await db.contents.find({
            "id": {"$in": fav_ids},
            "status": "publicado",
            **visible_content_query(user),
            "$or": [
                {"search_text": {"$regex": rx, "$options": "i"}},
                {"title": {"$regex": rx, "$options": "i"}},
                {"description": {"$regex": rx, "$options": "i"}},
            ],
        }, {"_id": 0, "id": 1, "title": 1, "path": 1}).limit(8).to_list(8)
        items.extend(GlobalSearchItem(id=c["id"], kind="favorito", title=c["title"], subtitle="Salvo na Minha Biblioteca", path=c.get("path", "")) for c in favs)
    unique: dict[tuple[str, str], GlobalSearchItem] = {}
    for item in items:
        unique[(item.kind, item.id)] = item
    result = list(unique.values())[:40]
    return GlobalSearchOut(query=term, items=result, total=len(result))


@router.get("/search", response_model=SearchOut)
async def search(
    q: str = "", course_id: str = "", period_id: str = "", discipline_id: str = "", topic_id: str = "",
    type: str = "", difficulty: str = "", sort: str = Query("relevancia", pattern="^(relevancia|recentes|populares)$"),
    page: int = Query(1, ge=1), user: dict | None = Depends(optional_user),
):
    size = 12
    base: dict = {**PUB, **visible_content_query(user)}
    for field, val in (("course_id", course_id), ("period_id", period_id), ("discipline_id", discipline_id),
                       ("topic_id", topic_id), ("difficulty", difficulty)):
        if val:
            base[field] = val
    term = q.strip()[:100]
    if term:
        base["search_text"] = {"$regex": re.escape(term), "$options": "i"}
        await db.search_logs.update_one({"term": term.lower()}, {"$inc": {"count": 1}, "$set": {"at": now_utc()}}, upsert=True)
    counts_raw = await db.contents.aggregate([{"$match": base}, {"$group": {"_id": "$type", "n": {"$sum": 1}}}]).to_list(20)
    counts = {c["_id"]: c["n"] for c in counts_raw}
    flt = {**base, "type": type} if type else base
    total = await db.contents.count_documents(flt)
    order = {"recentes": [("created_at", -1)], "populares": [("views", -1)]}.get(sort, [("views", -1), ("created_at", -1)])
    docs = await db.contents.find(flt, P).sort(order).skip((page - 1) * size).limit(size).to_list(size)
    if sort == "relevancia" and term:
        low = term.lower()
        docs.sort(key=lambda x: (low not in x["title"].lower(), -x.get("views", 0)))
    topics: list[TopicHit] = []
    if term and page == 1:
        tq = {"name": {"$regex": re.escape(term), "$options": "i"}, **PUB}
        if course_id:
            tq["course_id"] = course_id
        for t in await db.topics.find(tq, P).limit(8).to_list(8):
            course = await db.courses.find_one({"id": t["course_id"]}, P)
            period = await db.periods.find_one({"id": t["period_id"]}, P)
            disc = await db.disciplines.find_one({"id": t["discipline_id"]}, P)
            if course and period and disc:
                topics.append(TopicHit(id=t["id"], name=t["name"], discipline_name=disc["name"], course_name=course["name"],
                                       path=f"/cursos/{course['slug']}/{period['slug']}/{disc['slug']}/{t['slug']}"))
    return SearchOut(items=[Content(**present_content(x, user)) for x in docs], total=total, page=page,
                     pages=max(1, math.ceil(total / size)), counts=counts, topics=topics)


@router.get("/filters/periods", response_model=list[Period])
async def filter_periods(course_id: str):
    return await db.periods.find({"course_id": course_id}, P).sort("number", 1).to_list(50)


@router.get("/filters/disciplines", response_model=list[Discipline])
async def filter_disciplines(period_id: str = "", course_id: str = ""):
    q: dict = dict(PUB)
    if period_id:
        q["period_id"] = period_id
    if course_id:
        q["course_id"] = course_id
    return await db.disciplines.find(q, P).sort("name", 1).to_list(1000)


@router.get("/filters/topics", response_model=list[Topic])
async def filter_topics(discipline_id: str):
    return await db.topics.find({"discipline_id": discipline_id, **PUB}, P).sort("name", 1).to_list(1000)


@router.get("/sitemap.xml")
async def sitemap(request: Request):
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    base_url = ("http://" if host.startswith("localhost") else "https://") + host
    urls = ["/", "/cursos", "/termos-de-uso", "/politica-de-privacidade"]
    courses = {c["id"]: c for c in await db.courses.find(PUB, P).to_list(500)}
    periods = {p["id"]: p for p in await db.periods.find({}, P).to_list(5000)}
    discs = {d["id"]: d for d in await db.disciplines.find(PUB, P).to_list(10000)}
    for c in courses.values():
        urls.append(f"/cursos/{c['slug']}")
    for d in discs.values():
        c, p = courses.get(d["course_id"]), periods.get(d["period_id"])
        if c and p:
            urls.append(f"/cursos/{c['slug']}/{p['slug']}/{d['slug']}")
    for t in await db.topics.find(PUB, P).to_list(20000):
        c, p, d = courses.get(t["course_id"]), periods.get(t["period_id"]), discs.get(t["discipline_id"])
        if c and p and d:
            urls.append(f"/cursos/{c['slug']}/{p['slug']}/{d['slug']}/{t['slug']}")
    body = "".join(f"<url><loc>{base_url}{u}</loc></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'
    return Response(content=xml, media_type="application/xml")
