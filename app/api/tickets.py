import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.ticket import Ticket, CommentModel
from app.api.users import get_current_user
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketIn(BaseModel):
    title: str
    description: str
    category_id: Optional[str] = None
    priority_id: Optional[str] = None

@router.post("/")
async def create_ticket(data: TicketIn, user=Depends(get_current_user)):
    try:
        ticket = Ticket(
            title=data.title,
            description=data.description,
            category_id=data.category_id,
            priority_id=data.priority_id,
            created_by=str(user.id)
        )
        await ticket.insert()
        return ticket
    except Exception as e:
        logger.error("Błąd tworzenia zgłoszenia", exc_info=True)
        raise

@router.get("/")
async def list_tickets(user=Depends(get_current_user)):
    try:
        if user.role == "client":
            return await Ticket.find(Ticket.created_by == str(user.id)).to_list()
        return await Ticket.find_all().to_list()
    except Exception as e:
        logger.error("Błąd pobierania listy zgłoszeń", exc_info=True)
        raise

@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str, user=Depends(get_current_user)):
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client" and ticket.created_by != str(user.id):
            raise HTTPException(status_code=403, detail="Forbidden")
        return ticket
    except Exception as e:
        logger.error(f"Błąd pobierania zgłoszenia {ticket_id}", exc_info=True)
        raise

class TicketUpdate(BaseModel):
    status: Optional[str]
    assigned_to: Optional[str]

@router.patch("/{ticket_id}")
async def update_ticket(ticket_id: str, data: TicketUpdate, user=Depends(get_current_user)):
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role not in ["helpdesk", "admin"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        if data.status:
            ticket.status = data.status
        if data.assigned_to:
            ticket.assigned_to = data.assigned_to
        await ticket.save()
        return ticket
    except Exception as e:
        logger.error(f"Błąd aktualizacji zgłoszenia {ticket_id}", exc_info=True)
        raise

class CommentIn(BaseModel):
    content: str

@router.post("/{ticket_id}/comment")
async def add_comment(ticket_id: str, data: CommentIn, user=Depends(get_current_user)):
    try:
        ticket = await Ticket.get(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client" and ticket.created_by != str(user.id):
            raise HTTPException(status_code=403, detail="Forbidden")
        comment = CommentModel(author_id=str(user.id), content=data.content)
        ticket.comments.append(comment)
        await ticket.save()
        return ticket
    except Exception as e:
        logger.error(f"Błąd dodawania komentarza do zgłoszenia {ticket_id}", exc_info=True)
        raise
