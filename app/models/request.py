from pydantic import BaseModel

class MessageRequest(BaseModel):
    message: str
    username: str

class MessageResponse(BaseModel):
    response: str