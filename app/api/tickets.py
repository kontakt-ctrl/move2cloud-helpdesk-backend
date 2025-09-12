import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select as sqlalchemy_select
from sqlmodel import Session
from datetime import datetime

from app.models.ticket import Ticket, Comment, TicketRead, CommentOut, AuthorOut
from app.models.user import User
from app.api.users import get_current_user
from app.core.db import get_session

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketIn(BaseModel):
    title: str
    description: str
    category_id: Optional[int] = None
    priority_id: Optional[int] = None

@router.get("/new")
def new_ticket_form():
    return {
        "title": "",
        "description": "",
        "category_id": None,
        "priority_id": None
    }

@router.post("/", response_model=TicketRead)
def create_ticket(
    data: TicketIn,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
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
        session.commit()
        session.refresh(ticket)
        return TicketRead(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category_id=ticket.category_id,
            priority_id=ticket.priority_id,
            created_by=ticket.created_by,
            assigned_to=ticket.assigned_to,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            comments=[]
        )
    except Exception as e:
        logger.error("Błąd tworzenia zgłoszenia", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[TicketRead])
def list_tickets(
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        if user.role == "client":
            stmt = sqlalchemy_select(Ticket).where(Ticket.created_by == user.id)
        else:
            stmt = sqlalchemy_select(Ticket)
        result = session.exec(stmt)
        tickets = result.scalars().all()
        tickets_out = []
        for t in tickets:
            comments_query = session.exec(sqlalchemy_select(Comment).where(Comment.ticket_id == t.id))
            comments = []
            for c in comments_query.scalars().all():
                author_obj = session.get(User, c.author_id)
                author = AuthorOut(
                    id=author_obj.id,
                    email=author_obj.email,
                    full_name=author_obj.full_name
                ) if author_obj else None
                comments.append(
                    CommentOut(
                        id=c.id,
                        ticket_id=c.ticket_id,
                        content=c.content,
                        created_at=c.created_at,
                        author=author
                    )
                )
            tickets_out.append(
                TicketRead(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    category_id=t.category_id,
                    priority_id=t.priority_id,
                    created_by=t.created_by,
                    assigned_to=t.assigned_to,
                    status=t.status,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                    comments=comments
                )
            )
        return tickets_out
    except Exception as e:
        logger.error("Błąd pobierania listy zgłoszeń", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client" and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        comments_query = session.exec(sqlalchemy_select(Comment).where(Comment.ticket_id == ticket_id))
        comments = []
        for c in comments_query.scalars().all():
            author_obj = session.get(User, c.author_id)
            author = AuthorOut(
                id=author_obj.id,
                email=author_obj.email,
                full_name=author_obj.full_name
            ) if author_obj else None
            comments.append(
                CommentOut(
                    id=c.id,
                    ticket_id=c.ticket_id,
                    content=c.content,
                    created_at=c.created_at,
                    author=author
                )
            )
        return TicketRead(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category_id=ticket.category_id,
            priority_id=ticket.priority_id,
            created_by=ticket.created_by,
            assigned_to=ticket.assigned_to,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            comments=comments
        )
    except Exception as e:
        logger.error(f"Błąd pobierania zgłoszenia {ticket_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None

@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client":
            if ticket.created_by != user.id:
                raise HTTPException(status_code=403, detail="Forbidden")
        elif user.role not in ["helpdesk", "admin"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        if data.status is not None:
            ticket.status = data.status
        if data.assigned_to is not None and user.role in ["helpdesk", "admin"]:
            ticket.assigned_to = data.assigned_to
        ticket.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(ticket)
        comments_query = session.exec(sqlalchemy_select(Comment).where(Comment.ticket_id == ticket_id))
        comments = []
        for c in comments_query.scalars().all():
            author_obj = session.get(User, c.author_id)
            author = AuthorOut(
                id=author_obj.id,
                email=author_obj.email,
                full_name=author_obj.full_name
            ) if author_obj else None
            comments.append(
                CommentOut(
                    id=c.id,
                    ticket_id=c.ticket_id,
                    content=c.content,
                    created_at=c.created_at,
                    author=author
                )
            )
        return TicketRead(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category_id=ticket.category_id,
            priority_id=ticket.priority_id,
            created_by=ticket.created_by,
            assigned_to=ticket.assigned_to,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            comments=comments
        )
    except Exception as e:
        logger.error(f"Błąd aktualizacji zgłoszenia {ticket_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

class CommentIn(BaseModel):
    content: str

@router.post("/{ticket_id}/comment", response_model=CommentOut)
def add_comment(
    ticket_id: int,
    data: CommentIn,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Not found")
        if user.role == "client" and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        comment = Comment(ticket_id=ticket_id, author_id=user.id, content=data.content)
        session.add(comment)
        session.commit()
        session.refresh(comment)
        author = AuthorOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name
        )
        return CommentOut(
            id=comment.id,
            ticket_id=comment.ticket_id,
            content=comment.content,
            created_at=comment.created_at,
            author=author
        )
    except Exception as e:
        logger.error(f"Błąd dodawania komentarza do zgłoszenia {ticket_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
