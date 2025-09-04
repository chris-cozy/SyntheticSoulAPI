from pydantic import BaseModel, EmailStr

class TokenReply(BaseModel):
    access_token: str
    username: str
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ClaimRequest(BaseModel):
    email: EmailStr
    password: str
    username: str