from sqlmodel import SQLModel, Field
from typing import Optional

class Priority(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    level: int
