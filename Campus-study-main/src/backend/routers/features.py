"""Student productivity/gamification and administrator student-management features."""
import secrets
import string
import uuid
from datetime import date, datetime, timedelta
from typing import Any
import re
import asyncio
import httpx
from urllib.parse import quote_plus, urlparse
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from lib.auth import current_user, admin_user, log_admin
from lib.db import db
from lib.content import topic_context
from lib.dates import today_iso
from lib.security import cpf_hash, hash_password, now_utc, validate_password_strength
from curated_resources import CURATED_RESOURCES
from models.schemas import (
    AccessGrantIn, AdminStudent, Message, Note, NoteIn, Notification, RankingEntry,
    StudentPasswordResetIn, StudyPlanOut, StudyPlanTask, ResourceSearchIn, ResourceSearchOut, ResourceResult,
    ResourceSyncStartIn, PersonalStudyPlan, PersonalStudyPlanIn, PersonalStudyPlanOut, PersonalStudyPlanTask,
    WeeklyGoal, WeeklyGoalIn, CalendarEvent, CalendarOut, ReviewItem, GlobalSearchOut, GlobalSearchItem, StudyHistoryEvent,
)

router = APIRouter(tags=["features"])
P={"_id":0}

def _temp_password(n=12):
    alphabet=string.ascii_letters+string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(n))

@router.get("/admin/students", response_model=list[AdminStudent])
async def admin_students(q: str = "", admin: dict = Depends(admin_user)):
    q=q.strip()
    flt={"role":"student"}
    if q:
        digits=''.join(c for c in q if c.isdigit())
        if digits and len(digits)>=4:
            flt={"role":"student", "cpf_masked":{"$regex":digits}}
            if len(digits)==11:
                flt={"role":"student", "cpf_hash":cpf_hash(digits)}
        else:
            flt={"role":"student", "name":{"$regex":q,"$options":"i"}}
    users=await db.users.find(flt,P).sort("created_at",-1).limit(300).to_list(300)
    ids=[u["id"] for u in users]
    grants=await db.access_grants.find({"user_id":{"$in":ids}},P).to_list(2000) if ids else []
    by={i:[] for i in ids}
    for g in grants: by.setdefault(g["user_id"],[]).append(g)
    return [AdminStudent(id=u["id"],name=u["name"],email=u["email"],cpf_masked=u.get("cpf_masked",""),role=u.get("role","student"),status=u.get("status","ativo"),created_at=u["created_at"],last_login_at=u.get("last_login_at"),ranking_opt_in=bool(u.get("ranking_opt_in",False)),access_grants=by.get(u["id"],[]),plan=("ilimitado" if u.get("admin_plan") in {"mensal","ilimitado"} else "limitado")) for u in users]

@router.patch("/admin/students/{uid}", response_model=Message)
async def admin_student_patch(uid: str, body: dict[str, Any], admin: dict=Depends(admin_user)):
    if uid==admin["id"]: raise HTTPException(400,"Não é possível bloquear a própria conta por esta tela.")
    allowed={k:v for k,v in body.items() if k in {"status","ranking_opt_in","admin_plan"}}
    if "admin_plan" in allowed and allowed["admin_plan"] not in {"limitado","ilimitado"}: raise HTTPException(400,"Plano administrativo inválido.")
    if "status" in allowed and allowed["status"] not in {"ativo","bloqueado"}: raise HTTPException(400,"Status inválido.")
    if not allowed:
        return Message(message="Nenhuma alteração necessária.")
    res=await db.users.update_one({"id":uid,"role":"student"},{"$set":allowed})
    if not res.matched_count: raise HTTPException(404,"Aluno não encontrado.")
    await log_admin(admin,"moderou aluno","usuário",uid)
    return Message(message="Aluno atualizado.")

@router.delete("/admin/students/{uid}", response_model=Message)
async def admin_student_delete(uid: str, admin: dict=Depends(admin_user)):
    user=await db.users.find_one({"id":uid,"role":"student"},P)
    if not user: raise HTTPException(404,"Aluno não encontrado.")
    # Remove the student's personal account/data while leaving administrator audit logs intact.
    for coll in ("notes","favorites","history","progress","daily_stats","exams","exam_plans","exam_tasks","study_sessions","study_plans","study_reviews","weekly_goals","user_items","conversations","submissions","notifications","access_grants","password_resets"):
        await db[coll].delete_many({"user_id":uid})
    await db.users.delete_one({"id":uid,"role":"student"})
    await log_admin(admin,"removeu aluno","usuário",uid)
    return Message(message="Aluno removido e dados pessoais excluídos.")

@router.post("/admin/students/{uid}/reset-password")
async def admin_student_reset_password(uid: str, body: StudentPasswordResetIn, admin: dict=Depends(admin_user)):
    user=await db.users.find_one({"id":uid,"role":"student"},P)
    if not user: raise HTTPException(404,"Aluno não encontrado.")
    password=body.password or _temp_password()
    validate_password_strength(password)
    await db.users.update_one({"id":uid},{"$set":{"password_hash":hash_password(password)},"$inc":{"token_version":1}})
    await log_admin(admin,"redefiniu senha do aluno","usuário",uid)
    return {"message":"Senha redefinida. Mostre/guarde a senha temporária com segurança; ela não fica armazenada em texto puro.","temporary_password":password}

@router.post("/admin/students/{uid}/access-grants")
async def admin_grant(uid: str, body: AccessGrantIn, admin: dict=Depends(admin_user)):
    user=await db.users.find_one({"id":uid,"role":"student"},P)
    if not user: raise HTTPException(404,"Aluno não encontrado.")
    expires=now_utc()+timedelta(days=30*body.months_free)
    doc={"id":str(uuid.uuid4()),"user_id":uid,"feature":body.feature,"months_free":body.months_free,"note":body.note,"created_at":now_utc(),"expires_at":expires,"created_by":admin["id"]}
    await db.access_grants.insert_one(doc)
    await log_admin(admin,f"concedeu {body.months_free} mês(es) grátis","acesso",uid)
    return {k:v for k,v in doc.items() if k!="_id"}

@router.delete("/admin/students/{uid}/access-grants/{gid}", response_model=Message)
async def admin_revoke_grant(uid:str,gid:str,admin:dict=Depends(admin_user)):
    r=await db.access_grants.delete_one({"id":gid,"user_id":uid})
    if not r.deleted_count: raise HTTPException(404,"Acesso concedido não encontrado.")
    await log_admin(admin,"removeu concessão de acesso","acesso",uid)
    return Message(message="Acesso concedido removido.")

