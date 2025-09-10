from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CommentModel(BaseModel):
    author_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Ticket(Document):
    title: str
    description: str
    status: str = "open"  # open, in_progress, resolved, closed
    priority_id: Optional[str] = None
    category_id: Optional[str] = None
    created_by: str
    assigned_to: Optional[str] = None
    comments: List[CommentModel] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tickets"
