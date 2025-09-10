from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    author_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    category_id: Optional[int] = Field(foreign_key="category.id")
    priority_id: Optional[int] = Field(foreign_key="priority.id")
    created_by: int = Field(foreign_key="user.id")
    assigned_to: Optional[int] = Field(foreign_key="user.id", default=None)
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
