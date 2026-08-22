import pytest
import json
from typing import AsyncGenerator
from app.domain.entities import Chat, Message
from app.domain.repositories import IChatRepository, IMessageRepository
from app.domain.services import ILLMService
from app.usecases.chat_usecases import ListChatsUseCase, CreateChatUseCase, DeleteChatUseCase, GetMessagesUseCase
from app.usecases.generate_usecase import GenerateResponseUseCase

class MockChatRepository(IChatRepository):
    def __init__(self):
        self.chats = {}

    async def get_all(self):
        return list(self.chats.values())

    async def get_by_id(self, chat_id: str):
        return self.chats.get(chat_id)

    async def create(self, title: str = "새 대화", model: str = "gemini-3.1-flash-lite"):
        chat = Chat(title=title, model=model)
        self.chats[chat.id] = chat
        return chat

    async def update_title(self, chat_id: str, title: str):
        if chat_id in self.chats:
            self.chats[chat_id].title = title
            return self.chats[chat_id]
        return None

    async def delete(self, chat_id: str):
        if chat_id in self.chats:
            del self.chats[chat_id]
            return True
        return False

class MockMessageRepository(IMessageRepository):
    def __init__(self):
        self.messages = []

    async def get_by_chat_id(self, chat_id: str):
        return [m for m in self.messages if m.chat_id == chat_id]

    async def add(self, message: Message):
        self.messages.append(message)
        return message

    async def delete_by_chat_id(self, chat_id: str):
        self.messages = [m for m in self.messages if m.chat_id != chat_id]
        return True

class MockLLMService(ILLMService):
    def __init__(self):
        self.last_history = None
        self.last_image_url = None

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        history=None,
        image_url=None
    ) -> AsyncGenerator[str, None]:
        self.last_history = history
        self.last_image_url = image_url
        chunks = ["Hello ", "world!"]
        for c in chunks:
            yield c


@pytest.mark.asyncio
async def test_create_and_list_chat_usecases():
    chat_repo = MockChatRepository()
    create_uc = CreateChatUseCase(chat_repo)
    list_uc = ListChatsUseCase(chat_repo)

    chat = await create_uc.execute(title="Test Chat", model="gemini-3.5-flash")
    assert chat.title == "Test Chat"
    assert chat.model == "gemini-3.5-flash"

    chats = await list_uc.execute()
    assert len(chats) == 1
    assert chats[0].id == chat.id

@pytest.mark.asyncio
async def test_generate_response_usecase():
    chat_repo = MockChatRepository()
    msg_repo = MockMessageRepository()
    llm_service = MockLLMService()

    gen_uc = GenerateResponseUseCase(chat_repo, msg_repo, llm_service)

    events = []
    async for event in gen_uc.execute(prompt="Greeting message"):
        events.append(event)

    assert len(events) >= 3  # chat_id event, chunk events, done event
    assert "data: {" in events[0]
    
    # Verify messages saved
    chats = await chat_repo.get_all()
    assert len(chats) == 1
    messages = await msg_repo.get_by_chat_id(chats[0].id)
    assert len(messages) == 2  # user and assistant
    assert messages[0].sender == "user"
    assert messages[0].content == "Greeting message"
    assert messages[1].sender == "assistant"
    assert messages[1].content == "Hello world!"

@pytest.mark.asyncio
async def test_generate_response_usecase_multiturn():
    chat_repo = MockChatRepository()
    msg_repo = MockMessageRepository()
    llm_service = MockLLMService()

    gen_uc = GenerateResponseUseCase(chat_repo, msg_repo, llm_service)

    # 1. First turn
    events1 = []
    async for event in gen_uc.execute(prompt="First message"):
        events1.append(event)
    
    chats = await chat_repo.get_all()
    chat_id = chats[0].id

    # 2. Second turn with chat_id
    events2 = []
    async for event in gen_uc.execute(prompt="Second message", chat_id=chat_id, image_url="data:image/png;base64,abc"):
        events2.append(event)

    # Verify that history was passed to llm_service in second turn
    assert llm_service.last_history is not None
    assert len(llm_service.last_history) == 2  # first turn user & assistant
    assert llm_service.last_history[0].content == "First message"
    assert llm_service.last_image_url == "data:image/png;base64,abc"


class MockLLMServiceWithSuggestions(ILLMService):
    async def generate_stream(
        self,
        prompt: str,
        model: str,
        history=None,
        image_url=None
    ) -> AsyncGenerator[str, None]:
        chunks = [
            "안녕하세요! ",
            "오늘의 커피를 ",
            "추천해 드릴게요.\n\n<sugg",
            "estions>\n[\n",
            '  "원두 보관법은?",\n',
            '  "드립 커피 추출 팁은?",\n',
            '  "에스프레소 머신 추천해줘"\n',
            "]\n</suggestions>"
        ]
        for c in chunks:
            yield c

@pytest.mark.asyncio
async def test_generate_response_usecase_with_suggestions():
    chat_repo = MockChatRepository()
    msg_repo = MockMessageRepository()
    llm_service = MockLLMServiceWithSuggestions()

    gen_uc = GenerateResponseUseCase(chat_repo, msg_repo, llm_service)

    events = []
    async for event in gen_uc.execute(prompt="커피 추천해줘"):
        events.append(event)

    # Check SSE events
    event_data = [json.loads(e.replace("data: ", "").strip()) for e in events if e.strip()]
    event_types = [d["type"] for d in event_data]

    assert "chat_id" in event_types
    assert "chunk" in event_types
    assert "suggested_questions" in event_types
    assert "done" in event_types

    # Verify that raw suggestions tag was NOT leaked into chunk stream
    chunk_texts = [d["text"] for d in event_data if d["type"] == "chunk"]
    accumulated_chunk = "".join(chunk_texts)
    assert "<suggestions>" not in accumulated_chunk
    assert "원두 보관법은?" not in accumulated_chunk
    assert accumulated_chunk == "안녕하세요! 오늘의 커피를 추천해 드릴게요.\n\n"

    # Verify suggested questions
    sugg_event = next(d for d in event_data if d["type"] == "suggested_questions")
    assert len(sugg_event["questions"]) == 3
    assert sugg_event["questions"][0] == "원두 보관법은?"
    assert sugg_event["questions"][1] == "드립 커피 추출 팁은?"
    assert sugg_event["questions"][2] == "에스프레소 머신 추천해줘"

    # Verify message in DB does not contain the suggestions tag
    chats = await chat_repo.get_all()
    messages = await msg_repo.get_by_chat_id(chats[0].id)
    assistant_msg = next(m for m in messages if m.sender == "assistant")
    assert assistant_msg.content == "안녕하세요! 오늘의 커피를 추천해 드릴게요."


