from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, List
from app.domain.entities import Message

class ILLMService(ABC):
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        model: str,
        history: Optional[List[Message]] = None,
        image_url: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generates a text stream chunk by chunk for the given prompt, model, history, and image."""
        pass

class IPaymentGatewayService(ABC):
    @abstractmethod
    async def confirm_payment(
        self,
        payment_key: str,
        order_id: str,
        amount: float
    ) -> dict:
        """Confirms payment with payment gateway."""
        pass


