from pydantic import BaseModel, Field
from typing import Optional

class MessageCreate(BaseModel):
    chat_id: Optional[str] = None
    sender: str  # 'user' or 'assistant'
    content: str
    image_url: Optional[str] = None
    model: Optional[str] = "gemini-3.1-flash-lite"

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    sender: str
    content: str
    image_url: Optional[str] = None
    created_at: str

class ChatCreate(BaseModel):
    title: Optional[str] = "새 대화"
    model: Optional[str] = "gemini-3.1-flash-lite"

class ChatResponse(BaseModel):
    id: str
    title: str
    model: str
    created_at: str
    updated_at: str

class GenerateRequest(BaseModel):
    prompt: str
    chat_id: Optional[str] = None
    model: str = "gemini-3.1-flash-lite"
    image_url: Optional[str] = None
