from abc import ABC, abstractmethod
from typing import AsyncGenerator

class ILLMService(ABC):
    @abstractmethod
    async def generate_stream(self, prompt: str, model: str) -> AsyncGenerator[str, None]:
        """Generates a text stream chunk by chunk for the given prompt and model."""
        pass
