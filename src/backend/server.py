import asyncio
import logging
from datetime import datetime, timezone
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from bson import ObjectId
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from lib.db import client, db, ensure_indexes  # noqa: E402
from routers import admin, auth, catalog, study, features, payments, ai, support, system_status


async def _ai_generation_worker(stop_event: asyncio.Event):
    """Process queued AI curriculum generation jobs one topic at a time.

    The API server runs on Render, so this long-running worker survives normal HTTP
    response completion and lets the admin enqueue the whole catalog instead of
    manually creating content topic by topic.
    """
    from routers.ai import generate_topic_pack
    while not stop_event.is_set():
        job = await db.ai_generation_jobs.find_one_and_update(
            {"status": "queued"},
            {"$set": {"status": "running", "started_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}},
            sort=[("created_at", 1)],
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0},
        )
        if not job:
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                pass
            continue
        topic_ids = job.get("topic_ids", [])
        processed = int(job.get("processed", 0))
        failed = int(job.get("failed", 0))
        try:
            while processed < len(topic_ids) and not stop_event.is_set():
                topic_id = topic_ids[processed]
                try:
                    await generate_topic_pack(topic_id)
                except Exception as exc:
                    failed += 1
                    logging.getLogger("campus.ai.worker").exception("AI generation failed for %s: %s", topic_id, exc)
                processed += 1
                await db.ai_generation_jobs.update_one(
                    {"id": job["id"]},
                    {"$set": {"processed": processed, "failed": failed, "updated_at": datetime.now(timezone.utc)}}
                )
            final_status = "completed" if processed >= len(topic_ids) else "paused"
            await db.ai_generation_jobs.update_one(
                {"id": job["id"]},
                {"$set": {"status": final_status, "processed": processed, "failed": failed, "finished_at": datetime.now(timezone.utc) if final_status == "completed" else None, "updated_at": datetime.now(timezone.utc)}}
            )
        except Exception as exc:
            await db.ai_generation_jobs.update_one({"id": job["id"]}, {"$set": {"status": "failed", "error": str(exc), "processed": processed, "failed": failed + 1, "updated_at": datetime.now(timezone.utc)}})


async def _seed_catalog_after_startup():
    """Seed the catalog after the HTTP server is accepting traffic."""
    try:
        from seed import seed_curriculum
        await seed_curriculum()
        logging.getLogger("campus.seed").info("Catalog seed concluído.")
    except Exception:
        logging.getLogger("campus.seed").exception(
            "Catalog seed failed; API remains available."
        )


async def lifespan(app: FastAPI):
    app.state.index_task = asyncio.create_task(ensure_indexes())
    # Do not block startup on the large catalog seed.
    app.state.seed_task = asyncio.create_task(_seed_catalog_after_startup())
    # A background catalog job cannot survive a process restart. Mark it paused so the
    # administrator can resume from the persisted processed_topic_ids instead of losing state.
    await db.resource_sync_jobs.update_many(
        {"status": {"$in": ["queued", "running"]}},
        {"$set": {"status": "paused", "error": "Servidor reiniciado; a sincronização foi pausada e pode ser retomada.", "updated_at": datetime.now(timezone.utc)}}
    )
    await db.ai_generation_jobs.update_many(
        {"status": "running"},
        {"$set": {"status": "queued", "updated_at": datetime.now(timezone.utc)}}
    )
    await db.content_imports.update_many(
        {"status": "processing"},
        {"$set": {"status": "queued", "updated_at": datetime.now(timezone.utc)}}
    )
    app.state.ai_stop_event = asyncio.Event()
    app.state.ai_worker = asyncio.create_task(_ai_generation_worker(app.state.ai_stop_event))
    app.state.import_stop_event = asyncio.Event()
    app.state.import_worker = asyncio.create_task(admin.content_import_worker(app.state.import_stop_event))
    yield
    app.state.ai_stop_event.set()
    app.state.import_stop_event.set()
    app.state.ai_worker.cancel()
    app.state.import_worker.cancel()
    try:
        await app.state.ai_worker
    except asyncio.CancelledError:
        pass
    try:
        await app.state.import_worker
    except asyncio.CancelledError:
        pass
    client.close()


app = FastAPI(lifespan=lifespan, title="Campus Study API")
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Campus Study API", "version": "V1"}


@api_router.get("/health")
async def health():
    await db.command("ping")
    return {"status": "ok", "service": "campus-study-api", "version": "V1"}



@api_router.get("/uploads/{file_id}")
async def uploaded_file(file_id: str):
    try:
        oid = ObjectId(file_id)
    except Exception as exc:
        raise HTTPException(404, "Arquivo não encontrado.") from exc
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
    try:
        stream = await bucket.open_download_stream(oid)
    except Exception as exc:
        raise HTTPException(404, "Arquivo não encontrado.") from exc
    content_type = (stream.metadata or {}).get("content_type", "application/octet-stream")
    filename = stream.filename or "arquivo"
    async def iterator():
        while True:
            chunk = await stream.readchunk()
            if not chunk:
                break
            yield chunk
    safe_filename = filename.replace(chr(34), "")
    return StreamingResponse(iterator(), media_type=content_type, headers={"Content-Disposition": f'inline; filename="{safe_filename}"'})

for module in (auth, catalog, study, admin, features, payments, ai, support, system_status):
    api_router.include_router(module.router)

cors_origins = [x.strip() for x in os.environ.get("CORS_ORIGINS", "").split(",") if x.strip()]
if not cors_origins:
    # Same-origin/local development fallback. Production deployments should set CORS_ORIGINS
    # explicitly to the Vercel origin(s); wildcard + credentialed cookies is not safe.
    cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Include the router in the main app — must stay the last statement.
app.include_router(api_router)
