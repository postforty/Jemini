from typing import List, Optional
from app.domain.entities import Chat, Message
from app.domain.repositories import IChatRepository, IMessageRepository

class ListChatsUseCase:
    def __init__(self, chat_repo: IChatRepository):
        self.chat_repo = chat_repo

    async def execute(self, user_id: Optional[str] = None) -> List[Chat]:
        return await self.chat_repo.get_all(user_id=user_id)

class CreateChatUseCase:
    def __init__(self, chat_repo: IChatRepository):
        self.chat_repo = chat_repo

    async def execute(
        self,
        title: Optional[str] = None,
        model: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Chat:
        return await self.chat_repo.create(
            title=title or "새 대화",
            model=model or "gemini-3.1-flash-lite",
            user_id=user_id
        )

class DeleteChatUseCase:
    def __init__(self, chat_repo: IChatRepository, message_repo: IMessageRepository):
        self.chat_repo = chat_repo
        self.message_repo = message_repo

    async def execute(self, chat_id: str, user_id: Optional[str] = None) -> bool:
        existing = await self.chat_repo.get_by_id(chat_id)
        if not existing:
            return False
        if user_id and existing.user_id and existing.user_id != user_id:
            return False
        deleted = await self.chat_repo.delete(chat_id)
        if deleted:
            await self.message_repo.delete_by_chat_id(chat_id)
        return deleted

class GetMessagesUseCase:
    def __init__(self, message_repo: IMessageRepository):
        self.message_repo = message_repo

    async def execute(self, chat_id: str) -> List[Message]:
        return await self.message_repo.get_by_chat_id(chat_id)
