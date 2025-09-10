from beanie import Document
from pydantic import Field

class Priority(Document):
    name: str = Field(..., unique=True)
    level: int = Field(..., ge=1, le=10)  # 1 - najniższy, 10 - najwyższy

    class Settings:
        name = "priorities"