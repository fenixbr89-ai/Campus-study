"""Student area: home, progress/gamification, favorites, library items, exams, submissions."""

import random
import uuid
import hashlib
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pymongo import ReturnDocument

from fastapi import APIRouter, Depends, HTTPException

from lib.auth import current_user, require_feature_access
from lib.content import present_content, topic_context, visible_content_query
from lib.dates import today_iso
from lib.db import db
from lib.security import now_utc
from models.schemas import (
    Achievement, Content, Course, DayStat, Exam, ExamStartIn, ExamSubmitIn, FavoriteIn, HistoryItem, HomeOut,
    Message, ProgressOut, Submission, SubmissionIn, UserItem, UserItemIn, ExamPlan, ExamPlanIn, ExamPlanUpdateIn, ExamTask,
    StudySession, StudySessionStartIn, StudyPlanOut, StudyPlanTask,
    AcademicDashboardOut, AcademicRecommendation, StudyHistoryEvent, QuestionReview, QuestionReviewIn, TopicFavoriteOut,
    AcademicPerformanceOut, AcademicPerformanceBucket, AcademicTopicPerformance, AcademicDailyAccuracy,
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


async def _verified_study_seconds_by_date(user_id: str) -> dict[str, int]:
    """Return only time from completed, explicitly started study sessions.

    Legacy daily_stats can contain values created by older passive-timer logic.
    Progress must be based on actual study sessions instead of those legacy totals.
    """
    docs = await db.study_sessions.find(
        {"user_id": user_id, "status": "finalizado", "seconds": {"$gt": 0}}, P
    ).to_list(20000)
    zone = ZoneInfo(TZ)
    by_date: dict[str, int] = {}
    for session in docs:
        started = session.get("started_at")
        ended = session.get("ended_at")
        recorded = max(0, int(session.get("seconds", 0) or 0))
        if not started or not ended or recorded <= 0:
            continue
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        if ended.tzinfo is None:
            ended = ended.replace(tzinfo=timezone.utc)
        elapsed = max(0, int((ended - started).total_seconds()))
        remaining = min(recorded, elapsed) if elapsed else recorded
        cursor = started
        while remaining > 0:
            local = cursor.astimezone(zone)
            next_day_local = datetime.combine(local.date() + timedelta(days=1), datetime.min.time(), tzinfo=zone)
            boundary = next_day_local.astimezone(timezone.utc)
            segment = min(remaining, max(0, int((boundary - cursor).total_seconds())))
            if segment <= 0:
                segment = remaining
            key = local.date().isoformat()
            by_date[key] = by_date.get(key, 0) + segment
            remaining -= segment
            cursor = min(ended, cursor + timedelta(seconds=segment))
    return by_date


async def compute_progress(user: dict) -> ProgressOut:
    uid = user["id"]
    by_seconds = await _verified_study_seconds_by_date(uid)
    by_date = {day: seconds // 60 for day, seconds in by_seconds.items()}
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
    seconds_total = sum(by_seconds.values())
    minutes_total = seconds_total // 60
    month_prefix = today[:7]
    month_seconds = sum(seconds for day, seconds in by_seconds.items() if str(day).startswith(month_prefix))
    month_days = {day for day, seconds in by_seconds.items() if str(day).startswith(month_prefix) and seconds > 0}
    # Daily stats remain the source for day-level goals/streaks and are updated from real sessions.
    completed = await db.progress.find({"user_id": uid}, P).to_list(10000)
    exams = await db.exams.find({"user_id": uid, "status": "finalizado"}, {"_id": 0, "correct": 1, "total": 1}).to_list(10000)
    answered = sum(sum(1 for q in e.get("questions", []) if int(q.get("chosen", -1)) >= 0) for e in exams)
    correct = sum(e.get("correct", 0) for e in exams)
    topics_done = len(completed)
    discs = len({c.get("discipline_id") for c in completed if c.get("discipline_id")})
    meta_days = sum(1 for minutes in by_date.values() if minutes >= user.get("daily_goal_minutes", 60)) if user.get("daily_goal_minutes", 60) > 0 else sum(1 for minutes in by_date.values() if minutes > 0)
    # Points are now tied to verified study time: one point per full minute studied.
    points = minutes_total
    rate = round(correct / answered * 100, 1) if answered else 0.0
    ach = [
        ("primeira-hora", "Primeira hora", "Acumule 60 minutos de estudo real.", minutes_total >= 60),
        ("dez-horas", "10 horas de foco", "Acumule 10 horas de estudo.", minutes_total >= 600),
        ("cinquenta-horas", "50 horas de foco", "Acumule 50 horas de estudo.", minutes_total >= 3000),
        ("trinta-dias", "30 dias estudando", "Estude em 30 dias diferentes.", len([seconds for seconds in by_seconds.values() if seconds > 0]) >= 30),
        ("sequencia-3", "Constância", "Estude 3 dias seguidos.", streak >= 3),
        ("sequencia-7", "Semana perfeita", "Estude 7 dias seguidos.", streak >= 7),
        ("primeiro-simulado", "Estreia nos simulados", "Finalize seu primeiro simulado.", len(exams) >= 1),
        ("cem-questoes", "500 questões", "Responda 500 questões.", answered >= 500),
        ("meta-diaria", "Meta batida", "Atinja sua meta diária de estudo.", (user.get("daily_goal_minutes", 60) == 0 and by_date.get(today, 0) > 0) or by_date.get(today, 0) >= user.get("daily_goal_minutes", 60)),
        ("dez-assuntos", "Explorador do saber", "Conclua 10 assuntos.", topics_done >= 10),
        ("noventa-aproveitamento", "90% de aproveitamento", "Alcance 90% de acertos.", rate >= 90),
    ]
    unlocked_at = now_utc()
    for achievement_id, title, description, unlocked in ach:
        if unlocked:
            await db.user_achievements.update_one(
                {"user_id": uid, "achievement_id": achievement_id},
                {"$setOnInsert": {"id": str(uuid.uuid4()), "user_id": uid, "achievement_id": achievement_id,
                                   "title": title, "description": description, "unlocked_at": unlocked_at}},
                upsert=True,
            )
    return ProgressOut(points=points, streak_days=streak, minutes_total=minutes_total, month_minutes=month_seconds // 60, month_study_days=len(month_days),
                       minutes_today=by_date.get(today, 0), daily_goal_minutes=user.get("daily_goal_minutes", 60), topics_completed=topics_done,
                       disciplines_studied=discs, questions_answered=answered, correct_rate=rate, exams_taken=len(exams),
                       achievements=[Achievement(id=a, title=b, description=c, unlocked=d) for a, b, c, d in ach], week=week, month=month)


@router.get("/home", response_model=HomeOut)
async def home(user: dict = Depends(current_user)):
    hist = await db.history.find({"user_id": user["id"], "event_kind": "estudo"}, P).sort("at", -1).limit(8).to_list(8)
    courses = await db.courses.find({"status": "publicado"}, P).sort("name", 1).to_list(500)
    if user.get("course_id"):
        courses.sort(key=lambda c: c["id"] != user["course_id"])
    q = {"status": "publicado", **visible_content_query(user)}
    videos = await db.contents.find({**q, "type": "video"}, P).sort("created_at", -1).limit(10).to_list(10)
    articles = await db.contents.find({**q, "type": "artigo"}, P).sort("created_at", -1).limit(10).to_list(10)
    rq = {**q, "course_id": user["course_id"]} if user.get("course_id") else q
    rec = await db.contents.find(rq, P).sort("views", -1).limit(10).to_list(10)
    return HomeOut(
        continue_studying=[HistoryItem(**h) for h in hist], courses=[Course(**c) for c in courses],
        videos=[Content(**present_content(v, user)) for v in videos],
        articles=[Content(**present_content(a, user)) for a in articles],
        recommended=[Content(**present_content(r, user)) for r in rec], progress=await compute_progress(user), upcoming_exam=await get_upcoming_exam(user))


@router.get("/academic-dashboard", response_model=AcademicDashboardOut)
async def academic_dashboard(user: dict = Depends(current_user)):
    """Real student-facing academic summary built only from persisted data."""
    uid = user["id"]
    course = await db.courses.find_one({"id": user.get("course_id"), "status": "publicado"}, P) if user.get("course_id") else None
    completed = await db.progress.find({"user_id": uid}, P).to_list(10000)
    completed_ids = {x.get("topic_id") for x in completed if x.get("topic_id")}
    topic_query = {"status": "publicado"}
    if user.get("course_id"):
        topic_query["course_id"] = user["course_id"]
    topics = await db.topics.find(topic_query, P).sort("name", 1).to_list(10000)
    total = len(topics)
    completed_count = len(completed_ids & {t["id"] for t in topics})
    period_name = ""
    if completed_ids:
        latest = await db.progress.find_one({"user_id": uid, "topic_id": {"$in": list(completed_ids)}}, P, sort=[("at", -1)])
        if latest:
            period = await db.periods.find_one({"id": (await db.topics.find_one({"id": latest.get("topic_id")}, P) or {}).get("period_id")}, P)
            period_name = (period or {}).get("name", "")
    exams = await db.exams.find({"user_id": uid, "status": "finalizado"}, P).sort("finished_at", -1).to_list(1000)
    answered = sum(sum(1 for q in e.get("questions", []) if int(q.get("chosen", -1)) >= 0) for e in exams)
    correct = sum(int(e.get("correct", 0)) for e in exams)
    rate = round(correct / answered * 100, 1) if answered else 0
    sessions = await db.study_sessions.find({"user_id": uid}, P).to_list(20000)
    minutes = sum(int(x.get("seconds", 0)) for x in sessions) // 60
    completed_content_ids = {x.get("content_id") for x in sessions if x.get("content_id") and int(x.get("seconds", 0)) > 0}
    progress = await compute_progress(user)
    recent = (await study_history(user))[:8]
    recommendations: list[AcademicRecommendation] = []
    due_reviews = await db.question_reviews.count_documents({"user_id": uid, "due_date": {"$lte": today_iso(TZ)}})
    if due_reviews:
        recommendations.append(AcademicRecommendation(id="revisao-do-dia", title="Questões para revisar", reason=f"Você tem {due_reviews} questão(ões) com revisão pendente hoje.", path="/revisao", kind="revisao"))
    pending = [t for t in topics if t["id"] not in completed_ids]
    for topic in pending[:5]:
        disc = await db.disciplines.find_one({"id": topic.get("discipline_id")}, P)
        period = await db.periods.find_one({"id": topic.get("period_id")}, P)
        course_doc = course or await db.courses.find_one({"id": topic.get("course_id")}, P)
        path = f"/cursos/{(course_doc or {}).get('slug','')}/{(period or {}).get('slug','')}/{(disc or {}).get('slug','')}/{topic.get('slug','')}"
        recommendations.append(AcademicRecommendation(id=topic["id"], title=topic["name"], reason="Você ainda não concluiu este assunto.", path=path))
    ranking_position = None
    if user.get("ranking_opt_in"):
        month_prefix = today_iso(TZ)[:7]
        scores = await db.daily_stats.aggregate([
            {"$match": {"date": {"$regex": f"^{month_prefix}"}}},
            {"$group": {"_id": "$user_id", "minutes": {"$sum": "$minutes"}}},
            {"$sort": {"minutes": -1, "_id": 1}},
        ]).to_list(5000)
        for i, row in enumerate(scores, 1):
            if row.get("_id") == uid:
                ranking_position = i
                break
    return AcademicDashboardOut(
        course_name=(course or {}).get("name", ""), period_name=period_name,
        progress_pct=round(completed_count/total*100,1) if total else 0,
        topics_total=total, topics_completed=completed_count, contents_completed=len(completed_content_ids),
        questions_answered=answered, correct_rate=rate, exams_taken=len(exams), minutes_total=minutes,
        streak_days=progress.streak_days, points=progress.points, ranking_position=ranking_position,
        recent=recent, recommendations=recommendations,
    )


@router.get("/academic-performance", response_model=AcademicPerformanceOut)
async def academic_performance(user: dict = Depends(current_user)):
    """Academic analytics from finalized answers and verified study sessions."""
    uid = user["id"]
    exams = await db.exams.find({"user_id": uid, "status": "finalizado"}, P).sort("finished_at", 1).to_list(5000)

    # Load all topics in the student's course once, so analytics do not issue N+1 lookups.
    topic_query = {"status": "publicado"}
    if user.get("course_id"):
        topic_query["course_id"] = user["course_id"]
    all_topics = await db.topics.find(topic_query, P).sort("name", 1).to_list(10000)
    topic_map = {t["id"]: t for t in all_topics}
    disc_ids = {t.get("discipline_id") for t in all_topics if t.get("discipline_id")}
    period_ids = {t.get("period_id") for t in all_topics if t.get("period_id")}
    discs = await db.disciplines.find({"id": {"$in": list(disc_ids)}}, P).to_list(5000) if disc_ids else []
    periods = await db.periods.find({"id": {"$in": list(period_ids)}}, P).to_list(5000) if period_ids else []
    disc_map = {d["id"]: d for d in discs}
    period_map = {p["id"]: p for p in periods}

    answered = correct = 0
    by_disc: dict[str, dict[str, int]] = {}
    by_diff: dict[str, dict[str, int]] = {}
    by_topic: dict[str, dict[str, int]] = {}
    by_day: dict[str, dict[str, int]] = {}
    for exam in exams:
        finished = exam.get("finished_at") or exam.get("created_at")
        for q in exam.get("questions", []):
            chosen = int(q.get("chosen", -1)) if q.get("chosen") is not None else -1
            if chosen < 0:
                continue
            answered += 1
            is_correct = int(chosen == int(q.get("correct_index", -999)))
            correct += is_correct
            topic = topic_map.get(q.get("topic_id"), {})
            disc = disc_map.get(topic.get("discipline_id"), {})
            disc_label = disc.get("name", "Sem disciplina")
            diff = str(q.get("difficulty") or "Sem dificuldade").strip() or "Sem dificuldade"
            b = by_disc.setdefault(disc_label, {"questions": 0, "correct": 0})
            b["questions"] += 1; b["correct"] += is_correct
            b = by_diff.setdefault(diff, {"questions": 0, "correct": 0})
            b["questions"] += 1; b["correct"] += is_correct
            topic_id = q.get("topic_id")
            if topic_id:
                b = by_topic.setdefault(topic_id, {"questions": 0, "correct": 0})
                b["questions"] += 1; b["correct"] += is_correct
            if finished:
                f = finished if finished.tzinfo else finished.replace(tzinfo=timezone.utc)
                local_date = f.astimezone(ZoneInfo(TZ)).date().isoformat()
                b = by_day.setdefault(local_date, {"questions": 0, "correct": 0})
                b["questions"] += 1; b["correct"] += is_correct

    sessions = await db.study_sessions.find({"user_id": uid, "seconds": {"$gt": 0}}, P).to_list(20000)
    study_seconds: dict[str, int] = {}
    for session in sessions:
        topic_id = session.get("topic_id")
        if topic_id:
            study_seconds[topic_id] = study_seconds.get(topic_id, 0) + int(session.get("seconds", 0))
    completed_ids = {x["topic_id"] for x in await db.progress.find({"user_id": uid}, P).to_list(10000) if x.get("topic_id")}

    topic_out: list[AcademicTopicPerformance] = []
    for topic in all_topics:
        b = by_topic.get(topic["id"], {"questions": 0, "correct": 0})
        qn, cr = b["questions"], b["correct"]
        disc = disc_map.get(topic.get("discipline_id"), {})
        period = period_map.get(topic.get("period_id"), {})
        topic_out.append(AcademicTopicPerformance(
            id=topic["id"], title=topic["name"], discipline_name=disc.get("name", ""), period_name=period.get("name", ""),
            completed=topic["id"] in completed_ids, questions_answered=qn, correct=cr,
            correct_rate=round(cr / qn * 100, 1) if qn else 0, study_minutes=study_seconds.get(topic["id"], 0) // 60,
        ))

    def to_buckets(source: dict[str, dict[str, int]]) -> list[AcademicPerformanceBucket]:
        return [AcademicPerformanceBucket(
            label=k, questions=v["questions"], correct=v["correct"],
            correct_rate=round(v["correct"] / v["questions"] * 100, 1) if v["questions"] else 0,
        ) for k, v in sorted(source.items(), key=lambda item: (-item[1]["questions"], item[0]))]

    observed = [x for x in topic_out if x.questions_answered >= 3]
    strengths = [x.title for x in sorted(observed, key=lambda x: x.correct_rate, reverse=True) if x.correct_rate >= 80][:3]
    low = [x.title for x in sorted(observed, key=lambda x: x.correct_rate) if x.correct_rate < 60][:3]
    due = await db.question_reviews.find({"user_id": uid, "due_date": {"$lte": today_iso(TZ)}}, {"_id": 0, "topic_name": 1}).limit(10).to_list(10)
    needs_review = list(dict.fromkeys(low + [x.get("topic_name", "") for x in due if x.get("topic_name")]))[:5]
    daily = [AcademicDailyAccuracy(
        date=k, questions=v["questions"], correct=v["correct"],
        correct_rate=round(v["correct"] / v["questions"] * 100, 1) if v["questions"] else 0,
    ) for k, v in sorted(by_day.items())[-30:]]

    return AcademicPerformanceOut(
        questions_answered=answered, correct=correct, incorrect=max(0, answered - correct),
        correct_rate=round(correct / answered * 100, 1) if answered else 0,
        exams_taken=len(exams), by_discipline=to_buckets(by_disc), by_difficulty=to_buckets(by_diff),
        by_topic=topic_out[:500], daily_accuracy=daily, strengths=strengths, needs_review=needs_review,
    )


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
    # Compare-and-set the heartbeat timestamp before recording time. This prevents
    # concurrent heartbeat requests from crediting the same interval twice.
    delta = max(0, int((now - last).total_seconds()))
    if not delta:
        return 0
    stored_last = session.get("last_heartbeat_at")
    cas_last = stored_last if stored_last is not None else None
    result = await db.study_sessions.find_one_and_update(
        {"id": session["id"], "status": "em_andamento", "last_heartbeat_at": cas_last},
        {"$inc": {"seconds": delta}, "$set": {"last_heartbeat_at": now}},
        projection=P, return_document=ReturnDocument.AFTER,
    )
    if result is None:
        return 0
    await _record_interval(session["user_id"], last, now)
    return delta


STALE_SESSION_SECONDS = 90


@router.get("/study-sessions/active", response_model=StudySession | None)
async def active_study_session(user: dict = Depends(current_user)):
    doc = await db.study_sessions.find_one({"user_id": user["id"], "status": "em_andamento"}, P)
    if not doc:
        return None
    now = now_utc()
    last = doc.get("last_heartbeat_at") or doc.get("started_at")
    if last:
        last = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
        if (now - last).total_seconds() > STALE_SESSION_SECONDS:
            # An abandoned/hidden tab must not turn idle time into study time.
            await db.study_sessions.update_one(
                {"id": doc["id"], "status": "em_andamento"},
                {"$set": {"ended_at": last, "status": "finalizado"}},
            )
            return None
    return StudySession(**doc)


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
            content = await db.contents.find_one({"id": body.content_id, "status": "publicado", **visible_content_query(user)}, P)
            if not content:
                raise HTTPException(404, "Conteúdo de estudo não encontrado.")
            topic_id = topic_id or content.get("topic_id")
    if not topic_id and not body.content_id:
        raise HTTPException(400, "Inicie o estudo a partir de uma matéria ou conteúdo.")
    study_context = await topic_context(topic_id) if topic_id else None
    if study_context and (study_context["topic"].get("status") != "publicado" or study_context["course"].get("status") != "publicado"):
        raise HTTPException(404, "Assunto de estudo não encontrado.")
    active = await db.study_sessions.find_one({"user_id": user["id"], "status": "em_andamento"}, P)
    if active:
        return StudySession(**active)
    now = now_utc()
    doc = {"id": str(uuid.uuid4()), "user_id": user["id"], "task_id": task["id"] if task else None,
           "topic_id": topic_id, "content_id": body.content_id, "started_at": now, "ended_at": None,
           "last_heartbeat_at": now, "seconds": 0, "status": "em_andamento"}
    await db.study_sessions.insert_one(doc)
    if study_context:
        ctx = study_context
        await db.history.update_one(
            {"user_id": user["id"], "topic_id": topic_id},
            {"$set": {"at": now, "event_kind": "estudo", "topic_name": ctx["topic"]["name"],
                      "discipline_name": ctx["discipline"]["name"], "course_name": ctx["course"]["name"],
                      "path": f"/cursos/{ctx['course']['slug']}/{ctx['period']['slug']}/{ctx['discipline']['slug']}/{ctx['topic']['slug']}"}},
            upsert=True,
        )
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


@router.get("/progress", response_model=ProgressOut)
async def progress(user: dict = Depends(current_user)):
    return await compute_progress(user)


@router.post("/progress/heartbeat", response_model=Message)
async def heartbeat(user: dict = Depends(current_user)):
    # Legacy endpoint kept for compatibility. It no longer credits passive time.
    return Message(message="tempo-passivo-desativado")


@router.post("/progress/topics/{topic_id}", response_model=Message)
async def toggle_topic(topic_id: str, user: dict = Depends(current_user)):
    ctx = await topic_context(topic_id)
    if ctx["topic"].get("status") != "publicado" or ctx["course"].get("status") != "publicado":
        raise HTTPException(404, "Assunto não encontrado.")
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
@router.get("/question-reviews", response_model=list[QuestionReview])
async def list_question_reviews(due_only: bool = False, user: dict = Depends(current_user)):
    q = {"user_id": user["id"]}
    if due_only:
        q["due_date"] = {"$lte": today_iso(TZ)}
    docs = await db.question_reviews.find(q, P).sort("due_date", 1).limit(200).to_list(200)
    return [QuestionReview(**d) for d in docs]


@router.post("/question-reviews", response_model=QuestionReview)
async def mark_question_for_review(body: QuestionReviewIn, user: dict = Depends(current_user)):
    exam = await db.exams.find_one({"id": body.exam_id, "user_id": user["id"]}, P)
    if not exam or body.question_index >= len(exam.get("questions", [])):
        raise HTTPException(404, "Questão não encontrada.")
    q = exam["questions"][body.question_index]
    statement = str(q.get("statement", "")).strip()
    fingerprint = hashlib.sha256((statement + "\n" + "\n".join(q.get("options", []))).encode("utf-8")).hexdigest()
    question_topic_id = q.get("topic_id")
    if body.topic_id and body.topic_id != question_topic_id:
        raise HTTPException(400, "O assunto informado não corresponde à questão do simulado.")
    topic_id = question_topic_id
    topic = await db.topics.find_one({"id": topic_id, "status": "publicado"}, P) if topic_id else None
    disc = await db.disciplines.find_one({"id": topic.get("discipline_id")}, P) if topic else None
    course = await db.courses.find_one({"id": topic.get("course_id")}, P) if topic else None
    now = now_utc()
    existing = await db.question_reviews.find_one({"user_id": user["id"], "fingerprint": fingerprint}, P)
    if existing:
        await db.question_reviews.update_one({"id": existing["id"], "user_id": user["id"]}, {"$set": {"review_reason": body.review_reason}})
        return QuestionReview(**{**existing, "review_reason": body.review_reason})
    doc = {"id": str(uuid.uuid4()), "user_id": user["id"], "fingerprint": fingerprint,
           "statement": statement, "options": q.get("options", []), "correct_index": int(q.get("correct_index", 0)),
           "chosen": q.get("chosen"), "explanation": q.get("explanation", ""), "difficulty": q.get("difficulty", ""),
           "topic_id": topic_id, "topic_name": (topic or {}).get("name", ""),
           "discipline_name": (disc or {}).get("name", ""), "course_name": (course or {}).get("name", ""),
           "due_date": today_iso(TZ), "interval_days": 1, "errors": int(q.get("chosen") != q.get("correct_index")),
           "successes": int(q.get("chosen") == q.get("correct_index")), "last_reviewed_at": now,
           "review_reason": body.review_reason}
    await db.question_reviews.insert_one(doc)
    return QuestionReview(**doc)


@router.delete("/question-reviews/{review_id}", response_model=Message)
async def remove_question_review(review_id: str, user: dict = Depends(current_user)):
    result = await db.question_reviews.delete_one({"id": review_id, "user_id": user["id"]})
    if not result.deleted_count:
        raise HTTPException(404, "Questão não encontrada na revisão.")
    return Message(message="Questão removida da revisão.")


@router.post("/question-reviews/{review_id}/complete", response_model=QuestionReview)
async def complete_question_review(review_id: str, correct: bool = True, user: dict = Depends(current_user)):
    doc = await db.question_reviews.find_one({"id": review_id, "user_id": user["id"]}, P)
    if not doc:
        raise HTTPException(404, "Revisão não encontrada.")
    interval = min(60, max(1, int(doc.get("interval_days", 1) * (2 if correct else 1))))
    due = date.fromisoformat(today_iso(TZ)) + timedelta(days=interval)
    upd = {"due_date": due.isoformat(), "interval_days": interval, "last_reviewed_at": now_utc(),
           "successes": int(doc.get("successes", 0)) + int(correct), "errors": int(doc.get("errors", 0)) + int(not correct)}
    await db.question_reviews.update_one({"id": review_id}, {"$set": upd})
    return QuestionReview(**{**doc, **upd})


@router.get("/topic-favorites", response_model=list[TopicFavoriteOut])
async def list_topic_favorites(user: dict = Depends(current_user)):
    docs = await db.topic_favorites.find({"user_id": user["id"]}, P).sort("at", -1).limit(500).to_list(500)
    out=[]
    for f in docs:
        t=await db.topics.find_one({"id":f["topic_id"],"status":"publicado"},P)
        if not t: continue
        d=await db.disciplines.find_one({"id":t.get("discipline_id")},P); c=await db.courses.find_one({"id":t.get("course_id"),"status":"publicado"},P); p=await db.periods.find_one({"id":t.get("period_id")},P)
        if c and p and d:
            out.append(TopicFavoriteOut(id=t["id"],name=t["name"],path=f"/cursos/{c['slug']}/{p['slug']}/{d['slug']}/{t['slug']}",discipline_name=d["name"],course_name=c["name"]))
    return out


@router.post("/topic-favorites/{topic_id}", response_model=Message)
async def toggle_topic_favorite(topic_id: str, user: dict = Depends(current_user)):
    topic=await db.topics.find_one({"id":topic_id,"status":"publicado"},P)
    if not topic: raise HTTPException(404,"Assunto não encontrado.")
    q={"user_id":user["id"],"topic_id":topic_id}
    if await db.topic_favorites.find_one(q):
        await db.topic_favorites.delete_one(q); return Message(message="Assunto removido dos favoritos.")
    await db.topic_favorites.insert_one({**q,"at":now_utc()})
    return Message(message="Assunto salvo nos favoritos.")


@router.get("/favorites", response_model=list[Content])
async def list_favorites(user: dict = Depends(current_user)):
    favs = await db.favorites.find({"user_id": user["id"]}, P).sort("at", -1).to_list(2000)
    ids = [f["content_id"] for f in favs]
    docs = {d["id"]: d for d in await db.contents.find({"id": {"$in": ids}, "type": {"$ne": "flashcard"}, **PUB}, P).to_list(2000)}
    return [Content(**present_content(docs[i], user)) for i in ids if i in docs]


@router.post("/favorites", response_model=Message)
async def toggle_favorite(body: FavoriteIn, user: dict = Depends(current_user)):
    if not await db.contents.find_one({"id": body.content_id, **visible_content_query(user)}):
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
    reveal_answers = done or doc.get("mode") == "estudo"
    qs = [{"statement": q["statement"], "options": q["options"], "difficulty": q.get("difficulty", ""),
           "correct_index": q["correct_index"] if reveal_answers else None, "explanation": q.get("explanation", "") if reveal_answers else None,
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
        raw_questions = item["data"].get("questions", [])
        questions = []
        fingerprints = set()
        for q in raw_questions:
            if not isinstance(q, dict) or not str(q.get("statement", "")).strip() or len(q.get("options", [])) != 5 or not isinstance(q.get("correct_index"), int) or not 0 <= q.get("correct_index", -1) < 5:
                continue
            fingerprint = hashlib.sha256((str(q.get("statement", "")).strip() + "\n" + "\n".join(map(str, q.get("options", [])))).encode("utf-8")).hexdigest()
            if fingerprint in fingerprints:
                continue
            fingerprints.add(fingerprint); questions.append(q)
            if len(questions) == body.count:
                break
        if len(questions) < body.count:
            raise HTTPException(400, f"Há apenas {len(questions)} questões válidas no banco selecionado; são necessárias 20.")
        title = item.get("title", "Simulado")
    else:
        q = {"type":"questao","status":"publicado", **visible_content_query(user)}
        topic_ids: list[str] = []
        selected_topic = None
        if body.course_id:
            course = await db.courses.find_one({"id": body.course_id, "status": "publicado"}, {"id":1,"name":1})
            if not course:
                raise HTTPException(404, "Curso não encontrado.")
        else:
            course = None
        if body.period_id:
            period = await db.periods.find_one({"id": body.period_id}, {"id":1,"course_id":1,"name":1,"number":1})
            if not period or (body.course_id and period.get("course_id") != body.course_id):
                raise HTTPException(400, "O período selecionado não pertence ao curso informado.")
        else:
            period = None
        if body.discipline_id:
            discipline = await db.disciplines.find_one({"id": body.discipline_id, "status": "publicado"}, {"id":1,"course_id":1,"period_id":1,"name":1})
            if not discipline:
                raise HTTPException(404, "Disciplina não encontrada.")
            if body.course_id and discipline.get("course_id") != body.course_id:
                raise HTTPException(400, "A disciplina selecionada não pertence ao curso informado.")
            if body.period_id and discipline.get("period_id") != body.period_id:
                raise HTTPException(400, "A disciplina selecionada não pertence ao período informado.")
        else:
            discipline = None
        if body.topic_id:
            selected_topic = await db.topics.find_one({"id": body.topic_id, "status": "publicado"}, {"id":1,"name":1,"course_id":1,"period_id":1,"discipline_id":1})
            if not selected_topic:
                raise HTTPException(404, "Assunto não encontrado.")
            if body.course_id and selected_topic.get("course_id") != body.course_id:
                raise HTTPException(400, "O assunto selecionado não pertence ao curso informado.")
            if body.period_id and selected_topic.get("period_id") != body.period_id:
                raise HTTPException(400, "O assunto selecionado não pertence ao período informado.")
            if body.discipline_id and selected_topic.get("discipline_id") != body.discipline_id:
                raise HTTPException(400, "O assunto selecionado não pertence à disciplina informada.")
            topic_ids = [selected_topic["id"]]
            title = "Simulado de " + selected_topic.get("name", "assunto")
        elif body.period_id:
            topics = await db.topics.find({"period_id":body.period_id,"status":"publicado"}, {"id":1,"name":1}).sort("name",1).to_list(3000)
            topic_ids = [t["id"] for t in topics]
            period = await db.periods.find_one({"id": body.period_id}, {"name":1, "number":1})
            title = "Simulado geral do " + ((period or {}).get("name") or f"{(period or {}).get('number', '')}º período")
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
        valid_docs = []
        fingerprints = set()
        for c in docs:
            options = list(c.get("data", {}).get("options", []))
            correct = c.get("data", {}).get("correct_index")
            statement = c.get("data", {}).get("statement") or c.get("title")
            if len(options) != 5 or not isinstance(correct, int) or not 0 <= correct < 5 or not str(statement).strip():
                continue
            fingerprint = hashlib.sha256((str(statement).strip() + "\n" + "\n".join(map(str, options))).encode("utf-8")).hexdigest()
            if fingerprint in fingerprints:
                continue
            fingerprints.add(fingerprint); valid_docs.append(c)
        if len(valid_docs) < body.count:
            raise HTTPException(400, f"Há apenas {len(valid_docs)} questões válidas disponíveis para os filtros escolhidos; são necessárias 20.")
        if body.shuffle_questions: random.shuffle(valid_docs)
        docs = valid_docs[:body.count]
        questions = [{"statement":c["data"].get("statement") or c["title"],"options":list(c["data"].get("options",[])),"correct_index":int(c["data"].get("correct_index",0)),"explanation":c["data"].get("explanation",""),"difficulty":c.get("difficulty",""),"topic_id":c.get("topic_id")} for c in docs]
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
    if len(body.answers) > len(doc.get("questions", [])):
        raise HTTPException(400, "Quantidade de respostas inválida.")
    if any(int(answer) < -1 or int(answer) > 4 for answer in body.answers):
        raise HTTPException(400, "Alternativa inválida enviada para o simulado.")
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
