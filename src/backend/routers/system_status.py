"""Public system status with Admin-only writes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.auth import admin_user, log_admin
from lib.db import db
from lib.security import now_utc
from models.schemas import SystemStatus, SystemStatusIn, Message

router = APIRouter(prefix="/system-status", tags=["system-status"])

DEFAULT = {
    "overall": "operacional", "message": "Todos os serviços estão operacionais.",
    "maintenance": False, "maintenance_message": "",
    "services": [
        {"name": "Aplicativo", "status": "operacional", "description": ""},
        {"name": "API", "status": "operacional", "description": ""},
        {"name": "Conteúdos", "status": "operacional", "description": ""},
    ],
    "incidents": [],
}

@router.get("", response_model=SystemStatus)
async def public_status():
    d = await db.system_status.find_one({"id": "global"}, {"_id": 0})
    return SystemStatus(**{**DEFAULT, **(d or {})})

@router.put("", response_model=SystemStatus)
async def update_status(body: SystemStatusIn, admin: dict = Depends(admin_user)):
    doc = body.model_dump()
    doc.update({"id": "global", "updated_at": now_utc(), "updated_by": admin["id"]})
    await db.system_status.update_one({"id": "global"}, {"$set": doc}, upsert=True)
    await log_admin(admin, "atualizou status do sistema", "system_status", "global")
    return SystemStatus(**{**doc})