async def _discover_for_topic(client, course, period, discipline, topic, kind="todos", limit=5):
    terms=" ".join(x.strip() for x in [course,period,discipline,topic] if x.strip())
    kind_terms={"pdf":" filetype:pdf","video":" (vídeo OR videoaula OR aula)","artigo":" (artigo científico OR revisão)","resumo":" resumo","mapa":" (mapa mental OR mapa conceitual)"}
    q=f'{terms} português Brasil {kind_terms.get(kind, "")} -english -espanol'.strip()
    trusted={"scielo.br","scielo.org","gov.br","edu.br","usp.br","ufsc.br","ufrgs.br","ufmg.br","unb.br","ufrj.br","unicamp.br","fiocruz.br","bvsalud.org","arca.fiocruz.br","ares.unasus.gov.br","ncbi.nlm.nih.gov","youtube.com","youtu.be","books.google.com","openstax.org","anvisa.gov.br"}
    r=await client.get("https://html.duckduckgo.com/html/",params={"q":q}); r.raise_for_status(); html=r.text
    results=[]
    for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',html,re.I|re.S):
        url=m.group(1); title=re.sub(r'<[^>]+>',' ',m.group(2)); title=re.sub(r'\s+',' ',title).strip()
        if not url.startswith("http"): continue
        host=urlparse(url).netloc.lower().removeprefix("www.")
        if any(x in host for x in ["duckduckgo.com","facebook.com","instagram.com","pinterest.com"]): continue
        trusted_hit=(host in trusted or any(host.endswith('.'+d) for d in trusted))
        if not trusted_hit and kind in {"pdf","artigo","resumo","mapa"}: continue
        item_kind=kind if kind!="todos" else ("video" if ("youtube." in host or "youtu.be" in host or "video" in url.lower()) else ("pdf" if url.lower().split('?')[0].endswith('.pdf') else ("artigo" if any(k in title.lower() for k in ["artigo","estudo","revisão","revista","doi"]) else "material")))
        verified=False; open_access=False
        try:
            h=await client.get(url,timeout=7)
            ctype=h.headers.get('content-type','').lower(); sample=h.text[:120000] if ('text/' in ctype or 'html' in ctype) else ''
            lang=re.search(r'<html[^>]+lang=["\']([^"\']+)',sample,re.I)
            low=sample.lower()
            pt_markers=sum(low.count(x) for x in [' português',' resumo',' introdução','objetivo',' universidade ',' artigo'])
            verified=bool(lang and lang.group(1).lower().startswith('pt')) or pt_markers>=3
            if ctype.startswith('application/pdf'):
                try:
                    from pypdf import PdfReader
                    import io
                    txt=''.join((p.extract_text() or '')[:3000] for p in PdfReader(io.BytesIO(h.content)).pages[:3])
                    lowtxt=txt.lower()
                    verified=sum(lowtxt.count(x) for x in [' o ',' a ',' de ',' que ',' não ',' para ',' resumo ',' introdução ']) >= 6
                    open_access=True
                except Exception:
                    verified=False
            open_access=open_access or ('open access' in low or 'acesso aberto' in low or 'texto completo' in low)
        except Exception:
            verified=False
        if not verified: continue
        results.append(ResourceResult(title=title,url=url,source=host,kind=item_kind,language='pt-BR',verified=True,open_access=open_access,description=f'Recurso localizado para {terms}.'))
        if len(results)>=limit: break

    # Render/hosted environments can occasionally receive an empty or changed
    # DuckDuckGo result page. Keep the automatic library useful for the verified
    # catalog resources already curated in the project instead of silently ending
    # with zero results.
    if not results:
        wanted_kind = kind if kind in {"pdf", "video", "artigo", "resumo", "mapa"} else None
        norm = lambda value: re.sub(r"\s+", " ", str(value or "").strip().casefold())
        for item in CURATED_RESOURCES:
            if norm(item.get("course")) != norm(course) or norm(item.get("discipline")) != norm(discipline) or norm(item.get("topic")) != norm(topic):
                continue
            if wanted_kind and item.get("kind") != wanted_kind:
                continue
            results.append(ResourceResult(
                title=item["title"], url=item["url"], source=item.get("source", "fonte curada"),
                kind=item.get("kind", "material"), language="pt-BR", verified=True,
                open_access=bool(item.get("open_access", False)),
                description=item.get("description", f"Recurso curado para {terms}."),
            ))
            if len(results) >= limit:
                break
    return q, results

@router.post("/admin/resources/discover", response_model=ResourceSearchOut)
async def discover_resources(body: ResourceSearchIn, admin: dict = Depends(admin_user)):
    course_name, period_name, discipline_name, topic_name = body.course, body.period, body.discipline, body.topic
    if not body.topic_id:
        raise HTTPException(400, "Selecione um assunto específico antes de pesquisar materiais.")
    if body.topic_id:
        topic=await db.topics.find_one({"id":body.topic_id,"status":"publicado"},P)
        if not topic: raise HTTPException(404,"Assunto selecionado não encontrado.")
        course=await db.courses.find_one({"id":topic["course_id"]},P); period=await db.periods.find_one({"id":topic["period_id"]},P); discipline=await db.disciplines.find_one({"id":topic["discipline_id"]},P)
        if not (course and period and discipline): raise HTTPException(409,"O contexto do assunto selecionado está incompleto.")
        if body.discipline_id and body.discipline_id != discipline["id"]: raise HTTPException(400,"O assunto não pertence à disciplina selecionada.")
        if body.period_id and body.period_id != period["id"]: raise HTTPException(400,"O assunto não pertence ao período selecionado.")
        if body.course_id and body.course_id != course["id"]: raise HTTPException(400,"O assunto não pertence ao curso selecionado.")
        course_name, period_name, discipline_name, topic_name = course["name"], period["name"], discipline["name"], topic["name"]
    terms=" ".join(x.strip() for x in [course_name,period_name,discipline_name,topic_name] if x and x.strip())
    if not terms: raise HTTPException(400,"Selecione um contexto de curso, período, disciplina ou assunto.")
    try:
        async with httpx.AsyncClient(timeout=12,follow_redirects=True,headers={"User-Agent":"CampusStudy/1.0","Accept-Language":"pt-BR,pt;q=0.9"}) as client:
            q, results=await _discover_for_topic(client,course_name,period_name,discipline_name,topic_name,body.kind,30)
    except Exception:
        return ResourceSearchOut(results=[],query=terms,note="A busca externa não respondeu agora. Tente novamente mais tarde.")
    await log_admin(admin,"pesquisou materiais externos em português","recursos",terms)
    return ResourceSearchOut(results=results,query=q,note="Resultados validados para português quando a página/PDF permitiu verificação. Revise antes de publicar; links apontam para a fonte original.")

@router.post("/admin/resources/publish", response_model=Message)
async def publish_resource(body: dict[str, Any], admin: dict = Depends(admin_user)):
    topic_id=body.get('topic_id'); url=body.get('url'); title=(body.get('title') or '').strip(); kind=body.get('kind','material')
    if not url or not title: raise HTTPException(400,'title e url são obrigatórios.')
    parsed_url = urlparse(str(url))
    if parsed_url.scheme not in {'http', 'https'} or not parsed_url.netloc:
        raise HTTPException(400,'A URL precisa ser HTTP/HTTPS e apontar para uma fonte externa válida.')
    if not bool(body.get('verified', False)):
        raise HTTPException(400,'Só é permitido publicar um recurso externo após a validação automática de fonte e idioma.')
    topic=await db.topics.find_one({'id':topic_id},P) if topic_id else None
    if not topic:
        cname, pname, dname, tname = [str(body.get(k,'')).strip() for k in ('course','period','discipline','topic')]
        course=await db.courses.find_one({'name':{'$regex':re.escape(cname),'$options':'i'}},P) if cname else None
        period=await db.periods.find_one({'course_id':course['id'],'number':int(re.search(r'\d+',pname).group())},P) if course and re.search(r'\d+',pname) else None
        disc=await db.disciplines.find_one({'period_id':period['id'],'name':{'$regex':re.escape(dname),'$options':'i'}},P) if period and dname else None
        topic=await db.topics.find_one({'discipline_id':disc['id'],'name':{'$regex':re.escape(tname),'$options':'i'}},P) if disc and tname else None
        topic_id=topic['id'] if topic else None
    if not topic_id or not topic: raise HTTPException(404,'Assunto não encontrado.')
    if await db.contents.find_one({'topic_id':topic_id,'data.url':url},P): return Message(message='Este recurso já está publicado neste assunto.')
    ctype=kind if kind in {'video','pdf','artigo','resumo','mapa'} else 'material'
    doc={'type':ctype,'topic_id':topic_id,'title':title,'description':body.get('description','Recurso externo em português.'),'tags':['externo','internet','pt-BR'], 'data':{'url':url,'source':body.get('source',''),'language':'pt-BR','external':True,'open_access':bool(body.get('open_access',False)),'curated':bool(body.get('curated',False)),'verified':True,'verified_at':now_utc().isoformat()}}
    await db.contents.insert_one(await denormalize_content({**doc,'id':str(uuid.uuid4()),'created_at':now_utc(),'updated_at':now_utc(),'status':'publicado','views':0,'locked':False,'difficulty':''}))
    await log_admin(admin,'publicou recurso externo','recurso',topic_id)
    return Message(message='Recurso publicado no assunto.')

