from typing import List, Optional, Dict
from datetime import datetime
import uuid
from app.domain.entities import Chat, Message
from app.domain.repositories import IChatRepository, IMessageRepository

class InMemoryChatRepository(IChatRepository):
    def __init__(self, initial_chats: Optional[List[Chat]] = None):
        self._chats: Dict[str, Chat] = {}
        if initial_chats is not None:
            for chat in initial_chats:
                self._chats[chat.id] = chat
        else:
            # Seed default demo chats if empty
            c1 = Chat(
                id="11111111-1111-1111-1111-111111111111",
                title="커피 앱 기획 비판적 분석",
                model="gemini-3.5-flash"
            )
            c2 = Chat(
                id="22222222-2222-2222-2222-222222222222",
                title="커피 주문 앱 개발 고려사항",
                model="gemini-3.1-flash-lite"
            )
            self._chats[c1.id] = c1
            self._chats[c2.id] = c2

    async def get_all(self) -> List[Chat]:
        chats = list(self._chats.values())
        # Sort by created_at descending
        chats.sort(key=lambda x: x.created_at, reverse=True)
        return chats

    async def get_by_id(self, chat_id: str) -> Optional[Chat]:
        return self._chats.get(chat_id)

    async def create(self, title: str = "새 대화", model: str = "gemini-3.1-flash-lite") -> Chat:
        chat = Chat(title=title, model=model)
        self._chats[chat.id] = chat
        return chat

    async def update_title(self, chat_id: str, title: str) -> Optional[Chat]:
        chat = self._chats.get(chat_id)
        if chat:
            chat.title = title
            chat.updated_at = datetime.now().isoformat()
            return chat
        return None

    async def delete(self, chat_id: str) -> bool:
        if chat_id in self._chats:
            del self._chats[chat_id]
            return True
        return False

class InMemoryMessageRepository(IMessageRepository):
    def __init__(self, initial_messages: Optional[List[Message]] = None):
        self._messages: List[Message] = []
        if initial_messages is not None:
            self._messages = list(initial_messages)
        else:
            # Seed default demo messages
            m1 = Message(
                id=str(uuid.uuid4()),
                chat_id="11111111-1111-1111-1111-111111111111",
                sender="user",
                content="커피 주문 앱 기획안에 대해 비판적인 시각으로 분석해줘."
            )
            m2 = Message(
                id=str(uuid.uuid4()),
                chat_id="11111111-1111-1111-1111-111111111111",
                sender="assistant",
                content="커피 주문 앱 기획 시 고려해야 할 비판적 관점은 다음과 같습니다:\n\n1. **기존 시장 과점 및 사용자 이탈 위험**: 스타벅스 사이렌 오더나 배달의민족 등 기존 강자들과의 차별점 부재 시 유저 유입이 어렵습니다.\n2. **매장 POS 시스템 연동 복잡성**: 각 커피 프랜차이즈 및 개인 카페의 POS 솔루션과 실시간 주문 연동 시 커스텀 개발 비용이 증가합니다.\n3. **픽업 시간 예측의 정확도**: 출퇴근 시간 대기열 증가 시 사용자 불만이 폭증할 수 있습니다."
            )
            m3 = Message(
                id=str(uuid.uuid4()),
                chat_id="22222222-2222-2222-2222-222222222222",
                sender="user",
                content="커피 주문 앱 개발할 때 중요한 기술적 고려사항이 뭐야?"
            )
            m4 = Message(
                id=str(uuid.uuid4()),
                chat_id="22222222-2222-2222-2222-222222222222",
                sender="assistant",
                content="주요 기술적 고려사항:\n- **실시간 주문 상태 WebSocket 연동**\n- **위치 기반(GPS/Geofencing) 주변 매장 탐색**\n- **결제 게이트웨이(PG) 안전 연동**"
            )
            self._messages.extend([m1, m2, m3, m4])

    async def get_by_chat_id(self, chat_id: str) -> List[Message]:
        filtered = [m for m in self._messages if m.chat_id == chat_id]
        filtered.sort(key=lambda x: x.created_at)
        return filtered

    async def add(self, message: Message) -> Message:
        self._messages.append(message)
        return message

    async def delete_by_chat_id(self, chat_id: str) -> bool:
        self._messages = [m for m in self._messages if m.chat_id != chat_id]
        return True
