from pydantic import BaseModel, Field
from typing import Optional, List

class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    provider: Optional[str] = "llamacpp"

class ConversationResponse(BaseModel):
    id: str
    title: str
    provider: str
    created_at: str

class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]

