import pytest
from app.domain.entities import Chat, Message

def test_chat_entity_default_creation():
    chat = Chat()
    assert chat.id is not None
    assert chat.title == "새 대화"
    assert chat.model == "gemini-3.1-flash-lite"
    assert chat.created_at is not None

def test_message_entity_creation():
    msg = Message(chat_id="chat-123", sender="user", content="Hello world")
    assert msg.id is not None
    assert msg.chat_id == "chat-123"
    assert msg.sender == "user"
    assert msg.content == "Hello world"
    assert msg.image_url is None
