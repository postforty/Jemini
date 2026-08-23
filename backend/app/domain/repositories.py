from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import Chat, Message, Payment, Subscription

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

class IPaymentRepository(ABC):
    @abstractmethod
    async def add(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Payment]:
        pass

class ISubscriptionRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def upsert(self, subscription: Subscription) -> Subscription:
        pass

