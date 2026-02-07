from typing import Annotated
from pydantic import BaseModel, EmailStr, Field

Password = Annotated[str, Field(min_length=8, max_length=128)]
Username = Annotated[str, Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_][a-zA-Z0-9_\-\.]{2,31}$")]

class TokenReply(BaseModel):
    access_token: str
    username: str
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: Password

class ClaimRequest(BaseModel):
    email: EmailStr
    password: Password
    username: Username
