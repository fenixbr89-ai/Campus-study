"""Authenticated student support tickets and staff replies."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.auth import current_user, admin_user, log_admin
from lib.db import db
from lib.security import now_utc
from lib.email import send_email
from models.schemas import Message, SupportReplyIn, SupportTicket, SupportTicketIn

router = APIRouter(prefix="/support", tags=["support"])

def _ticket(d: dict, include_private: bool = False) -> SupportTicket:
    data = dict(d)
    if not include_private:
        data.pop("user_email", None)
        data.pop("user_name", None)
    return SupportTicket(**data)

@router.post("/tickets", response_model=SupportTicket)
async def create_ticket(body: SupportTicketIn, user: dict = Depends(current_user)):
    now = now_utc()
    doc = {
        "id": str(uuid.uuid4()), "user_id": user["id"], "user_name": user["name"],
        "user_email": user["email"], "category": body.category, "subject": body.subject.strip(),
        "message": body.message.strip(), "status": "aberto", "replies": [],
        "created_at": now, "updated_at": now,
    }
    await db.support_tickets.insert_one(doc)
    try:
        from lib.settings import get_settings
        settings = await get_settings()
        support_email = settings.get("support_email")
        if support_email:
            await send_email(
                to=support_email,
                subject=f"Novo feedback — {doc['subject']}",
                html=f"<h2>Novo contato no Campus Study</h2><p><b>Aluno:</b> {doc['user_name']} ({doc['user_email']})</p><p><b>Categoria:</b> {doc['category']}</p><p><b>Assunto:</b> {doc['subject']}</p><p>{doc['message'].replace(chr(10), '<br>')}</p>",
            )
    except Exception:
        pass
    return _ticket(doc)

@router.get("/tickets", response_model=list[SupportTicket])
async def my_tickets(user: dict = Depends(current_user)):
    docs = await db.support_tickets.find({"user_id": user["id"]}, {"_id": 0}).sort("updated_at", -1).limit(100).to_list(100)
    return [_ticket(d) for d in docs]

@router.get("/tickets/{ticket_id}", response_model=SupportTicket)
async def my_ticket(ticket_id: str, user: dict = Depends(current_user)):
    d = await db.support_tickets.find_one({"id": ticket_id, "user_id": user["id"]}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Chamado não encontrado.")
    return _ticket(d)

@router.post("/tickets/{ticket_id}/reply", response_model=SupportTicket)
async def student_reply(ticket_id: str, body: SupportReplyIn, user: dict = Depends(current_user)):
    d = await db.support_tickets.find_one({"id": ticket_id, "user_id": user["id"]}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Chamado não encontrado.")
    reply = {"id": str(uuid.uuid4()), "author_id": user["id"], "author_name": user["name"],
             "author_role": user.get("role", "student"), "message": body.message.strip(), "at": now_utc()}
    await db.support_tickets.update_one({"id": ticket_id}, {"$push": {"replies": reply}, "$set": {"status": "aberto", "updated_at": now_utc()}})
    d["replies"] = [*d.get("replies", []), reply]; d["status"] = "aberto"; d["updated_at"] = now_utc()
    return _ticket(d)

@router.get("/admin/tickets", response_model=list[SupportTicket])
async def admin_tickets(admin: dict = Depends(admin_user)):
    docs = await db.support_tickets.find({}, {"_id": 0}).sort("updated_at", -1).limit(500).to_list(500)
    return [_ticket(d, True) for d in docs]

@router.post("/admin/tickets/{ticket_id}/reply", response_model=SupportTicket)
async def admin_reply(ticket_id: str, body: SupportReplyIn, admin: dict = Depends(admin_user)):
    d = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not d: raise HTTPException(404, "Chamado não encontrado.")
    reply = {"id": str(uuid.uuid4()), "author_id": admin["id"], "author_name": admin["name"],
             "author_role": admin.get("role", "admin"), "message": body.message.strip(), "at": now_utc()}
    await db.support_tickets.update_one({"id": ticket_id}, {"$push": {"replies": reply}, "$set": {"status": "em_analise", "updated_at": now_utc()}})
    await log_admin(admin, "respondeu chamado", "support_ticket", ticket_id)
    try:
        await send_email(
            to=d.get("user_email", ""),
            subject=f"Resposta do Campus Study — {d.get('subject', '')}",
            html=f"<h2>Seu chamado recebeu uma resposta</h2><p><b>Assunto:</b> {d.get('subject', '')}</p><p><b>Equipe Campus Study:</b></p><p>{reply['message'].replace(chr(10), '<br>')}</p><p>Acesse o aplicativo para continuar a conversa.</p>",
        )
    except Exception:
        pass
    d["replies"] = [*d.get("replies", []), reply]; d["status"] = "em_analise"; d["updated_at"] = now_utc()
    return _ticket(d, True)

@router.patch("/admin/tickets/{ticket_id}/status", response_model=Message)
async def admin_ticket_status(ticket_id: str, status: str, admin: dict = Depends(admin_user)):
    allowed = {"aberto", "em_analise", "aguardando_usuario", "resolvido", "fechado"}
    if status not in allowed: raise HTTPException(400, "Status de chamado inválido.")
    result = await db.support_tickets.update_one({"id": ticket_id}, {"$set": {"status": status, "updated_at": now_utc()}})
    if not result.modified_count: raise HTTPException(404, "Chamado não encontrado.")
    await log_admin(admin, f"alterou status para {status}", "support_ticket", ticket_id)
    return Message(message="Status atualizado.")
