from sqlmodel import SQLModel, Field
from typing import Optional
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

# Dodajemy model Pydantic do odpowiedzi API
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

    class Config:
        orm_mode = True
