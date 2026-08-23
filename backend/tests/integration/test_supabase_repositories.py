import pytest
from unittest.mock import MagicMock
from app.domain.entities import Chat, Message
from app.infrastructure.persistence.supabase_repo import SupabaseChatRepository, SupabaseMessageRepository

@pytest.mark.asyncio
async def test_supabase_chat_repository_crud():
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Mock get_all
    mock_order = MagicMock()
    mock_order.execute.return_value = MagicMock(data=[
        {
            "id": "chat-1",
            "title": "테스트 대화",
            "model": "gemini-3.1-flash-lite",
            "created_at": "2026-08-23T12:00:00",
            "updated_at": "2026-08-23T12:00:00"
        }
    ])
    mock_select = MagicMock()
    mock_select.order.return_value = mock_order
    mock_select.is_.return_value.order.return_value = mock_order
    mock_select.eq.return_value.order.return_value = mock_order
    mock_table.select.return_value = mock_select

    repo = SupabaseChatRepository(mock_client)
    chats = await repo.get_all()

    assert len(chats) == 1
    assert chats[0].id == "chat-1"
    assert chats[0].title == "테스트 대화"

    # Mock get_by_id
    mock_eq = MagicMock()
    mock_eq.execute.return_value = MagicMock(data=[
        {
            "id": "chat-1",
            "title": "테스트 대화",
            "model": "gemini-3.1-flash-lite",
            "created_at": "2026-08-23T12:00:00",
            "updated_at": "2026-08-23T12:00:00"
        }
    ])
    mock_select.eq.return_value = mock_eq
    chat = await repo.get_by_id("chat-1")
    assert chat is not None
    assert chat.id == "chat-1"

    # Mock create
    mock_insert = MagicMock()
    mock_insert.execute.return_value = MagicMock(data=[
        {
            "id": "new-chat-id",
            "title": "새 대화",
            "model": "gemini-3.1-flash-lite",
            "created_at": "2026-08-23T12:00:00",
            "updated_at": "2026-08-23T12:00:00"
        }
    ])
    mock_table.insert.return_value = mock_insert
    new_chat = await repo.create(title="새 대화")
    assert new_chat.id == "new-chat-id"

    # Mock delete
    mock_delete = MagicMock()
    mock_delete_eq = MagicMock()
    mock_delete_eq.execute.return_value = MagicMock(data=[])
    mock_delete.eq.return_value = mock_delete_eq
    mock_table.delete.return_value = mock_delete
    success = await repo.delete("chat-1")
    assert success is True


@pytest.mark.asyncio
async def test_supabase_message_repository_crud():
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Mock get_by_chat_id
    mock_order = MagicMock()
    mock_order.execute.return_value = MagicMock(data=[
        {
            "id": "msg-1",
            "chat_id": "chat-1",
            "sender": "user",
            "content": "안녕하세요",
            "image_url": None,
            "created_at": "2026-08-23T12:00:00"
        }
    ])
    mock_eq = MagicMock()
    mock_eq.order.return_value = mock_order
    mock_select = MagicMock()
    mock_select.eq.return_value = mock_eq
    mock_table.select.return_value = mock_select

    repo = SupabaseMessageRepository(mock_client)
    messages = await repo.get_by_chat_id("chat-1")
    assert len(messages) == 1
    assert messages[0].content == "안녕하세요"

    # Mock add
    mock_insert = MagicMock()
    mock_insert.execute.return_value = MagicMock(data=[
        {
            "id": "msg-2",
            "chat_id": "chat-1",
            "sender": "assistant",
            "content": "반갑습니다",
            "image_url": None,
            "created_at": "2026-08-23T12:01:00"
        }
    ])
    mock_table.insert.return_value = mock_insert
    new_msg = await repo.add(Message(chat_id="chat-1", sender="assistant", content="반갑습니다"))
    assert new_msg.id == "msg-2"

    # Mock delete_by_chat_id
    mock_delete = MagicMock()
    mock_delete_eq = MagicMock()
    mock_delete_eq.execute.return_value = MagicMock(data=[])
    mock_delete.eq.return_value = mock_delete_eq
    mock_table.delete.return_value = mock_delete
    success = await repo.delete_by_chat_id("chat-1")
    assert success is True
