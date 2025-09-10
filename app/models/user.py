from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing import Literal, Optional

class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: str = ""
    role: Literal["client", "helpdesk", "admin"] = "client"
    is_active: bool = True

    class Settings:
        name = "users"