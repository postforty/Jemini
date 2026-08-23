from typing import List, Optional, Any
from datetime import datetime
from app.domain.entities import Chat, Message
from app.domain.repositories import IChatRepository, IMessageRepository

class SupabaseChatRepository(IChatRepository):
    def __init__(self, client: Any):
        self.client = client

    async def get_all(self) -> List[Chat]:
        res = self.client.table("chats").select("*").order("created_at", desc=True).execute()
        return [
            Chat(
                id=item["id"],
                title=item.get("title", "새 대화"),
                model=item.get("model", "gemini-3.1-flash-lite"),
                created_at=item.get("created_at", datetime.now().isoformat()),
                updated_at=item.get("updated_at", datetime.now().isoformat())
            )
            for item in res.data
        ]

    async def get_by_id(self, chat_id: str) -> Optional[Chat]:
        res = self.client.table("chats").select("*").eq("id", chat_id).execute()
        if res.data:
            item = res.data[0]
            return Chat(
                id=item["id"],
                title=item.get("title", "새 대화"),
                model=item.get("model", "gemini-3.1-flash-lite"),
                created_at=item.get("created_at", datetime.now().isoformat()),
                updated_at=item.get("updated_at", datetime.now().isoformat())
            )
        return None

    async def create(self, title: str = "새 대화", model: str = "gemini-3.1-flash-lite") -> Chat:
        chat = Chat(title=title, model=model)
        chat_data = {
            "id": chat.id,
            "title": chat.title,
            "model": chat.model,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        res = self.client.table("chats").insert(chat_data).execute()
        if res.data:
            item = res.data[0]
            return Chat(
                id=item["id"],
                title=item.get("title", title),
                model=item.get("model", model),
                created_at=item.get("created_at", chat.created_at),
                updated_at=item.get("updated_at", chat.updated_at)
            )
        return chat

    async def update_title(self, chat_id: str, title: str) -> Optional[Chat]:
        now_str = datetime.now().isoformat()
        res = self.client.table("chats").update({"title": title, "updated_at": now_str}).eq("id", chat_id).execute()
        if res.data:
            item = res.data[0]
            return Chat(
                id=item["id"],
                title=item["title"],
                model=item["model"],
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            )
        return None

    async def delete(self, chat_id: str) -> bool:
        existing = await self.get_by_id(chat_id)
        if not existing:
            return False
        self.client.table("chats").delete().eq("id", chat_id).execute()
        return True

class SupabaseMessageRepository(IMessageRepository):
    def __init__(self, client: Any):
        self.client = client

    async def get_by_chat_id(self, chat_id: str) -> List[Message]:
        res = self.client.table("messages").select("*").eq("chat_id", chat_id).order("created_at", desc=False).execute()
        return [
            Message(
                id=item["id"],
                chat_id=item["chat_id"],
                sender=item["sender"],
                content=item["content"],
                image_url=item.get("image_url"),
                created_at=item.get("created_at", datetime.now().isoformat())
            )
            for item in res.data
        ]

    async def add(self, message: Message) -> Message:
        msg_data = {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender": message.sender,
            "content": message.content,
            "image_url": message.image_url,
            "created_at": message.created_at
        }
        res = self.client.table("messages").insert(msg_data).execute()
        if res.data:
            item = res.data[0]
            return Message(
                id=item["id"],
                chat_id=item["chat_id"],
                sender=item["sender"],
                content=item["content"],
                image_url=item.get("image_url"),
                created_at=item.get("created_at", message.created_at)
            )
        return message

    async def delete_by_chat_id(self, chat_id: str) -> bool:
        self.client.table("messages").delete().eq("chat_id", chat_id).execute()
        return True
