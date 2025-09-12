from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    priority_id: Optional[int] = Field(default=None, foreign_key="priority.id")
    created_by: int
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    author_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

# Nowy model autora komentarza do zwracania w API
class AuthorOut(BaseModel):
    id: int
    email: str
    full_name: str

# Komentarz z polem author
class CommentOut(BaseModel):
    id: int
    ticket_id: int
    content: str
    created_at: datetime
    author: AuthorOut

    class Config:
        orm_mode = True

# TicketRead z listą komentarzy z autorami
class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    category_id: Optional[int]
    priority_id: Optional[int]
    created_by: int
    assigned_to: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True