async def _resource_job(job_id: str, admin_id: str, topic_ids: list[str]):
    """Process external resources with persistent pause/resume/cancel state."""
    job = await db.resource_sync_jobs.find_one({"id": job_id}, P)
    if not job:
        return
    current_status = job.get("status")
    if current_status not in {"queued", "running"}:
        return
    await db.resource_sync_jobs.update_one(
        {"id": job_id, "status": {"$in": ["queued", "running"]}},
        {"$set": {"status": "running", "started_at": job.get("started_at") or now_utc(), "updated_at": now_utc()}}
    )
    sem = asyncio.Semaphore(4)
    kinds = [job.get("kind")] if job.get("kind") in {"pdf", "video", "artigo", "resumo", "mapa"} else ["pdf", "video", "artigo", "resumo", "mapa"]

    async def is_stopped() -> str:
        fresh = await db.resource_sync_jobs.find_one({"id": job_id}, P)
        return str(fresh.get("status")) if fresh else "cancelled"

    async def one(t):
        async with sem:
            status = await is_stopped()
            if status in {"paused", "cancelled", "failed"}:
                return
            # A topic can be safely skipped after a previous run; this makes resume idempotent.
            fresh = await db.resource_sync_jobs.find_one({"id": job_id}, P)
            if t["id"] in (fresh or {}).get("processed_topic_ids", []):
                return
            disc = await db.disciplines.find_one({"id": t["discipline_id"]}, P)
            course = await db.courses.find_one({"id": t["course_id"]}, P)
            period = await db.periods.find_one({"id": t["period_id"]}, P)
            if not (disc and course and period):
                await db.resource_sync_jobs.update_one(
                    {"id": job_id},
                    {"$inc": {"errors": 1, "processed": 1}, "$addToSet": {"processed_topic_ids": t["id"]},
                     "$set": {"last_topic": t.get("name", ""), "updated_at": now_utc()}}
                )
                return
            await db.resource_queries.update_one(
                {"topic_id": t["id"]},
                {"$set": {
                    "topic_id": t["id"], "course": course["name"], "period": period["name"],
                    "discipline": disc["name"], "topic": t["name"],
                    "query": f"{course['name']} {period['name']} {disc['name']} {t['name']} português Brasil",
                    "last_sync_at": now_utc(), "job_id": job_id
                }}, upsert=True
            )
            topic_errors = 0
            for kind in kinds:
                if await is_stopped() in {"paused", "cancelled"}:
                    return
                try:
                    _, found = await asyncio.wait_for(
                        _discover_for_topic(
                            client, course["name"], period["name"], disc["name"], t["name"], kind, 2
                        ),
                        timeout=20,
                    )
                    for r in found:
                        exists = await db.contents.find_one({"topic_id": t["id"], "data.url": r.url}, P)
                        if exists:
                            continue
                        ctype = r.kind if r.kind in {"video", "pdf", "artigo", "resumo", "mapa"} else "material"
                        doc = {
                            "id": str(uuid.uuid4()), "type": ctype, "topic_id": t["id"], "title": r.title,
                            "description": r.description, "tags": ["externo", "internet", "pt-BR", "auto-curado"],
                            "data": {"url": r.url, "source": r.source, "language": "pt-BR", "external": True,
                                     "open_access": r.open_access, "verified": r.verified, "resource_kind": kind,
                                     "sync_job_id": job_id, "verified_at": now_utc().isoformat()},
                            "status": "publicado", "difficulty": "", "views": 0, "locked": False,
                            "created_at": now_utc(), "updated_at": now_utc()
                        }
                        await db.contents.insert_one(await denormalize_content(doc))
                        await db.resource_sync_jobs.update_one(
                            {"id": job_id}, {"$inc": {"published": 1}, "$set": {"updated_at": now_utc()}}
                        )
                except Exception as exc:
                    topic_errors += 1
                    await db.resource_sync_jobs.update_one(
                        {"id": job_id},
                        {"$set": {"last_error": f"{kind}: {str(exc)[:300]}", "updated_at": now_utc()}}
                    )
            await db.resource_sync_jobs.update_one(
                {"id": job_id},
                {"$inc": {"processed": 1, "errors": topic_errors},
                 "$addToSet": {"processed_topic_ids": t["id"]},
                 "$set": {"last_topic": t["name"], "updated_at": now_utc()}}
            )

    try:
        async with httpx.AsyncClient(
            timeout=12, follow_redirects=True,
            headers={"User-Agent": "CampusStudy/1.0", "Accept-Language": "pt-BR,pt;q=0.9"}
        ) as client:
            docs = await db.topics.find({"id": {"$in": topic_ids}, "status": "publicado"}, P).to_list(20000)
            await asyncio.gather(*(one(t) for t in docs))
        final = await db.resource_sync_jobs.find_one({"id": job_id}, P)
        status = (final or {}).get("status")
        if status == "paused":
            await db.resource_sync_jobs.update_one({"id": job_id}, {"$set": {"updated_at": now_utc()}})
        elif status == "cancelled":
            await db.resource_sync_jobs.update_one({"id": job_id}, {"$set": {"finished_at": now_utc(), "updated_at": now_utc()}})
        else:
            processed = int((final or {}).get("processed", 0))
            total = int((final or {}).get("total", len(topic_ids)))
            await db.resource_sync_jobs.update_one(
                {"id": job_id},
                {"$set": {"status": "completed" if processed >= total else "paused", "finished_at": now_utc() if processed >= total else None, "updated_at": now_utc()}}
            )
            if processed >= total:
                await log_admin(
                    {"id": admin_id}, "executou preenchimento automático da biblioteca", "recursos",
                    f"{processed} assuntos processados"
                )
    except Exception as exc:
        await db.resource_sync_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "failed", "finished_at": now_utc(), "error": str(exc)[:500], "updated_at": now_utc()},
             "$inc": {"errors": 1}}
        )

