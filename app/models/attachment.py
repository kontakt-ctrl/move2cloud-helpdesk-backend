from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    filename: str
    content_type: str
    path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
