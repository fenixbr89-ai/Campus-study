"""Student area: home, progress/gamification, favorites, library items, exams, submissions."""

import random
import uuid
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pymongo import ReturnDocument

from fastapi import APIRouter, Depends, HTTPException

from lib.auth import current_user, require_feature_access
from lib.content import present_content, topic_context
from lib.dates import today_iso
from lib.db import db
from lib.security import now_utc
from models.schemas import (
    Achievement, Content, Course, DayStat, Exam, ExamStartIn, ExamSubmitIn, FavoriteIn, HistoryItem, HomeOut,
    Message, ProgressOut, Submission, SubmissionIn, UserItem, UserItemIn, ExamPlan, ExamPlanIn, ExamPlanUpdateIn, ExamTask,
    StudySession, StudySessionStartIn, StudyPlanOut, StudyPlanTask,
)

router = APIRouter(tags=["study"])
P = {"_id": 0}
TZ = "America/Sao_Paulo"


async def build_exam_plan(doc: dict, user: dict) -> ExamPlan:
    exam_date = date.fromisoformat(doc["exam_date"])
    today = date.fromisoformat(today_iso(TZ))
    days_left = max(0, (exam_date - today).days)
    discipline = await db.disciplines.find_one({"id": doc["discipline_id"]}, P)
    if not discipline:
        raise HTTPException(404, "Disciplina da prova não encontrada.")
    topics = await db.topics.find({"discipline_id": discipline["id"], "status": "publicado"}, P).sort("name", 1).to_list(1000)
    topic_ids = [t["id"] for t in topics]
    completed_docs = await db.progress.find({"user_id": user["id"], "topic_id": {"$in": topic_ids}}, P).to_list(1000) if topic_ids else []
    completed_ids = {p["topic_id"] for p in completed_docs}
    pending = [t for t in topics if t["id"] not in completed_ids]
    # “Em andamento” usa o histórico recente para não considerar todo assunto visitado como concluído.
    history = await db.history.find({"user_id": user["id"], "topic_id": {"$in": topic_ids}}, P).sort("at", -1).to_list(1000) if topic_ids else []
    in_progress_ids = {h["topic_id"] for h in history if h["topic_id"] not in completed_ids}
    topics_in_progress = len(in_progress_ids)
    topics_pending = max(0, len(topics) - len(completed_ids) - topics_in_progress)
    question_count = await db.contents.count_documents({"topic_id": {"$in": topic_ids}, "type": "questao", "status": "publicado"}) if topic_ids else 0
    remaining_work = max(1, len(topics) - len(completed_ids))
    daily_minutes = max(20, min(180, (remaining_work * 30 + max(days_left, 1) - 1) // max(days_left, 1)))
    revisions = max(1, (remaining_work + 2) // 3) if remaining_work else 0
    mock_exams = max(1, (remaining_work + 4) // 5) if remaining_work else 0
    progress_pct = round(len(completed_ids) / len(topics) * 100) if topics else 0
    today_topic = pending[0]["name"] if pending else (topics[0]["name"] if topics else "Revisão geral")
    return ExamPlan(
        id=doc["id"], title=doc["title"], exam_date=doc["exam_date"], discipline_id=discipline["id"],
        discipline_name=discipline["name"], days_left=days_left, progress_pct=progress_pct, topics_total=len(topics),
        topics_completed=len(completed_ids), topics_in_progress=topics_in_progress, topics_pending=topics_pending,
        questions_to_practice=question_count, revisions=revisions, mock_exams=mock_exams, daily_minutes=daily_minutes,
        today_topic=today_topic, today_discipline=discipline["name"], created_at=doc["created_at"],
    )


async def _upsert_exam_task(doc: dict) -> None:
    key = {"user_id": doc["user_id"], "exam_plan_id": doc["exam_plan_id"], "task_date": doc["task_date"], "kind": doc["kind"]}
    await db.exam_tasks.update_one(key, {"$setOnInsert": doc}, upsert=True)


async def ensure_exam_tasks(plan: dict, user: dict) -> None:
    """Persist a practical daily queue and rebuild only unfinished future work after progress changes."""
    today = date.fromisoformat(today_iso(TZ))
    exam_date = date.fromisoformat(plan["exam_date"])
    topics = await db.topics.find({"discipline_id": plan["discipline_id"], "status": "publicado"}, P).sort("name", 1).to_list(1000)
    topic_ids = [t["id"] for t in topics]
    completed = await db.progress.find({"user_id": user["id"], "topic_id": {"$in": topic_ids}}, P).to_list(1000) if topic_ids else []
    completed_ids = {p["topic_id"] for p in completed}
    pending = [t for t in topics if t["id"] not in completed_ids]

    # Keep completed history, but recalculate all unfinished future tasks from today's reality.
    await db.exam_tasks.delete_many({"user_id": user["id"], "exam_plan_id": plan["id"], "completed": False, "task_date": {"$gte": today.isoformat()}})
    existing_completed = await db.exam_tasks.count_documents({"user_id": user["id"], "exam_plan_id": plan["id"], "completed": True})
    del existing_completed

    days = max(1, (exam_date - today).days + 1)
    days = min(days, 90)
    minutes = await build_exam_plan(plan, user)
    topic_index = 0
    for offset in range(days):
        day = today + timedelta(days=offset)
        if topic_index < len(pending):
            topic = pending[topic_index]
            topic_index += 1
            topic_minutes = max(15, min(60, minutes.daily_minutes))
            await _upsert_exam_task({
                "id": str(uuid.uuid4()), "user_id": user["id"], "exam_plan_id": plan["id"],
                "task_date": day.isoformat(), "kind": "topic", "title": f"Estudar — {topic['name']}",
                "topic_id": topic["id"], "topic_name": topic["name"], "discipline_name": minutes.discipline_name,
                "minutes": topic_minutes, "completed": False, "completed_at": None,
            })
            if minutes.daily_minutes > topic_minutes:
                await _upsert_exam_task({
                    "id": str(uuid.uuid4()), "user_id": user["id"], "exam_plan_id": plan["id"],
                    "task_date": day.isoformat(), "kind": "questions",
                    "title": "Resolver questões de fixação", "topic_id": topic["id"],
                    "topic_name": topic["name"], "discipline_name": minutes.discipline_name,
                    "minutes": minutes.daily_minutes - topic_minutes, "completed": False, "completed_at": None,
                })
        else:
            await _upsert_exam_task({
                "id": str(uuid.uuid4()), "user_id": user["id"], "exam_plan_id": plan["id"],
                "task_date": day.isoformat(), "kind": "review", "title": "Revisão e questões",
                "topic_id": None, "topic_name": None, "discipline_name": minutes.discipline_name,
                "minutes": minutes.daily_minutes, "completed": False, "completed_at": None,
            })


async def get_upcoming_exam(user: dict) -> ExamPlan | None:
    today = today_iso(TZ)
    docs = await db.exam_plans.find({"user_id": user["id"], "exam_date": {"$gte": today}}, P).sort("exam_date", 1).limit(1).to_list(1)
    return await build_exam_plan(docs[0], user) if docs else None


async def compute_progress(user: dict) -> ProgressOut:
    uid = user["id"]
    days = await db.daily_stats.find({"user_id": uid}, P).to_list(5000)
    by_date = {d["date"]: int(d.get("minutes", 0)) for d in days}
    today = today_iso(TZ)
    t = date.fromisoformat(today)
    streak = 0
    cursor = t if by_date.get(today) else t - timedelta(days=1)
    while by_date.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    week = [DayStat(date=(t - timedelta(days=i)).isoformat(), minutes=by_date.get((t - timedelta(days=i)).isoformat(), 0))
            for i in range(6, -1, -1)]
    month = [DayStat(date=(t - timedelta(days=i)).isoformat(), minutes=by_date.get((t - timedelta(days=i)).isoformat(), 0))
             for i in range(29, -1, -1)]
    sessions = await db.study_sessions.find({"user_id": uid}, P).to_list(20000)
    seconds_total = sum(int(x.get("seconds", 0)) for x in sessions)
    minutes_total = seconds_total // 60
    month_prefix = today[:7]
    month_seconds = 0
    month_days = set()
    for x in sessions:
        started = x.get("started_at")
        if started and started.astimezone(ZoneInfo(TZ)).strftime("%Y-%m") == month_prefix:
            month_seconds += int(x.get("seconds", 0))
            month_days.add(started.astimezone(ZoneInfo(TZ)).date().isoformat())
    # Daily stats remain the source for day-level goals/streaks and are updated from real sessions.
    completed = await db.progress.find({"user_id": uid}, P).to_list(10000)
    exams = await db.exams.find({"user_id": uid, "status": "finalizado"}, {"_id": 0, "correct": 1, "total": 1}).to_list(10000)
    answered = sum(e.get("total", 0) for e in exams)
    correct = sum(e.get("correct", 0) for e in exams)
    topics_done = len(completed)
    discs = len({c.get("discipline_id") for c in completed if c.get("discipline_id")})
    meta_days = sum(1 for d in days if d.get("minutes", 0) >= user.get("daily_goal_minutes", 60)) if user.get("daily_goal_minutes", 60) > 0 else sum(1 for d in days if d.get("minutes", 0) > 0)
    # Points are now tied to verified study time: one point per full minute studied.
    points = minutes_total
    rate = round(correct / answered * 100, 1) if answered else 0.0
    ach = [
        ("primeira-hora", "Primeira hora", "Acumule 60 minutos de estudo real.", minutes_total >= 60),
        ("dez-horas", "10 horas de foco", "Acumule 10 horas de estudo.", minutes_total >= 600),
        ("cinquenta-horas", "50 horas de foco", "Acumule 50 horas de estudo.", minutes_total >= 3000),
        ("trinta-dias", "30 dias estudando", "Estude em 30 dias diferentes.", len([d for d in days if d.get("minutes",0)>0]) >= 30),
        ("sequencia-3", "Constância", "Estude 3 dias seguidos.", streak >= 3),
        ("sequencia-7", "Semana perfeita", "Estude 7 dias seguidos.", streak >= 7),
        ("primeiro-simulado", "Estreia nos simulados", "Finalize seu primeiro simulado.", len(exams) >= 1),
        ("cem-questoes", "500 questões", "Responda 500 questões.", answered >= 500),
        ("meta-diaria", "Meta batida", "Atinja sua meta diária de estudo.", (user.get("daily_goal_minutes", 60) == 0 and by_date.get(today, 0) > 0) or by_date.get(today, 0) >= user.get("daily_goal_minutes", 60)),
        ("dez-assuntos", "Explorador do saber", "Conclua 10 assuntos.", topics_done >= 10),
        ("noventa-aproveitamento", "90% de aproveitamento", "Alcance 90% de acertos.", rate >= 90),
    ]
    return ProgressOut(points=points, streak_days=streak, minutes_total=minutes_total, month_minutes=month_seconds // 60, month_study_days=len(month_days),
                       minutes_today=by_date.get(today, 0), daily_goal_minutes=user.get("daily_goal_minutes", 60), topics_completed=topics_done,
                       disciplines_studied=discs, questions_answered=answered, correct_rate=rate, exams_taken=len(exams),
                       achievements=[Achievement(id=a, title=b, description=c, unlocked=d) for a, b, c, d in ach], week=week, month=month)


@router.get("/home", response_model=HomeOut)
async def home(user: dict = Depends(current_user)):
    hist = await db.history.find({"user_id": user["id"]}, P).sort("at", -1).limit(8).to_list(8)
    courses = await db.courses.find({"status": "publicado"}, P).sort("name", 1).to_list(500)
    if user.get("course_id"):
        courses.sort(key=lambda c: c["id"] != user["course_id"])
    q = {"status": "publicado"}
    videos = await db.contents.find({**q, "type": "video"}, P).sort("created_at", -1).limit(10).to_list(10)
    articles = await db.contents.find({**q, "type": "artigo"}, P).sort("created_at", -1).limit(10).to_list(10)
    rq = {**q, "course_id": user["course_id"]} if user.get("course_id") else q
    rec = await db.contents.find(rq, P).sort("views", -1).limit(10).to_list(10)
    return HomeOut(
        continue_studying=[HistoryItem(**h) for h in hist], courses=[Course(**c) for c in courses],
        videos=[Content(**present_content(v, user)) for v in videos],
        articles=[Content(**present_content(a, user)) for a in articles],
        recommended=[Content(**present_content(r, user)) for r in rec], progress=await compute_progress(user), upcoming_exam=await get_upcoming_exam(user))


@router.post("/study-plan/redistribute", response_model=StudyPlanOut)
async def redistribute_study_plan(user: dict = Depends(current_user)):
    plans = await db.exam_plans.find({"user_id": user["id"], "exam_date": {"$gte": today_iso(TZ)}}, P).sort("exam_date", 1).limit(3).to_list(3)
    for plan in plans:
        await ensure_exam_tasks(plan, user)
    # Reuse the existing study-plan presentation so redistribution never creates
    # a second planning data model or diverges from the UI's source of truth.
    today = today_iso(TZ)
    tasks: list[StudyPlanTask] = []
    for plan in plans:
        docs = await db.exam_tasks.find({"user_id": user["id"], "exam_plan_id": plan["id"], "task_date": {"$gte": today}}, P).sort([("task_date", 1), ("completed", 1)]).limit(500).to_list(500)
        tasks.extend(StudyPlanTask(id=d["id"], date=d["task_date"], title=d["title"], discipline_name=d["discipline_name"], topic_name=d.get("topic_name"), minutes=int(d["minutes"]), completed=bool(d["completed"]), kind=d["kind"]) for d in docs)
    personal = await db.study_plans.find({"user_id": user["id"]}, P).sort("updated_at", -1).limit(10).to_list(10)
    for plan in personal:
        for d in plan.get("task_docs", [])[:300]:
            tasks.append(StudyPlanTask(id=d["id"], date=d["date"], title=d["title"], discipline_name=d.get("discipline_name", ""), topic_name=d.get("topic_name") or None, minutes=int(d.get("minutes", plan.get("minutes_per_session", 60))), completed=bool(d.get("completed", False)), kind="personal"))
    tasks.sort(key=lambda x: (x.date, x.completed, x.title.lower()))
    pending = sum(t.minutes for t in tasks if not t.completed)
    return StudyPlanOut(tasks=tasks, pending_minutes=pending, message=(f"Você tem {pending} minutos pendentes." if pending else "Plano em dia!"))


@router.get("/exam-plans", response_model=list[ExamPlan])
async def list_exam_plans(user: dict = Depends(current_user)):
    docs = await db.exam_plans.find({"user_id": user["id"]}, P).sort("exam_date", 1).to_list(100)
    return [await build_exam_plan(d, user) for d in docs]


@router.post("/exam-plans", response_model=ExamPlan)
async def create_exam_plan(body: ExamPlanIn, user: dict = Depends(current_user)):
    exam_date = date.fromisoformat(body.exam_date)
    if exam_date < date.fromisoformat(today_iso(TZ)):
        raise HTTPException(400, "A data da prova precisa ser hoje ou uma data futura.")
    if not await db.disciplines.find_one({"id": body.discipline_id, "status": "publicado"}, P):
        raise HTTPException(404, "Disciplina não encontrada.")
    doc = {**body.model_dump(), "id": str(uuid.uuid4()), "user_id": user["id"], "created_at": now_utc()}
    await db.exam_plans.insert_one(doc)
    await ensure_exam_tasks(doc, user)
    return await build_exam_plan(doc, user)


@router.put("/exam-plans/{plan_id}", response_model=ExamPlan)
async def update_exam_plan(plan_id: str, body: ExamPlanUpdateIn, user: dict = Depends(current_user)):
    exam_date = date.fromisoformat(body.exam_date)
    if exam_date < date.fromisoformat(today_iso(TZ)):
        raise HTTPException(400, "A data da prova precisa ser hoje ou uma data futura.")
    discipline = await db.disciplines.find_one({"id": body.discipline_id, "status": "publicado"}, P)
    if not discipline:
        raise HTTPException(404, "Disciplina não encontrada.")
    plan = await db.exam_plans.find_one({"id": plan_id, "user_id": user["id"]}, P)
    if not plan:
        raise HTTPException(404, "Plano de prova não encontrado.")
    updated = {**body.model_dump(), "updated_at": now_utc()}
    old_task_ids = [x["id"] for x in await db.exam_tasks.find({"exam_plan_id": plan_id, "user_id": user["id"]}, {"_id": 0, "id": 1}).to_list(1000)]
    if old_task_ids:
        await db.history.delete_many({"user_id": user["id"], "exam_task_id": {"$in": old_task_ids}})
    # Exam tasks are derived data. Rebuild the schedule after an edit so a changed
    # discipline/date can never leave tasks from the previous proof behind.
    await db.exam_tasks.delete_many({"exam_plan_id": plan_id, "user_id": user["id"]})
    await db.exam_plans.update_one({"id": plan_id, "user_id": user["id"]}, {"$set": updated})
    fresh = {**plan, **updated}
    await ensure_exam_tasks(fresh, user)
    return await build_exam_plan(fresh, user)


@router.delete("/exam-plans/{plan_id}", response_model=Message)
async def delete_exam_plan(plan_id: str, user: dict = Depends(current_user)):
    # Capture dependent task IDs BEFORE deleting the tasks. The previous order
    # deleted exam_tasks first and therefore could never clean related history.
    plan_filter = {"id": plan_id, "user_id": user["id"]}
    plan = await db.exam_plans.find_one(plan_filter, {"_id": 0, "id": 1})
    if not plan:
        raise HTTPException(404, "Plano de prova não encontrado.")

    task_ids = [
        x["id"]
        for x in await db.exam_tasks.find(
            {"exam_plan_id": plan_id, "user_id": user["id"]},
            {"_id": 0, "id": 1},
        ).to_list(1000)
    ]

    await db.exam_plans.delete_one(plan_filter)
    await db.exam_tasks.delete_many({"exam_plan_id": plan_id, "user_id": user["id"]})
    if task_ids:
        await db.history.delete_many({"user_id": user["id"], "exam_task_id": {"$in": task_ids}})

    return Message(message="Plano da prova excluído.")


@router.get("/exam-plans/{plan_id}/tasks", response_model=list[ExamTask])
async def list_exam_tasks(plan_id: str, user: dict = Depends(current_user)):
    plan = await db.exam_plans.find_one({"id": plan_id, "user_id": user["id"]}, P)
    if not plan:
        raise HTTPException(404, "Plano de prova não encontrado.")
    count = await db.exam_tasks.count_documents({"exam_plan_id": plan_id, "user_id": user["id"]})
    if count == 0:
        await ensure_exam_tasks(plan, user)
    docs = await db.exam_tasks.find({"exam_plan_id": plan_id, "user_id": user["id"]}, P).sort([ ("task_date", 1), ("completed", 1) ]).to_list(500)
    return [ExamTask(**d) for d in docs]


@router.post("/exam-tasks/{task_id}/complete", response_model=Message)
async def complete_exam_task(task_id: str, user: dict = Depends(current_user)):
    task = await db.exam_tasks.find_one({"id": task_id, "user_id": user["id"]}, P)
    if not task:
        raise HTTPException(404, "Tarefa não encontrada.")
    if task.get("completed"):
        return Message(message="Tarefa já concluída.")
    if task.get("topic_id") and task.get("kind") == "topic":
        ctx = await topic_context(task["topic_id"])
        existing = await db.progress.find_one({"user_id": user["id"], "topic_id": task["topic_id"]})
        now = now_utc()
        if not existing:
            await db.progress.insert_one({"user_id": user["id"], "topic_id": task["topic_id"],
                                          "discipline_id": ctx["discipline"]["id"], "course_id": ctx["course"]["id"], "at": now})
        await db.history.update_one(
            {"user_id": user["id"], "exam_task_id": task_id},
            {"$set": {"user_id": user["id"], "exam_task_id": task_id, "event_kind": "tarefa", "topic_id": task["topic_id"],
                      "topic_name": ctx["topic"]["name"], "discipline_name": ctx["discipline"]["name"],
                      "course_name": ctx["course"]["name"],
                      "path": f"/cursos/{ctx['course']['slug']}/{ctx['period']['slug']}/{ctx['discipline']['slug']}/{ctx['topic']['slug']}",
                      "at": now}}, upsert=True)
    elif task.get("kind") in {"questions", "review"}:
        await db.history.update_one(
            {"user_id": user["id"], "exam_task_id": task_id},
            {"$set": {"user_id": user["id"], "exam_task_id": task_id, "event_kind": "tarefa",
                      "topic_id": task.get("topic_id", ""), "topic_name": task.get("topic_name", ""),
                      "discipline_name": task.get("discipline_name", ""), "course_name": "",
                      "path": "/meu-plano", "task_title": task.get("title", "Tarefa de estudo"), "at": now_utc()}},
            upsert=True,
        )
    await db.exam_tasks.update_one({"id": task_id, "user_id": user["id"]}, {"$set": {"completed": True, "completed_at": now_utc()}})
    plan = await db.exam_plans.find_one({"id": task["exam_plan_id"], "user_id": user["id"]}, P)
    if plan:
        await ensure_exam_tasks(plan, user)
    return Message(message="Tarefa concluída. Plano recalculado.")


async def _record_interval(user_id: str, started_at: datetime, ended_at: datetime) -> int:
    """Persist exact seconds into daily_stats, splitting intervals across local calendar days."""
    if ended_at <= started_at:
        return 0
    zone = ZoneInfo(TZ)
    total = 0
    cursor = started_at
    while cursor < ended_at:
        local = cursor.astimezone(zone)
        next_day = (local.date() + timedelta(days=1))
        boundary_local = datetime.combine(next_day, datetime.min.time(), tzinfo=zone)
        boundary_utc = boundary_local.astimezone(started_at.tzinfo)
        segment_end = min(ended_at, boundary_utc)
        seconds = max(0, int((segment_end - cursor).total_seconds()))
        if seconds:
            date_key = local.date().isoformat()
            new_seconds = await db.daily_stats.find_one_and_update(
                {"user_id": user_id, "date": date_key},
                {"$inc": {"seconds": seconds}, "$set": {"last_beat": ended_at}},
                upsert=True, projection=P, return_document=ReturnDocument.AFTER,
            )
            # Compatibility with older documents that only had minutes.
            current = int((new_seconds or {}).get("seconds", seconds))
            await db.daily_stats.update_one({"user_id": user_id, "date": date_key}, {"$set": {"minutes": current // 60}})
            total += seconds
        cursor = segment_end
    return total


async def _flush_session(session: dict, *, now: datetime) -> int:
    last = session.get("last_heartbeat_at") or session.get("started_at")
    last = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
    # No heartbeat means there is no evidence that the user was actively studying.
    delta = max(0, int((now - last).total_seconds()))
    if delta:
        await _record_interval(session["user_id"], last, now)
        await db.study_sessions.update_one({"id": session["id"]}, {"$inc": {"seconds": delta}, "$set": {"last_heartbeat_at": now}})
    return delta


@router.get("/study-sessions/active", response_model=StudySession | None)
async def active_study_session(user: dict = Depends(current_user)):
    doc = await db.study_sessions.find_one({"user_id": user["id"], "status": "em_andamento"}, P)
    return StudySession(**doc) if doc else None


@router.post("/study-sessions", response_model=StudySession)
async def start_study_session(body: StudySessionStartIn, user: dict = Depends(current_user)):
    if body.task_id:
        task = await db.exam_tasks.find_one({"id": body.task_id, "user_id": user["id"], "completed": False}, P)
        if not task:
            raise HTTPException(404, "Tarefa de estudo não encontrada ou já concluída.")
        topic_id = body.topic_id or task.get("topic_id")
    else:
        task = None
        topic_id = body.topic_id
        if body.content_id:
            content = await db.contents.find_one({"id": body.content_id, "status": "publicado"}, P)
            if not content:
                raise HTTPException(404, "Conteúdo de estudo não encontrado.")
            topic_id = topic_id or content.get("topic_id")
    if not topic_id and not body.content_id:
        raise HTTPException(400, "Inicie o estudo a partir de uma matéria ou conteúdo.")
    active = await db.study_sessions.find_one({"user_id": user["id"], "status": "em_andamento"}, P)
    if active:
        return StudySession(**active)
    now = now_utc()
    doc = {"id": str(uuid.uuid4()), "user_id": user["id"], "task_id": task["id"] if task else None,
           "topic_id": topic_id, "content_id": body.content_id, "started_at": now, "ended_at": None,
           "last_heartbeat_at": now, "seconds": 0, "status": "em_andamento"}
    await db.study_sessions.insert_one(doc)
    return StudySession(**doc)


@router.post("/study-sessions/{session_id}/heartbeat", response_model=StudySession)
async def study_session_heartbeat(session_id: str, user: dict = Depends(current_user)):
    session = await db.study_sessions.find_one({"id": session_id, "user_id": user["id"], "status": "em_andamento"}, P)
    if not session:
        raise HTTPException(404, "Sessão de estudo não encontrada.")
    now = now_utc()
    await _flush_session(session, now=now)
    latest = await db.study_sessions.find_one({"id": session_id}, P)
    return StudySession(**latest)


@router.post("/study-sessions/{session_id}/stop", response_model=StudySession)
async def stop_study_session(session_id: str, user: dict = Depends(current_user)):
    session = await db.study_sessions.find_one({"id": session_id, "user_id": user["id"], "status": "em_andamento"}, P)
    if not session:
        raise HTTPException(404, "Sessão de estudo não encontrada.")
    now = now_utc()
    await _flush_session(session, now=now)
    latest = await db.study_sessions.find_one({"id": session_id}, P)
    update = {"ended_at": now, "status": "finalizado"}
    await db.study_sessions.update_one({"id": session_id}, {"$set": update})
    final = {**latest, **update}
    return StudySession(**final)


@router.post("/progress/heartbeat", response_model=Message)
async def heartbeat(user: dict = Depends(current_user)):
    # Legacy endpoint kept for compatibility. It no longer credits passive time.
    return Message(message="tempo-passivo-desativado")


@router.post("/progress/topics/{topic_id}", response_model=Message)
async def toggle_topic(topic_id: str, user: dict = Depends(current_user)):
    ctx = await topic_context(topic_id)
    existing = await db.progress.find_one({"user_id": user["id"], "topic_id": topic_id})
    if existing:
        await db.progress.delete_one({"user_id": user["id"], "topic_id": topic_id})
        return Message(message="Assunto desmarcado.")
    now = now_utc()
    await db.progress.insert_one({"user_id": user["id"], "topic_id": topic_id, "discipline_id": ctx["discipline"]["id"],
                                  "course_id": ctx["course"]["id"], "at": now})
    await db.history.update_one(
        {"user_id": user["id"], "topic_id": topic_id},
        {"$set": {"at": now, "topic_name": ctx["topic"]["name"], "discipline_name": ctx["discipline"]["name"],
                  "course_name": ctx["course"]["name"],
                  "path": f"/cursos/{ctx['course']['slug']}/{ctx['period']['slug']}/{ctx['discipline']['slug']}/{ctx['topic']['slug']}"}},
        upsert=True,
    )
    return Message(message="Assunto concluído.")


# ---------- favorites ----------
@router.get("/favorites", response_model=list[Content])
async def list_favorites(user: dict = Depends(current_user)):
    favs = await db.favorites.find({"user_id": user["id"]}, P).sort("at", -1).to_list(2000)
    ids = [f["content_id"] for f in favs]
    docs = {d["id"]: d for d in await db.contents.find({"id": {"$in": ids}, "type": {"$ne": "flashcard"}, **PUB}, P).to_list(2000)}
    return [Content(**present_content(docs[i], user)) for i in ids if i in docs]


@router.post("/favorites", response_model=Message)
async def toggle_favorite(body: FavoriteIn, user: dict = Depends(current_user)):
    if not await db.contents.find_one({"id": body.content_id}):
        raise HTTPException(404, "Conteúdo não encontrado.")
    q = {"user_id": user["id"], "content_id": body.content_id}
    if await db.favorites.find_one(q):
        await db.favorites.delete_one(q)
        return Message(message="Removido dos salvos.")
    await db.favorites.insert_one({**q, "at": now_utc()})
    return Message(message="Salvo na sua biblioteca.")


# ---------- personal library items  ----------
def _item_out(doc: dict, full: bool = True) -> UserItem:
    d = {k: v for k, v in doc.items() if k not in ("_id", "user_id")}
    if not full and d["kind"] == "pdf":
        d["data"] = {k: v for k, v in d["data"].items() if k != "text"}
    return UserItem(**d)


async def save_item(user: dict, body: UserItemIn) -> UserItem:
    topic_name = ""
    if body.topic_id:
        topic_name = (await topic_context(body.topic_id))["topic"]["name"]
    now = now_utc()
    doc = {**body.model_dump(), "id": str(uuid.uuid4()), "user_id": user["id"], "topic_name": topic_name,
           "created_at": now, "updated_at": now}
    await db.user_items.insert_one(doc)
    return _item_out(doc)


@router.get("/items", response_model=list[UserItem])
async def list_items(kind: str = "", user: dict = Depends(current_user)):
    q = {"user_id": user["id"]}
    if kind:
        q["kind"] = kind
    docs = await db.user_items.find(q, P).sort("updated_at", -1).to_list(1000)
    return [_item_out(d, full=False) for d in docs]


@router.get("/items/{iid}", response_model=UserItem)
async def get_item(iid: str, user: dict = Depends(current_user)):
    doc = await db.user_items.find_one({"id": iid, "user_id": user["id"]}, P)
    if not doc:
        raise HTTPException(404, "Item não encontrado.")
    return _item_out(doc, full=False)


@router.post("/items", response_model=UserItem)
async def create_item(body: UserItemIn, user: dict = Depends(current_user)):
    if body.kind == "pdf":
        raise HTTPException(400, "O envio de PDF não está disponível nesta versão.")
    return await save_item(user, body)


@router.put("/items/{iid}", response_model=UserItem)
async def update_item(iid: str, body: UserItemIn, user: dict = Depends(current_user)):
    doc = await db.user_items.find_one({"id": iid, "user_id": user["id"]}, P)
    if not doc:
        raise HTTPException(404, "Item não encontrado.")
    data = body.data
    if doc["kind"] == "pdf":
        data = {**doc["data"]}
    await db.user_items.update_one({"id": iid}, {"$set": upd})
    return _item_out({**doc, **upd}, full=False)


@router.delete("/items/{iid}", response_model=Message)
async def delete_item(iid: str, user: dict = Depends(current_user)):
    res = await db.user_items.delete_one({"id": iid, "user_id": user["id"]})
    if not res.deleted_count:
        raise HTTPException(404, "Item não encontrado.")
    return Message(message="Item excluído.")


# ---------- exams (simulados) ----------
def _exam_out(doc: dict) -> Exam:
    done = doc["status"] == "finalizado"
    # O modo de estudo mostra a alternativa correta durante a resolução para permitir
    # feedback imediato. O resultado final continua registrando a escolha do aluno.
    qs = [{"statement": q["statement"], "options": q["options"], "difficulty": q.get("difficulty", ""),
           "correct_index": q["correct_index"], "explanation": q.get("explanation", ""),
           "chosen": q.get("chosen") if done else None} for q in doc["questions"]]
    return Exam(**{**{k: v for k, v in doc.items() if k not in ("_id", "user_id", "questions")}, "questions": qs})


@router.post("/exams", response_model=Exam)
async def start_exam(body: ExamStartIn, user: dict = Depends(current_user)):
    require_feature_access(user, "simulados")
    questions = []
    title = "Simulado"
    if body.source == "item" and body.item_id:
        item = await db.user_items.find_one({"id": body.item_id, "user_id": user["id"]}, P)
        if not item or item.get("kind") != "questoes": raise HTTPException(404, "Banco de questões não encontrado.")
        questions = item["data"].get("questions", [])[: body.count]
        title = item.get("title", "Simulado")
    else:
        from routers.ai import generate_topic_pack
        q = {"type":"questao","status":"publicado"}
        topic_ids: list[str] = []
        if body.topic_id:
            topic_ids = [body.topic_id]
            title = "Simulado de " + (await db.topics.find_one({"id": body.topic_id}, {"name": 1}) or {}).get("name", "assunto")
        elif body.discipline_id:
            topics = await db.topics.find({"discipline_id":body.discipline_id,"status":"publicado"}, {"id":1,"name":1}).sort("name",1).to_list(1000)
            topic_ids = [t["id"] for t in topics]
            discipline = await db.disciplines.find_one({"id": body.discipline_id}, {"name":1})
            title = "Simulado geral de " + (discipline or {}).get("name", "disciplina")
        elif body.course_id:
            topics = await db.topics.find({"course_id":body.course_id,"status":"publicado"}, {"id":1}).sort("name",1).to_list(3000)
            topic_ids = [t["id"] for t in topics]
            course = await db.courses.find_one({"id": body.course_id}, {"name":1})
            title = "Simulado geral de " + (course or {}).get("name", "curso")
        if topic_ids:
            q["topic_id"] = {"$in": topic_ids}
        if body.difficulty: q["difficulty"] = body.difficulty
        docs = await db.contents.find(q, P).to_list(5000)
        if len(docs) < body.count:
            raise HTTPException(400, f"Este assunto possui apenas {len(docs)} questões publicadas; são necessárias 20 para o simulado.")
        if body.shuffle_questions: random.shuffle(docs)
        docs = docs[:body.count]
        questions = [{"statement":c["data"].get("statement") or c["title"],"options":list(c["data"].get("options",[])),"correct_index":int(c["data"].get("correct_index",0)),"explanation":c["data"].get("explanation",""),"difficulty":c.get("difficulty","")} for c in docs]
        if not title:
            title = "Simulado de " + (body.difficulty if body.difficulty else "questões")
    if body.shuffle_questions: random.shuffle(questions)
    if body.shuffle_options:
        for qn in questions:
            correct_text = qn["options"][qn.get("correct_index",0)] if qn.get("options") and qn.get("correct_index",0) < len(qn["options"]) else None
            random.shuffle(qn["options"])
            if correct_text is not None: qn["correct_index"] = qn["options"].index(correct_text)
    if not questions: raise HTTPException(400,"Não há questões disponíveis para os filtros escolhidos.")
    now=now_utc(); doc={"id":str(uuid.uuid4()),"user_id":user["id"],"title":title,"status":"em_andamento","questions":questions,"correct":0,"total":len(questions),"score":None,"mode":body.mode,"duration_seconds":0,"created_at":now,"finished_at":None}
    await db.exams.insert_one(doc); return _exam_out(doc)

@router.get("/exams", response_model=list[Exam])
async def list_exams(user: dict = Depends(current_user)):
    require_feature_access(user, "simulados")
    docs = await db.exams.find({"user_id": user["id"]}, P).sort("created_at", -1).to_list(200)
    return [_exam_out(d) for d in docs]


@router.get("/exams/{eid}", response_model=Exam)
async def get_exam(eid: str, user: dict = Depends(current_user)):
    require_feature_access(user, "simulados")
    doc = await db.exams.find_one({"id": eid, "user_id": user["id"]}, P)
    if not doc:
        raise HTTPException(404, "Simulado não encontrado.")
    return _exam_out(doc)


@router.post("/exams/{eid}/submit", response_model=Exam)
async def submit_exam(eid: str, body: ExamSubmitIn, user: dict = Depends(current_user)):
    require_feature_access(user, "simulados")
    doc = await db.exams.find_one({"id": eid, "user_id": user["id"]}, P)
    if not doc: raise HTTPException(404, "Simulado não encontrado.")
    if doc["status"] == "finalizado": raise HTTPException(409, "Este simulado já foi finalizado.")
    correct=0
    for i,q in enumerate(doc["questions"]):
        q["chosen"] = body.answers[i] if i < len(body.answers) else -1
        correct += int(q["chosen"] == q.get("correct_index"))
    duration=int(body.duration_seconds or 0) if hasattr(body,"duration_seconds") else 0
    upd={"questions":doc["questions"],"correct":correct,"status":"finalizado","score":round(correct/doc["total"]*10,1),"finished_at":now_utc(),"duration_seconds":duration}
    await db.exams.update_one({"id":eid},{"$set":upd})
    await db.history.update_one(
        {"user_id": user["id"], "exam_id": eid},
        {"$set": {"user_id": user["id"], "exam_id": eid, "event_kind": "questões", "at": upd["finished_at"],
                  "topic_id": "", "topic_name": doc.get("title", "Simulado"),
                  "discipline_name": "Simulado", "course_name": "", "path": f"/simulados/{eid}"}},
        upsert=True,
    )
    return _exam_out({**doc,**upd})

@router.post("/exams/{eid}/retry-wrong", response_model=Exam)
async def retry_wrong(eid:str,user:dict=Depends(current_user)):
    require_feature_access(user, "simulados")
    doc=await db.exams.find_one({"id":eid,"user_id":user["id"],"status":"finalizado"},P)
    if not doc: raise HTTPException(404,"Simulado finalizado não encontrado.")
    wrong=[q for q in doc["questions"] if q.get("chosen")!=q.get("correct_index")]
    if not wrong: raise HTTPException(400,"Você não errou nenhuma questão neste simulado.")
    now=now_utc(); new={"id":str(uuid.uuid4()),"user_id":user["id"],"title":"Refazer questões erradas — "+doc["title"],"status":"em_andamento","questions":[{**q,"chosen":None} for q in wrong],"correct":0,"total":len(wrong),"score":None,"mode":"prova","duration_seconds":0,"created_at":now,"finished_at":None}
    await db.exams.insert_one(new); return _exam_out(new)

# ---------- student submissions ----------
@router.post("/submissions", response_model=Submission)
async def create_submission(body: SubmissionIn, user: dict = Depends(current_user)):
    ctx = await topic_context(body.topic_id)
    doc = {**body.model_dump(), "id": str(uuid.uuid4()), "user_id": user["id"], "user_name": user["name"],
           "topic_name": ctx["topic"]["name"], "status": "pendente", "reviewer_note": "", "created_at": now_utc()}
    await db.submissions.insert_one(doc)
    return Submission(**doc)


@router.get("/submissions/mine", response_model=list[Submission])
async def my_submissions(user: dict = Depends(current_user)):
    return await db.submissions.find({"user_id": user["id"]}, P).sort("created_at", -1).to_list(200)