@router.post("/admin/resources/sync-all/start")
async def start_resource_sync(body: ResourceSyncStartIn, background_tasks: BackgroundTasks, admin: dict = Depends(admin_user)):
    active = await db.resource_sync_jobs.find_one({"status": {"$in": ["queued", "running"]}}, P)
    if active:
        return {"message": "Já existe uma sincronização em andamento.", "job_id": active["id"], "status": active["status"], "total": active.get("total", 0)}
    if not body.topic_id:
        raise HTTPException(400, "Selecione um assunto específico antes de iniciar a busca automática.")
    topic = await db.topics.find_one({"id": body.topic_id, "status": "publicado"}, P)
    if not topic:
        raise HTTPException(404, "O assunto selecionado não foi encontrado.")
    # Never broaden the selected scope: the automatic saver works on exactly one topic.
    for field, expected in (("discipline_id", topic.get("discipline_id")), ("period_id", topic.get("period_id")), ("course_id", topic.get("course_id"))):
        supplied = getattr(body, field)
        if supplied and supplied != expected:
            raise HTTPException(400, "O assunto selecionado não pertence aos filtros informados.")
    topics = [topic]
    if not topics:
        raise HTTPException(404, "Nenhum assunto publicado corresponde aos filtros selecionados.")
    job_id = str(uuid.uuid4()); now = now_utc()
    doc = {"id": job_id, "status": "queued", "total": len(topics), "processed": 0, "published": 0, "errors": 0,
           "processed_topic_ids": [], "topic_ids": [t["id"] for t in topics], "kind": body.kind,
           "filters": {"course_id": body.course_id, "period_id": body.period_id, "discipline_id": body.discipline_id, "topic_id": body.topic_id},
           "started_at": None, "finished_at": None, "created_at": now, "updated_at": now, "last_topic": "", "admin_id": admin["id"]}
    await db.resource_sync_jobs.insert_one(doc)
    background_tasks.add_task(_resource_job, job_id, admin["id"], doc["topic_ids"])
    await log_admin(admin, "iniciou preenchimento automático da biblioteca", "recursos", f"{len(topics)} assunto(s)")
    return {"message": f"Busca iniciada para {len(topics)} assunto(s) selecionado(s).", "job_id": job_id, "status": "queued", "total": len(topics)}

@router.get("/admin/resources/sync-status")
async def resource_sync_status(admin: dict = Depends(admin_user)):
    job = await db.resource_sync_jobs.find_one({}, P, sort=[("created_at", -1)])
    if not job:
        return {"status": "idle", "total": 0, "processed": 0, "published": 0, "errors": 0, "progress": 0}
    total = int(job.get("total", 0)); processed = int(job.get("processed", 0))
    return {**{k: job.get(k) for k in ["id", "status", "total", "processed", "published", "errors", "last_topic", "started_at", "finished_at", "created_at", "error"]},
            "progress": round((processed / total) * 100, 1) if total else 100,
            "last_error": job.get("last_error", "")}

@router.post("/admin/resources/sync-all/pause")
async def pause_resource_sync(admin: dict = Depends(admin_user)):
    job = await db.resource_sync_jobs.find_one({"status": {"$in": ["queued", "running"]}}, P, sort=[("created_at", -1)])
    if not job:
        raise HTTPException(404, "Nenhuma sincronização ativa para pausar.")
    await db.resource_sync_jobs.update_one({"id": job["id"]}, {"$set": {"status": "paused", "updated_at": now_utc()}})
    await log_admin(admin, "pausou preenchimento automático", "recursos", job["id"])
    return {"message": "Sincronização pausada.", "job_id": job["id"], "status": "paused"}

@router.post("/admin/resources/sync-all/cancel")
async def cancel_resource_sync(admin: dict = Depends(admin_user)):
    job = await db.resource_sync_jobs.find_one({"status": {"$in": ["queued", "running", "paused"]}}, P, sort=[("created_at", -1)])
    if not job:
        raise HTTPException(404, "Nenhuma sincronização para cancelar.")
    await db.resource_sync_jobs.update_one({"id": job["id"]}, {"$set": {"status": "cancelled", "finished_at": now_utc(), "updated_at": now_utc()}})
    await log_admin(admin, "cancelou preenchimento automático", "recursos", job["id"])
    return {"message": "Sincronização cancelada. Os recursos já publicados foram preservados.", "job_id": job["id"], "status": "cancelled"}

@router.post("/admin/resources/sync-all/resume")
async def resume_resource_sync(background_tasks: BackgroundTasks, admin: dict = Depends(admin_user)):
    active = await db.resource_sync_jobs.find_one({"status": {"$in": ["queued", "running"]}}, P)
    if active:
        return {"message": "A sincronização já está em execução.", "job_id": active["id"], "status": active["status"]}
    last = await db.resource_sync_jobs.find_one({}, P, sort=[("created_at", -1)])
    if not last or last.get("status") not in {"paused", "failed", "cancelled", "completed"}:
        return {"message": "Não há sincronização anterior para retomar.", "status": "idle"}
    topic_ids = list(last.get("topic_ids") or [])
    if not topic_ids:
        raise HTTPException(409, "A sincronização anterior não possui escopo salvo. Inicie uma nova busca selecionando um assunto.")
    done = set(last.get("processed_topic_ids", []))
    remaining = [tid for tid in topic_ids if tid not in done]
    if not remaining:
        await db.resource_sync_jobs.update_one({"id": last["id"]}, {"$set": {"status": "completed", "finished_at": now_utc(), "updated_at": now_utc()}})
        return {"message": "Todo o catálogo já foi processado.", "job_id": last["id"], "status": "completed", "total": len(topic_ids)}
    await db.resource_sync_jobs.update_one({"id": last["id"]}, {"$set": {"status": "queued", "error": None, "updated_at": now_utc()}})
    background_tasks.add_task(_resource_job, last["id"], admin["id"], topic_ids)
    return {"message": "Sincronização retomada do ponto em que parou.", "job_id": last["id"], "status": "queued", "total": len(topic_ids)}

@router.get("/notes", response_model=list[Note])
async def list_notes(user:dict=Depends(current_user)):
    docs=await db.notes.find({"user_id":user["id"]},P).sort("updated_at",-1).limit(500).to_list(500)
    return [Note(**d) for d in docs]

@router.get("/notes/search", response_model=list[Note])
async def search_notes(q: str = "", user: dict = Depends(current_user)):
    term = q.strip()[:100]
    if not term:
        return await list_notes(user)
    rx = re.escape(term)
    docs = await db.notes.find({"user_id": user["id"], "$or": [{"title": {"$regex": rx, "$options": "i"}}, {"body": {"$regex": rx, "$options": "i"}}]}, P).sort("updated_at", -1).limit(500).to_list(500)
    return [Note(**d) for d in docs]

@router.post("/notes", response_model=Note)
async def create_note(body:NoteIn,user:dict=Depends(current_user)):
    now=now_utc(); d={**body.model_dump(),"id":str(uuid.uuid4()),"user_id":user["id"],"created_at":now,"updated_at":now}
    await db.notes.insert_one(d); return Note(**d)

@router.put("/notes/{nid}", response_model=Note)
async def update_note(nid:str,body:NoteIn,user:dict=Depends(current_user)):
    d=await db.notes.find_one({"id":nid,"user_id":user["id"]},P)
    if not d: raise HTTPException(404,"Anotação não encontrada.")
    upd={**body.model_dump(),"updated_at":now_utc()}; await db.notes.update_one({"id":nid},{"$set":upd}); return Note(**{**d,**upd})

@router.delete("/notes/{nid}", response_model=Message)
async def delete_note(nid:str,user:dict=Depends(current_user)):
    r=await db.notes.delete_one({"id":nid,"user_id":user["id"]})
    if not r.deleted_count: raise HTTPException(404,"Anotação não encontrada.")
    return Message(message="Anotação excluída.")

