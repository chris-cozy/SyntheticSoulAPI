from datetime import datetime
from pydantic import BaseModel

class MessageRequest(BaseModel):
    message: str
    username: str

class MessageResponse(BaseModel):
    response: str

class ImplicitlyAddressedResponse(BaseModel):
    implicitly_addressed: str

class ExtendedMessageRequest(BaseModel):
    message: str
    sender: str
    timestamp: datetime
    
class ImplicitlyAddressedRequest(BaseModel):
    message_list: list[object]