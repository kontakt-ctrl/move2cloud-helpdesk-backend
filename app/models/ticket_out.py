from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    category_id: Optional[int] = None
    priority_id: Optional[int] = None
    created_by: int
    assigned_to: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