@router.get("/study-plan", response_model=StudyPlanOut)
async def study_plan(user:dict=Depends(current_user)):
    today=today_iso("America/Sao_Paulo")
    plans=await db.exam_plans.find({"user_id":user["id"],"exam_date":{"$gte":today}},P).sort("exam_date",1).limit(3).to_list(3)
    tasks=[]
    for p in plans:
        docs=await db.exam_tasks.find({"user_id":user["id"],"exam_plan_id":p["id"]},P).sort([("task_date",1),("completed",1)]).limit(300).to_list(300)
        for d in docs:
            tasks.append(StudyPlanTask(id=d["id"],date=d["task_date"],title=d["title"],discipline_name=d["discipline_name"],topic_name=d.get("topic_name"),minutes=d["minutes"],completed=d["completed"],kind=d["kind"]))
    personal = await db.study_plans.find({"user_id": user["id"]}, P).sort("updated_at", -1).limit(10).to_list(10)
    for plan in personal:
        pd = plan.get("task_docs", [])[:300]
        for d in pd:
            tasks.append(StudyPlanTask(id=d["id"], date=d["date"], title=d["title"], discipline_name=d.get("discipline_name", ""), topic_name=d.get("topic_name") or None, minutes=int(d.get("minutes", plan.get("minutes_per_session",60))), completed=bool(d.get("completed", False)), kind="personal"))
    tasks.sort(key=lambda x: (x.date, x.completed, x.title.lower()))
    pending=sum(t.minutes for t in tasks if not t.completed)
    return StudyPlanOut(tasks=tasks,pending_minutes=pending,message=(f"Você tem {pending} minutos pendentes." if pending else "Plano em dia!"))


@router.post("/personal-study-plans", response_model=PersonalStudyPlanOut)
async def create_personal_study_plan(body: PersonalStudyPlanIn, user: dict = Depends(current_user)):
    valid_days={"0","1","2","3","4","5","6"}
    days=[str(d) for d in body.days if str(d) in valid_days]
    if not days: raise HTTPException(400,"Escolha ao menos um dia da semana.")
    topics=[]
    if body.topic_ids:
        topics = await db.topics.find({"id":{"$in":body.topic_ids},"status":"publicado"},P).to_list(100)
    if body.discipline_ids:
        more=await db.topics.find({"discipline_id":{"$in":body.discipline_ids},"status":"publicado"},P).sort("name",1).limit(200).to_list(200)
        by_id={t["id"]:t for t in topics}
        by_id.update({t["id"]:t for t in more})
        topics=list(by_id.values())
    if not topics:
        raise HTTPException(400,"Escolha ao menos uma disciplina ou assunto para o plano.")
    now=now_utc(); pid=str(uuid.uuid4())
    task_docs=[]; topic_i=0
    today=date.fromisoformat(today_iso("America/Sao_Paulo"))
    for offset in range(0, 42):
        day=today + timedelta(days=offset)
        if str(day.weekday()) not in days: continue
        topic=topics[topic_i % len(topics)]; topic_i += 1
        task_docs.append({"id":str(uuid.uuid4()),"date":day.isoformat(),"title":f"Estudar — {topic['name']}","discipline_id":topic.get("discipline_id"),"topic_id":topic["id"],"topic_name":topic["name"],"discipline_name":"","start_time":body.start_time,"minutes":body.minutes_per_session,"completed":False,"completed_at":None})
        if len(task_docs)>=120: break
    # Fill discipline names once, keeping network/database reads bounded.
    dids=list({d.get("discipline_id") for d in task_docs if d.get("discipline_id")})
    discs={d["id"]:d for d in await db.disciplines.find({"id":{"$in":dids}},P).to_list(100)} if dids else {}
    for d in task_docs: d["discipline_name"]=discs.get(d.get("discipline_id"),{}).get("name","")
    doc={"id":pid,"user_id":user["id"],**body.model_dump(),"days":days,"topic_ids":list({t["id"] for t in topics}),"course_id":topics[0].get("course_id"),"period_id":topics[0].get("period_id"),"task_docs":task_docs,"created_at":now,"updated_at":now}
    await db.study_plans.insert_one(doc)
    plan=PersonalStudyPlan(id=pid,title=doc["title"],days=days,start_time=doc["start_time"],minutes_per_session=doc["minutes_per_session"],discipline_ids=doc["discipline_ids"],topic_ids=doc["topic_ids"],course_id=doc.get("course_id"),period_id=doc.get("period_id"),created_at=now,updated_at=now)
    return PersonalStudyPlanOut(plan=plan,tasks=[PersonalStudyPlanTask(plan_id=pid,**d) for d in task_docs])


@router.put("/personal-study-plans/{plan_id}", response_model=PersonalStudyPlanOut)
async def update_personal_study_plan(plan_id: str, body: PersonalStudyPlanIn, user: dict = Depends(current_user)):
    existing = await db.study_plans.find_one({"id": plan_id, "user_id": user["id"]}, P)
    if not existing:
        raise HTTPException(404, "Plano de estudos não encontrado.")
    days=[str(d) for d in body.days if str(d) in {"0","1","2","3","4","5","6"}]
    if not days:
        raise HTTPException(400, "Escolha ao menos um dia da semana.")
    topics=[]
    if body.topic_ids:
        topics=await db.topics.find({"id":{"$in":body.topic_ids},"status":"publicado"},P).to_list(100)
    if body.discipline_ids:
        more=await db.topics.find({"discipline_id":{"$in":body.discipline_ids},"status":"publicado"},P).sort("name",1).limit(200).to_list(200)
        by={t["id"]:t for t in topics}; by.update({t["id"]:t for t in more}); topics=list(by.values())
    if not topics: raise HTTPException(400,"Escolha ao menos uma disciplina ou assunto para o plano.")
    now=now_utc(); task_docs=[]; topic_i=0; today=date.fromisoformat(today_iso("America/Sao_Paulo"))
    for offset in range(42):
        day=today+timedelta(days=offset)
        if str(day.weekday()) not in days: continue
        topic=topics[topic_i%len(topics)]; topic_i+=1
        task_docs.append({"id":str(uuid.uuid4()),"date":day.isoformat(),"title":f"Estudar — {topic['name']}","discipline_id":topic.get("discipline_id"),"topic_id":topic["id"],"topic_name":topic["name"],"discipline_name":"","start_time":body.start_time,"minutes":body.minutes_per_session,"completed":False,"completed_at":None})
        if len(task_docs)>=120: break
    dids=list({x.get("discipline_id") for x in task_docs if x.get("discipline_id")}); discs={d["id"]:d for d in await db.disciplines.find({"id":{"$in":dids}},P).to_list(100)} if dids else {}
    for x in task_docs: x["discipline_name"]=discs.get(x.get("discipline_id"),{}).get("name","")
    data=body.model_dump(); data["days"]=days; data["topic_ids"]=list({t["id"] for t in topics}); data["course_id"]=topics[0].get("course_id"); data["period_id"]=topics[0].get("period_id"); data["task_docs"]=task_docs; data["updated_at"]=now
    await db.study_plans.update_one({"id":plan_id,"user_id":user["id"]},{"$set":data})
    fresh={**existing,**data}
    plan=PersonalStudyPlan(id=plan_id,title=fresh["title"],days=days,start_time=fresh["start_time"],minutes_per_session=fresh["minutes_per_session"],discipline_ids=fresh["discipline_ids"],topic_ids=fresh["topic_ids"],course_id=fresh.get("course_id"),period_id=fresh.get("period_id"),created_at=fresh["created_at"],updated_at=now)
    return PersonalStudyPlanOut(plan=plan,tasks=[PersonalStudyPlanTask(plan_id=plan_id,**x) for x in task_docs])


