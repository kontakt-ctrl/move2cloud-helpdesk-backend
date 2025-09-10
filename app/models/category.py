from beanie import Document
from pydantic import Field

class Category(Document):
    name: str = Field(..., unique=True)

    class Settings:
        name = "categories"