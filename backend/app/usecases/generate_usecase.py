import json
import asyncio
from typing import Optional, AsyncGenerator
from app.domain.entities import Message
from app.domain.repositories import IChatRepository, IMessageRepository
from app.domain.services import ILLMService

class GenerateResponseUseCase:
    def __init__(
        self,
        chat_repo: IChatRepository,
        message_repo: IMessageRepository,
        llm_service: ILLMService
    ):
        self.chat_repo = chat_repo
        self.message_repo = message_repo
        self.llm_service = llm_service

    async def execute(
        self,
        prompt: str,
        chat_id: Optional[str] = None,
        model: str = "gemini-3.1-flash-lite",
        image_url: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        # 1. Validate or Create Chat
        existing_chat = await self.chat_repo.get_by_id(chat_id) if chat_id else None
        if not existing_chat:
            title = prompt[:25] + ("..." if len(prompt) > 25 else "")
            new_chat = await self.chat_repo.create(title=title, model=model)
            chat_id = new_chat.id
        else:
            chat_id = existing_chat.id

        # 2. Save User Message
        user_msg = Message(
            chat_id=chat_id,
            sender="user",
            content=prompt,
            image_url=image_url
        )
        await self.message_repo.add(user_msg)

        # 3. Yield initial chat_id SSE event
        yield f"data: {json.dumps({'type': 'chat_id', 'chat_id': chat_id})}\n\n"
        await asyncio.sleep(0.01)

        # 4. Stream LLM chunks
        full_response = ""
        async for chunk in self.llm_service.generate_stream(prompt, model):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"

        # 5. Save Assistant Message
        assistant_msg = Message(
            chat_id=chat_id,
            sender="assistant",
            content=full_response
        )
        await self.message_repo.add(assistant_msg)

        # 6. Auto update chat title if default
        chat = await self.chat_repo.get_by_id(chat_id)
        if chat and chat.title == "새 대화":
            new_title = prompt[:20] + ("..." if len(prompt) > 20 else "")
            await self.chat_repo.update_title(chat_id, new_title)

        # 7. Yield done SSE event
        yield f"data: {json.dumps({'type': 'done', 'full_text': full_response})}\n\n"