@router.get("/personal-study-plans", response_model=list[PersonalStudyPlanOut])
async def list_personal_study_plans(user: dict = Depends(current_user)):
    docs=await db.study_plans.find({"user_id":user["id"]},P).sort("updated_at",-1).limit(50).to_list(50)
    out=[]
    for d in docs:
        plan=PersonalStudyPlan(id=d["id"],title=d["title"],days=d["days"],start_time=d["start_time"],minutes_per_session=d["minutes_per_session"],discipline_ids=d.get("discipline_ids",[]),topic_ids=d.get("topic_ids",[]),course_id=d.get("course_id"),period_id=d.get("period_id"),created_at=d["created_at"],updated_at=d["updated_at"])
        out.append(PersonalStudyPlanOut(plan=plan,tasks=[PersonalStudyPlanTask(plan_id=d["id"],**x) for x in d.get("task_docs",[])[:200]]))
    return out


@router.delete("/personal-study-plans/{plan_id}", response_model=Message)
async def delete_personal_study_plan(plan_id: str, user: dict = Depends(current_user)):
    plan=await db.study_plans.find_one({"id":plan_id,"user_id":user["id"]}, P)
    if not plan:
        raise HTTPException(404,"Plano de estudos não encontrado.")
    task_ids=[t.get("id") for t in plan.get("task_docs",[]) if t.get("id")]
    await db.study_plans.delete_one({"id":plan_id,"user_id":user["id"]})
    if task_ids:
        await db.history.delete_many({"user_id":user["id"],"personal_task_id":{"$in":task_ids}})
    return Message(message="Plano de estudos excluído.")


@router.post("/personal-study-plans/{plan_id}/tasks/{task_id}/complete", response_model=Message)
async def complete_personal_task(plan_id:str, task_id:str, user:dict=Depends(current_user)):
    plan=await db.study_plans.find_one({"id":plan_id,"user_id":user["id"]},P)
    if not plan: raise HTTPException(404,"Plano de estudos não encontrado.")
    found=False
    tasks=plan.get("task_docs",[])
    for task in tasks:
        if task.get("id")==task_id:
            task["completed"]=not bool(task.get("completed")); task["completed_at"]=now_utc() if task["completed"] else None; found=True; break
    if not found: raise HTTPException(404,"Tarefa não encontrada.")
    completed_task=next(x for x in tasks if x.get("id")==task_id)
    await db.study_plans.update_one({"id":plan_id,"user_id":user["id"]},{"$set":{"task_docs":tasks,"updated_at":now_utc()}})
    if completed_task.get("completed"):
        now=now_utc()
        topic_id=completed_task.get("topic_id")
        if topic_id:
            try:
                ctx=await topic_context(topic_id)
                existing_progress=await db.progress.find_one({"user_id":user["id"],"topic_id":topic_id})
                if not existing_progress:
                    await db.progress.insert_one({"user_id":user["id"],"topic_id":topic_id,"discipline_id":ctx["discipline"]["id"],"course_id":ctx["course"]["id"],"at":now})
                pending_reviews=await db.study_reviews.find({"user_id":user["id"],"topic_id":topic_id,"completed":False},P).to_list(20)
                existing_keys={(r.get("due_date"),int(r.get("interval_days",0) or 0)) for r in pending_reviews}
                for days in (1,3,7):
                    due=(now.date()+timedelta(days=days)).isoformat()
                    if (due,days) in existing_keys:
                        continue
                    await db.study_reviews.insert_one({"id":str(uuid.uuid4()),"user_id":user["id"],"topic_id":topic_id,"topic_name":ctx["topic"]["name"],"discipline_name":ctx["discipline"]["name"],"course_name":ctx["course"]["name"],"due_date":due,"interval_days":days,"completed":False,"completed_at":None,"created_at":now})
                course_name=ctx["course"]["name"]
            except HTTPException:
                course_name=""
        else:
            course_name=""
        await db.history.update_one(
            {"user_id":user["id"],"personal_task_id":task_id},
            {"$set":{"user_id":user["id"],"personal_task_id":task_id,"event_kind":"plano","topic_id":completed_task.get("topic_id", ""),
                      "topic_name":completed_task.get("topic_name", "Estudo pessoal"),"discipline_name":completed_task.get("discipline_name", ""),
                      "course_name":course_name,"path":"/meu-plano","task_title":completed_task.get("title","Tarefa de estudo"),"at":now}}, upsert=True
        )
    else:
        await db.history.delete_one({"user_id":user["id"],"personal_task_id":task_id})
    return Message(message="Tarefa atualizada.")


@router.get("/calendar", response_model=CalendarOut)
async def study_calendar(start: str = "", end: str = "", user: dict = Depends(current_user)):
    today=date.fromisoformat(today_iso("America/Sao_Paulo"))
    from_date=date.fromisoformat(start) if start else today - timedelta(days=7)
    to_date=date.fromisoformat(end) if end else today + timedelta(days=35)
    if to_date < from_date: raise HTTPException(400,"Período de calendário inválido.")
    if (to_date-from_date).days>93: raise HTTPException(400,"O período máximo do calendário é de 94 dias.")
    events=[]
    exams=await db.exam_plans.find({"user_id":user["id"],"exam_date":{"$gte":from_date.isoformat(),"$lte":to_date.isoformat()}},P).to_list(50)
    for e in exams: events.append(CalendarEvent(id=e["id"],date=e["exam_date"],title=f"Prova: {e['title']}",kind="prova",minutes=0,completed=False,path="/meu-plano"))
    plan_docs=await db.study_plans.find({"user_id":user["id"]},P).to_list(50)
    for pdoc in plan_docs:
        for t in pdoc.get("task_docs",[]):
            if from_date.isoformat()<=t.get("date","")<=to_date.isoformat(): events.append(CalendarEvent(id=t["id"],date=t["date"],title=t["title"],kind="estudo",minutes=int(t.get("minutes",0)),completed=bool(t.get("completed")),path="/meu-plano"))
    exam_ids={e["id"] for e in exams}
    task_docs=await db.exam_tasks.find({"user_id":user["id"],"task_date":{"$gte":from_date.isoformat(),"$lte":to_date.isoformat()}},P).limit(500).to_list(500)
    for t in task_docs:
        if t.get("exam_plan_id") in exam_ids: events.append(CalendarEvent(id=t["id"],date=t["task_date"],title=t["title"],kind=t.get("kind","tarefa"),minutes=int(t.get("minutes",0)),completed=bool(t.get("completed")),path="/meu-plano"))
    return CalendarOut(start=from_date.isoformat(),end=to_date.isoformat(),events=events)


@router.get("/reviews", response_model=list[ReviewItem])
async def list_reviews(user:dict=Depends(current_user), due_only: bool=False):
    q={"user_id":user["id"]}
    if due_only: q.update({"completed":False,"due_date":{"$lte":now_utc().date().isoformat()}})
    docs=await db.study_reviews.find(q,P).sort([("completed",1),("due_date",1)]).limit(300).to_list(300)
    return [ReviewItem(**{k:d.get(k) for k in ("id","topic_id","topic_name","discipline_name","course_name","due_date","interval_days","completed","completed_at")}) for d in docs]


@router.post("/reviews/{review_id}/complete", response_model=Message)
async def complete_review(review_id:str,user:dict=Depends(current_user)):
    r=await db.study_reviews.update_one({"id":review_id,"user_id":user["id"],"completed":False},{"$set":{"completed":True,"completed_at":now_utc()}})
    if not r.modified_count: raise HTTPException(404,"Revisão não encontrada ou já concluída.")
    return Message(message="Revisão concluída.")


