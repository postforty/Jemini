from typing import List, Optional, Any
from datetime import datetime
from app.domain.entities import Chat, Message, Payment, Subscription
from app.infrastructure.security.cipher import AES256GCMCipher
from app.domain.repositories import (
    IChatRepository,
    IMessageRepository,
    IPaymentRepository,
    ISubscriptionRepository
)

class SupabaseChatRepository(IChatRepository):
    def __init__(self, client: Any, cipher: AES256GCMCipher):
        self.client = client
        self.cipher = cipher

    async def get_all(self, user_id: Optional[str] = None) -> List[Chat]:
        query = self.client.table("chats").select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        else:
            query = query.is_("user_id", "null")
        res = query.order("created_at", desc=True).execute()
        return [
            Chat(
                id=item["id"],
                title=self.cipher.decrypt(item.get("title")) or "새 대화",
                model=item.get("model", "gemini-3.1-flash-lite"),
                user_id=item.get("user_id"),
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
                title=self.cipher.decrypt(item.get("title")) or "새 대화",
                model=item.get("model", "gemini-3.1-flash-lite"),
                user_id=item.get("user_id"),
                created_at=item.get("created_at", datetime.now().isoformat()),
                updated_at=item.get("updated_at", datetime.now().isoformat())
            )
        return None

    async def create(
        self,
        title: str = "새 대화",
        model: str = "gemini-3.1-flash-lite",
        user_id: Optional[str] = None
    ) -> Chat:
        chat = Chat(title=title, model=model, user_id=user_id)
        chat_data = {
            "id": chat.id,
            "title": self.cipher.encrypt(chat.title),
            "model": chat.model,
            "user_id": user_id,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        res = self.client.table("chats").insert(chat_data).execute()
        if res.data:
            item = res.data[0]
            return Chat(
                id=item["id"],
                title=chat.title,
                model=item.get("model", model),
                user_id=item.get("user_id", user_id),
                created_at=item.get("created_at", chat.created_at),
                updated_at=item.get("updated_at", chat.updated_at)
            )
        return chat

    async def update_title(self, chat_id: str, title: str) -> Optional[Chat]:
        now_str = datetime.now().isoformat()
        res = self.client.table("chats").update({"title": self.cipher.encrypt(title), "updated_at": now_str}).eq("id", chat_id).execute()
        if res.data:
            item = res.data[0]
            return Chat(
                id=item["id"],
                title=title,
                model=item["model"],
                user_id=item.get("user_id"),
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
    def __init__(self, client: Any, cipher: AES256GCMCipher):
        self.client = client
        self.cipher = cipher

    async def get_by_chat_id(self, chat_id: str) -> List[Message]:
        res = self.client.table("messages").select("*").eq("chat_id", chat_id).order("created_at", desc=False).execute()
        return [
            Message(
                id=item["id"],
                chat_id=item["chat_id"],
                sender=item["sender"],
                content=self.cipher.decrypt(item["content"]) or "",
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
            "content": self.cipher.encrypt(message.content),
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
                content=message.content,
                image_url=item.get("image_url"),
                created_at=item.get("created_at", message.created_at)
            )
        return message

    async def delete_by_chat_id(self, chat_id: str) -> bool:
        self.client.table("messages").delete().eq("chat_id", chat_id).execute()
        return True

class SupabasePaymentRepository(IPaymentRepository):
    def __init__(self, client: Any):
        self.client = client

    async def add(self, payment: Payment) -> Payment:
        data = {
            "id": payment.id,
            "payment_key": payment.payment_key,
            "order_id": payment.order_id,
            "order_name": payment.order_name,
            "amount": payment.amount,
            "method": payment.method,
            "status": payment.status,
            "user_id": payment.user_id,
            "created_at": payment.created_at,
        }
        res = self.client.table("payments").insert(data).execute()
        if res.data:
            item = res.data[0]
            return Payment(
                id=item["id"],
                payment_key=item["payment_key"],
                order_id=item["order_id"],
                order_name=item["order_name"],
                amount=float(item["amount"]),
                method=item.get("method"),
                status=item["status"],
                user_id=item.get("user_id"),
                created_at=item.get("created_at", payment.created_at),
            )
        return payment

    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        res = self.client.table("payments").select("*").eq("order_id", order_id).execute()
        if res.data:
            item = res.data[0]
            return Payment(
                id=item["id"],
                payment_key=item["payment_key"],
                order_id=item["order_id"],
                order_name=item["order_name"],
                amount=float(item["amount"]),
                method=item.get("method"),
                status=item["status"],
                user_id=item.get("user_id"),
                created_at=item.get("created_at"),
            )
        return None

    async def get_by_user_id(self, user_id: str) -> List[Payment]:
        res = self.client.table("payments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return [
            Payment(
                id=item["id"],
                payment_key=item["payment_key"],
                order_id=item["order_id"],
                order_name=item["order_name"],
                amount=float(item["amount"]),
                method=item.get("method"),
                status=item["status"],
                user_id=item.get("user_id"),
                created_at=item.get("created_at"),
            )
            for item in res.data
        ]

class SupabaseSubscriptionRepository(ISubscriptionRepository):
    def __init__(self, client: Any):
        self.client = client

    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        res = self.client.table("user_subscriptions").select("*").eq("user_id", user_id).execute()
        if res.data:
            item = res.data[0]
            return Subscription(
                user_id=item["user_id"],
                plan_type=item.get("plan_type", "pro"),
                status=item.get("status", "active"),
                payment_id=item.get("payment_id"),
                current_period_end=item.get("current_period_end"),
                created_at=item.get("created_at", datetime.now().isoformat()),
                updated_at=item.get("updated_at", datetime.now().isoformat()),
            )
        return None

    async def upsert(self, subscription: Subscription) -> Subscription:
        data = {
            "user_id": subscription.user_id,
            "plan_type": subscription.plan_type,
            "status": subscription.status,
            "payment_id": subscription.payment_id,
            "current_period_end": subscription.current_period_end,
            "created_at": subscription.created_at,
            "updated_at": subscription.updated_at,
        }
        res = self.client.table("user_subscriptions").upsert(data).execute()
        if res.data:
            item = res.data[0]
            return Subscription(
                user_id=item["user_id"],
                plan_type=item.get("plan_type", subscription.plan_type),
                status=item.get("status", subscription.status),
                payment_id=item.get("payment_id", subscription.payment_id),
                current_period_end=item.get("current_period_end", subscription.current_period_end),
                created_at=item.get("created_at", subscription.created_at),
                updated_at=item.get("updated_at", subscription.updated_at),
            )
        return subscription

