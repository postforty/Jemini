import pytest
from app.domain.entities import Chat, Message
from app.infrastructure.persistence.in_memory_repo import InMemoryChatRepository, InMemoryMessageRepository

@pytest.mark.asyncio
async def test_in_memory_chat_repository_crud():
    repo = InMemoryChatRepository(initial_chats=[])
    
    # 1. Get initial chats (empty)
    chats = await repo.get_all()
    assert len(chats) == 0

    # 2. Create chat
    created = await repo.create(title="Coffee App Plan", model="gemini-3.5-flash")
    assert created.title == "Coffee App Plan"
    assert created.model == "gemini-3.5-flash"

    # 3. Get by id
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "Coffee App Plan"

    # 4. Update title
    updated = await repo.update_title(created.id, "Updated Title")
    assert updated is not None
    assert updated.title == "Updated Title"

    # 5. Delete chat
    deleted = await repo.delete(created.id)
    assert deleted is True

    # 6. Verify empty again
    assert len(await repo.get_all()) == 0

@pytest.mark.asyncio
async def test_in_memory_message_repository_crud():
    repo = InMemoryMessageRepository(initial_messages=[])

    msg = Message(chat_id="chat-999", sender="user", content="Hello!")
    added = await repo.add(msg)
    assert added.content == "Hello!"

    messages = await repo.get_by_chat_id("chat-999")
    assert len(messages) == 1
    assert messages[0].content == "Hello!"

    await repo.delete_by_chat_id("chat-999")
    assert len(await repo.get_by_chat_id("chat-999")) == 0