@router.get("/weekly-goal", response_model=WeeklyGoal)
async def get_weekly_goal(user:dict=Depends(current_user)):
    today=date.fromisoformat(today_iso("America/Sao_Paulo")); week_start=today-timedelta(days=today.weekday()); ws=week_start.isoformat()
    doc=await db.weekly_goals.find_one({"user_id":user["id"],"week_start":ws},P)
    if not doc:
        now=now_utc(); doc={"id":str(uuid.uuid4()),"user_id":user["id"],"week_start":ws,"minutes":300,"topics":3,"questions":30,"tasks":5,"created_at":now,"updated_at":now}
        await db.weekly_goals.insert_one(doc)
    return await _weekly_goal_out(doc,user)


async def _weekly_goal_out(doc:dict,user:dict)->WeeklyGoal:
    start=date.fromisoformat(doc["week_start"]); end=start+timedelta(days=6); prefix_dates={ (start+timedelta(days=i)).isoformat() for i in range(7) }
    stats=await db.daily_stats.find({"user_id":user["id"],"date":{"$in":list(prefix_dates)}},P).to_list(20)
    week_progress=await db.progress.find({"user_id":user["id"]},P).sort("at",-1).limit(5000).to_list(5000)
    progress_docs=[x for x in week_progress if x.get("at") and start <= x["at"].astimezone().date() <= end]
    week_exams=await db.exams.find({"user_id":user["id"],"status":"finalizado"},P).sort("finished_at",-1).limit(500).to_list(500)
    exams=[x for x in week_exams if x.get("finished_at") and start <= x["finished_at"].astimezone().date() <= end]
    questions=sum(int(e.get("total",0)) for e in exams)
    plans=await db.study_plans.find({"user_id":user["id"]},P).to_list(50); task_count=0
    for pl in plans:
        task_count += sum(1 for t in pl.get("task_docs",[]) if t.get("date") in prefix_dates and t.get("completed"))
    exam_task_docs=await db.exam_tasks.find({"user_id":user["id"],"completed":True,"task_date":{"$in":list(prefix_dates)}},P).to_list(1000)
    task_count += len(exam_task_docs)
    return WeeklyGoal(id=doc["id"],week_start=doc["week_start"],minutes=int(doc.get("minutes",0)),topics=int(doc.get("topics",0)),questions=int(doc.get("questions",0)),tasks=int(doc.get("tasks",0)),progress_minutes=sum(int(x.get("minutes",0)) for x in stats),progress_topics=len(progress_docs),progress_questions=questions,progress_tasks=task_count,created_at=doc["created_at"],updated_at=doc["updated_at"])


@router.put("/weekly-goal", response_model=WeeklyGoal)
async def set_weekly_goal(body:WeeklyGoalIn,user:dict=Depends(current_user)):
    try: start=date.fromisoformat(body.week_start)
    except ValueError: raise HTTPException(400,"Semana inválida.")
    today=date.fromisoformat(today_iso("America/Sao_Paulo")); current=today-timedelta(days=today.weekday())
    if start != current: raise HTTPException(400,"A meta deve pertencer à semana atual.")
    now=now_utc(); data=body.model_dump()
    await db.weekly_goals.update_one(
        {"user_id":user["id"],"week_start":body.week_start},
        {"$set":{"minutes":data["minutes"],"topics":data["topics"],"questions":data["questions"],"tasks":data["tasks"],"updated_at":now},
         "$setOnInsert":{"id":str(uuid.uuid4()),"user_id":user["id"],"created_at":now}},
        upsert=True,
    )
    doc=await db.weekly_goals.find_one({"user_id":user["id"],"week_start":body.week_start},P)
    return await _weekly_goal_out(doc,user)


@router.get("/study-history", response_model=list[StudyHistoryEvent])
async def study_history(user: dict = Depends(current_user)):
    events: list[StudyHistoryEvent] = []
    history_docs = await db.history.find({"user_id": user["id"]}, P).sort("at", -1).limit(400).to_list(400)
    for x in history_docs:
        at = x.get("at")
        if not at or x.get("exam_id"):
            continue
        event_kind = x.get("event_kind")
        if event_kind == "tarefa":
            title = x.get("task_title") or x.get("topic_name") or "Tarefa de estudo"
            subtitle = f"{x.get('discipline_name','')} · {x.get('course_name','')}".strip(" ·")
            events.append(StudyHistoryEvent(id=f"exam-task:{x.get('exam_task_id', x.get('id',''))}", kind="tarefa", title=title, subtitle=subtitle, date=at, path=x.get("path", "/meu-plano")))
        elif event_kind == "plano":
            events.append(StudyHistoryEvent(id=f"personal:{x.get('personal_task_id', x.get('id',''))}", kind="plano",
                                             title=x.get("task_title") or x.get("topic_name") or "Tarefa de estudo",
                                             subtitle=x.get("discipline_name", ""), date=at, path=x.get("path", "/meu-plano")))
        else:
            subtitle = f"{x.get('discipline_name','')} · {x.get('course_name','')}".strip(" ·")
            events.append(StudyHistoryEvent(id=f"visit:{x.get('topic_id','')}", kind="conteúdo",
                                             title=x.get("topic_name", "Assunto"), subtitle=subtitle, date=at, path=x.get("path", "")))
    finished_exams = await db.exams.find({"user_id": user["id"], "status": "finalizado"}, P).sort("finished_at", -1).limit(100).to_list(100)
    for x in finished_exams:
        at = x.get("finished_at") or x.get("created_at")
        if at:
            events.append(StudyHistoryEvent(id=f"exam:{x['id']}", kind="questões", title=x.get("title", "Simulado"),
                                             subtitle=f"{int(x.get('correct',0))}/{int(x.get('total',0))} acertos", date=at, path=f"/simulados?exame={x['id']}"))
    sessions = await db.study_sessions.find({"user_id": user["id"], "status": "finalizado"}, P).sort("started_at", -1).limit(100).to_list(100)
    for x in sessions:
        at = x.get("ended_at") or x.get("started_at")
        if at and int(x.get("seconds", 0)) > 0:
            events.append(StudyHistoryEvent(id=f"session:{x['id']}", kind="estudo", title="Sessão de estudo",
                                             subtitle=f"{int(x.get('seconds',0))//60} min", date=at, path="/progresso"))
    events.sort(key=lambda e: e.date, reverse=True)
    return events[:300]


@router.get("/notifications", response_model=list[Notification])
async def notifications(user:dict=Depends(current_user)):
    docs=await db.notifications.find({"user_id":user["id"]},P).sort("created_at",-1).limit(100).to_list(100)
    return [Notification(**d) for d in docs]

@router.post("/notifications/{nid}/read", response_model=Message)
async def notification_read(nid:str,user:dict=Depends(current_user)):
    await db.notifications.update_one({"id":nid,"user_id":user["id"]},{"$set":{"read":True}}); return Message(message="Notificação lida.")

@router.post("/ranking-opt-in", response_model=Message)
async def ranking_opt_in(enabled:bool=True,user:dict=Depends(current_user)):
    await db.users.update_one({"id":user["id"]},{"$set":{"ranking_opt_in":enabled}})
    return Message(message="Participação no ranking atualizada.")

