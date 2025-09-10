import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.ticket import Ticket, Comment
from app.api.users import get_current_user
from app.core.db import async_session

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketIn(BaseModel):
    title: str
    description: str
    category_id: Optional[int] = None
    priority_id: Optional[int] = None

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.post("/", response_model=Ticket)
async def create_ticket(
    data: TicketIn,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = Ticket(
            title=data.title,
            description=data.description,
            category_id=data.category_id,
            priority_id=data.priority_id,
            created_by=user.id
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
        return ticket
    except Exception as e:
        logger.error("Błąd tworzenia zgłoszenia", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[Ticket])
async def list_tickets(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        if user.role == "client":
            result = await session.execute(select(Ticket).where(Ticket.created_by == user.id))
        else:
            result = await session.execute(select(Ticket))
        tickets = result.scalars().all()
        return tickets
    except Exception as e:
        logger.error("Błąd pobierania listy zgłoszeń", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client" and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return ticket
    except Exception as e:
        logger.error(f"Błąd pobierania zgłoszenia {ticket_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

class TicketUpdate(BaseModel):
    status: Optional[str]
    assigned_to: Optional[int]

@router.patch("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role not in ["helpdesk", "admin"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        if data.status:
            ticket.status = data.status
        if data.assigned_to:
            ticket.assigned_to = data.assigned_to
        ticket.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(ticket)
        return ticket
    except Exception as e:
        logger.error(f"Błąd aktualizacji zgłoszenia {ticket_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

class CommentIn(BaseModel):
    content: str

@router.post("/{ticket_id}/comment", response_model=Comment)
async def add_comment(
    ticket_id: int,
    data: CommentIn,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client" and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        comment = Comment(ticket_id=ticket_id, author_id=user.id, content=data.content)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment
    except Exception as e:
        logger.error(f"Błąd dodawania komentarza do zgłoszenia {ticket_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
