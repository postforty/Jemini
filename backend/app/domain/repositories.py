from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import Chat, Message

class IChatRepository(ABC):
    @abstractmethod
    async def get_all(self, user_id: Optional[str] = None) -> List[Chat]:
        pass

    @abstractmethod
    async def get_by_id(self, chat_id: str) -> Optional[Chat]:
        pass

    @abstractmethod
    async def create(
        self,
        title: str = "새 대화",
        model: str = "gemini-3.1-flash-lite",
        user_id: Optional[str] = None
    ) -> Chat:
        pass

    @abstractmethod
    async def update_title(self, chat_id: str, title: str) -> Optional[Chat]:
        pass

    @abstractmethod
    async def delete(self, chat_id: str) -> bool:
        pass

class IMessageRepository(ABC):
    @abstractmethod
    async def get_by_chat_id(self, chat_id: str) -> List[Message]:
        pass

    @abstractmethod
    async def add(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def delete_by_chat_id(self, chat_id: str) -> bool:
        pass
