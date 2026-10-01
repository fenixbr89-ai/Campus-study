"""Shared Mongo handle — import `client`/`db` from here (server.py, routers, seed.py)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, IndexModel

load_dotenv(Path(__file__).parent.parent / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

logger = logging.getLogger(__name__)

# One entry per collection: every field a route filters, sorts, or dedupes on. Applied by ensure_indexes() at startup.
INDEXES: dict[str, list[IndexModel]] = {
    "users": [IndexModel([("id", ASCENDING)], name="id", unique=True),
              IndexModel([("cpf_hash", ASCENDING)], name="cpf_hash", unique=True),
              IndexModel([("email", ASCENDING)], name="email", unique=True)],
    "courses": [IndexModel([("id", ASCENDING)], name="id", unique=True), IndexModel([("slug", ASCENDING)], name="slug", unique=True)],
    "periods": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                IndexModel([("course_id", ASCENDING), ("number", ASCENDING)], name="course_number", unique=True)],
    "disciplines": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                    IndexModel([("period_id", ASCENDING), ("slug", ASCENDING)], name="period_slug"),
                    IndexModel([("course_id", ASCENDING)], name="course_id")],
    "topics": [IndexModel([("id", ASCENDING)], name="id", unique=True),
               IndexModel([("discipline_id", ASCENDING), ("slug", ASCENDING)], name="disc_slug")],
    "contents": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                 IndexModel([("topic_id", ASCENDING), ("status", ASCENDING)], name="topic_status"),
                 IndexModel([("type", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)], name="type_status_created"),
                 IndexModel([("discipline_id", ASCENDING)], name="discipline_id"),
                 IndexModel([("views", DESCENDING)], name="views")],
    "favorites": [IndexModel([("user_id", ASCENDING), ("content_id", ASCENDING)], name="user_content", unique=True)],
    "progress": [IndexModel([("user_id", ASCENDING), ("topic_id", ASCENDING)], name="user_topic", unique=True)],
    "history": [IndexModel([("user_id", ASCENDING), ("at", DESCENDING)], name="user_at")],
    "notes": [IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)], name="user_updated")],
    "daily_stats": [IndexModel([("user_id", ASCENDING), ("date", ASCENDING)], name="user_date", unique=True)],
    "user_items": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                   IndexModel([("user_id", ASCENDING), ("kind", ASCENDING), ("updated_at", DESCENDING)], name="user_kind")],
    "exams": [IndexModel([("id", ASCENDING)], name="id", unique=True),
              IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_created")],
    "exam_plans": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                   IndexModel([("user_id", ASCENDING), ("exam_date", ASCENDING)], name="user_exam_date")],
    "exam_tasks": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                   IndexModel([("user_id", ASCENDING), ("exam_plan_id", ASCENDING), ("task_date", ASCENDING), ("kind", ASCENDING)], name="user_plan_date_kind", unique=True)],
    "weekly_goals": [IndexModel([("user_id", ASCENDING), ("week_start", ASCENDING)], name="user_week", unique=True)],
    "study_plans": [IndexModel([("id", ASCENDING)], name="id", unique=True), IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)], name="user_updated")],
    "study_reviews": [IndexModel([("id", ASCENDING)], name="id", unique=True), IndexModel([("user_id", ASCENDING), ("due_date", ASCENDING), ("completed", ASCENDING)], name="user_due")],
    "study_sessions": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                        IndexModel([("user_id", ASCENDING), ("status", ASCENDING)], name="user_status"),
                        IndexModel([("user_id", ASCENDING), ("started_at", DESCENDING)], name="user_started")],
    "conversations": [IndexModel([("id", ASCENDING)], name="id", unique=True),
                      IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)], name="user_updated")],
    "password_resets": [IndexModel([("token_hash", ASCENDING)], name="token_hash"),
                        IndexModel([("expires_at", ASCENDING)], name="expires_ttl", expireAfterSeconds=86400)],
    "submissions": [IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], name="status_created")],
    "search_logs": [IndexModel([("term", ASCENDING)], name="term", unique=True)],
    "admin_logs": [IndexModel([("at", DESCENDING)], name="at")],
    "stripe_events": [IndexModel([("event_id", ASCENDING)], name="event_id", unique=True)],
    "stripe_subscriptions": [IndexModel([("subscription_id", ASCENDING)], name="subscription_id", unique=True), IndexModel([("user_id", ASCENDING)], name="user_id")],
    "ai_generation_jobs": [IndexModel([("id", ASCENDING)], name="id", unique=True), IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], name="status_created")],
    "resource_sync_jobs": [IndexModel([("id", ASCENDING)], name="id", unique=True), IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], name="status_created")],
}


async def ensure_indexes() -> None:
    # Older V1.3 used a unique exam_tasks index without `kind`, which prevented
    # different task types from sharing the same plan/date. Remove that legacy
    # index before applying the corrected composite constraint.
    try:
        await db.exam_tasks.drop_index("user_plan_date")
    except Exception:
        pass
    for collection, models in INDEXES.items():
        for model in models:  # one at a time so a bad spec skips only itself
            try:
                await db[collection].create_indexes([model])
            except Exception as exc:  # never block boot on an index; the log line names what to fix
                logger.error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)
