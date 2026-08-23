from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

@dataclass
class Message:
    chat_id: str
    sender: str  # 'user' | 'assistant'
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Chat:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "새 대화"
    model: str = "gemini-3.1-flash-lite"
    user_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