@router.get("/ranking", response_model=list[RankingEntry])
async def ranking(user:dict=Depends(current_user)):
    require_feature_access(user, "ranking")
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    zone = ZoneInfo("America/Sao_Paulo")
    now_local = datetime.now(timezone.utc).astimezone(zone)
    month_prefix = now_local.strftime("%Y-%m")
    users = await db.users.find({"role":"student","status":"ativo","ranking_opt_in":True},P).limit(5000).to_list(5000)
    course_ids = {u.get("course_id") for u in users if u.get("course_id")}
    courses = {c["id"]: c for c in await db.courses.find({"id":{"$in":[x for x in course_ids if x]}} ,P).to_list(5000)} if course_ids else {}
    minutes_by_user = {}
    if users:
        ids = [u["id"] for u in users]
        async for row in db.daily_stats.aggregate([
            {"$match": {"user_id": {"$in": ids}, "date": {"$regex": f"^{month_prefix}"}}},
            {"$group": {"_id": "$user_id", "minutes": {"$sum": {"$ifNull": ["$minutes", 0]}}}},
        ]):
            minutes_by_user[row["_id"]] = int(row.get("minutes", 0))
    rows=[]
    for u in users:
        month_minutes = minutes_by_user.get(u["id"], 0)
        rows.append({
            "points": month_minutes, "minutes": month_minutes, "name": u.get("name", "Estudante"),
            "id": u["id"], "course_name": courses.get(u.get("course_id"),{}).get("name", ""),
            "faculty": u.get("faculty", ""), "avatar_url": u.get("avatar_url", ""),
        })
    rows.sort(key=lambda x: (-x["points"], x["name"].lower()))
    ranked = []
    for i, r in enumerate(rows, start=1):
        ranked.append(RankingEntry(
            position=i, name=r["name"], points=r["points"], minutes=r["minutes"],
            course_name=r["course_name"], faculty=r["faculty"], avatar_url=r["avatar_url"],
            is_me=(r["id"] == user["id"]),
        ))
    # Return the top 100 plus the current user even when they are outside the top 100.
    top = ranked[:100]
    me = next((entry for entry in ranked if entry.is_me), None)
    if me and not any(entry.is_me for entry in top):
        top.append(me)
    return top

@router.post("/notifications/generate", response_model=Message)
async def generate_notifications(user:dict=Depends(current_user)):
    """Generate idempotent, data-driven reminders for exams, tasks, reviews, goals and study activity."""
    from datetime import timezone
    from zoneinfo import ZoneInfo
    zone=ZoneInfo("America/Sao_Paulo")
    now=now_utc()
    local_today=now.astimezone(zone).date()
    today=local_today.isoformat()
    local_midnight=datetime.combine(local_today, datetime.min.time(), tzinfo=zone)
    day_start_utc=local_midnight.astimezone(timezone.utc)
    created=[]

    async def add(kind,title,body):
        if await db.notifications.find_one({"user_id":user["id"],"kind":kind,"created_at":{"$gte":day_start_utc}}):
            return
        d={"id":str(uuid.uuid4()),"user_id":user["id"],"title":title,"body":body,"kind":kind,"read":False,"created_at":now_utc()}
        await db.notifications.insert_one(d)
        created.append(d)

    # Study time today / inactivity.
    stats=await db.daily_stats.find_one({"user_id":user["id"],"date":today},P) or {}
    minutes_today=int(stats.get("minutes",0) or 0)
    daily_goal=int(user.get("daily_goal_minutes",60) or 0)
    if daily_goal > 0 and minutes_today >= daily_goal:
        await add("meta_atingida", "Parabéns! Você atingiu sua meta de estudos.", f"Você estudou {minutes_today} minutos hoje. Continue assim!")
    elif minutes_today == 0:
        await add("meta", "Você ainda não estudou hoje.", "Que tal separar alguns minutos para estudar e manter seu ritmo?")
    elif daily_goal > minutes_today:
        remaining=daily_goal-minutes_today
        await add("meta_progresso", "Sua meta de hoje ainda não foi concluída.", f"Você já estudou {minutes_today} minutos. Faltam {remaining} minutos para sua meta diária.")

    # Detect 3+ consecutive days without recorded study.
    recent_dates={(r.get("date"), int(r.get("minutes",0) or 0)) async for r in db.daily_stats.find({"user_id":user["id"]}, {"date":1,"minutes":1}).sort("date",-1).limit(10)}
    recent_map={d:m for d,m in recent_dates if d}
    inactive_days=0
    for i in range(1,8):
        d=(local_today-timedelta(days=i)).isoformat()
        if recent_map.get(d,0) > 0:
            break
        inactive_days += 1
    if inactive_days >= 3:
        await add("inatividade", "Você está há 3 dias sem estudar.", "Retome aos poucos: uma tarefa ou alguns minutos hoje já ajudam a voltar ao ritmo.")

    # Upcoming exam and pending exam tasks.
    plans=await db.exam_plans.find({"user_id":user["id"],"exam_date":{"$gte":today}},P).sort("exam_date",1).limit(3).to_list(3)
    if plans:
        plan=plans[0]
        days=(date.fromisoformat(plan["exam_date"])-local_today).days
        pending=await db.exam_tasks.count_documents({"user_id":user["id"],"exam_plan_id":plan["id"],"completed":False})
        if days == 0:
            await add("prova_hoje", "Sua prova é hoje.", f"A prova de {plan['title']} é hoje. {pending} tarefa(s) ainda estão pendentes.")
        elif days == 1:
            if pending:
                await add("prova_amanha_pendente", "Sua prova é amanhã.", f"A prova de {plan['title']} é amanhã e você ainda tem {pending} tarefa(s) pendente(s). Que tal revisar hoje?")
            else:
                await add("prova_amanha", "Sua prova é amanhã.", f"A prova de {plan['title']} é amanhã. Que tal fazer uma revisão final?")
        elif days <= 7:
            await add("prova", f"Faltam {days} dias para sua prova.", f"Sua prova de {plan['title']} está chegando. Você ainda tem {pending} tarefa(s) pendente(s).")

    # Today's tasks from exam plans.
    today_tasks=await db.exam_tasks.count_documents({"user_id":user["id"],"task_date":today,"completed":False})
    if today_tasks:
        await add("tarefas_hoje", "Você tem tarefas de estudo hoje.", f"Hoje você tem {today_tasks} tarefa(s) do seu plano de estudos.")

    # Spaced reviews due today/overdue.
    due_reviews=await db.study_reviews.count_documents({"user_id":user["id"],"completed":False,"due_date":{"$lte":today}})
    if due_reviews:
        await add("revisao", "Você tem uma revisão programada.", f"Há {due_reviews} revisão(ões) para hoje ou pendentes. Aproveite para revisar os assuntos.")

    # Weekly goal progress.
    week_start=local_today-timedelta(days=local_today.weekday())
    weekly=await db.weekly_goals.find_one({"user_id":user["id"],"week_start":week_start.isoformat()},P)
    if weekly:
        week_dates={(week_start+timedelta(days=i)).isoformat() for i in range(7)}
        week_stats=await db.daily_stats.find({"user_id":user["id"],"date":{"$in":list(week_dates)}},P).to_list(20)
        week_minutes=sum(int(x.get("minutes",0) or 0) for x in week_stats)
        target_minutes=int(weekly.get("minutes",0) or 0)
        if target_minutes > 0:
            pct_value=min(100,round(week_minutes/target_minutes*100))
            if pct_value >= 100:
                await add("meta_semanal_atingida", "Parabéns! Você atingiu sua meta semanal.", f"Sua meta semanal de {target_minutes} minutos foi concluída.")
            elif pct_value >= 70:
                remaining=max(0,target_minutes-week_minutes)
                await add("meta_semanal_progresso", f"Sua meta semanal está em {pct_value}%.", f"Faltam {remaining} minutos para concluir sua meta semanal.")

    return Message(message=f"{len(created)} notificação(ões) gerada(s).")
