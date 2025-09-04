from pydantic import BaseModel, EmailStr


class TokenReply(BaseModel):
    access_token: str
    username: str
    # optionally include "expires_in": ACCESS_TTL_MIN * 60

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ClaimRequest(BaseModel):
    email: EmailStr
    password: str