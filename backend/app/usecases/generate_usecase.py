import json
import asyncio
import re
from typing import Optional, AsyncGenerator, List
from app.domain.entities import Message
from app.domain.repositories import IChatRepository, IMessageRepository
from app.domain.services import ILLMService

def _extract_questions_from_json(json_str: str) -> List[str]:
    clean = json_str.strip()
    if not clean:
        return []
    try:
        data = json.loads(clean)
        if isinstance(data, list):
            return [str(q).strip() for q in data if str(q).strip()]
        if isinstance(data, dict) and "questions" in data and isinstance(data["questions"], list):
            return [str(q).strip() for q in data["questions"] if str(q).strip()]
    except Exception:
        pass

    # Regex fallback for extracting quoted strings
    matches = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', clean)
    return [m.replace('\\"', '"').strip() for m in matches if len(m.strip()) > 3]

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
            history = []
        else:
            chat_id = existing_chat.id
            history = await self.message_repo.get_by_chat_id(chat_id)

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

        # 4. Stream LLM chunks with in-band suggestions extraction
        TAG_START = "<suggestions>"
        TAG_END = "</suggestions>"

        clean_text_accumulated = ""
        buffer = ""
        found_tag = False
        json_buffer = ""

        async for chunk in self.llm_service.generate_stream(
            prompt=prompt,
            model=model,
            history=history,
            image_url=image_url
        ):
            if found_tag:
                json_buffer += chunk
            else:
                buffer += chunk
                if TAG_START in buffer:
                    found_tag = True
                    clean_part, suggestions_part = buffer.split(TAG_START, 1)
                    if clean_part:
                        clean_text_accumulated += clean_part
                        yield f"data: {json.dumps({'type': 'chunk', 'text': clean_part})}\n\n"
                    json_buffer += suggestions_part
                    buffer = ""
                else:
                    # Hold potential prefix of TAG_START to prevent token boundary leaks
                    hold_len = 0
                    for l in range(min(len(buffer), len(TAG_START)), 0, -1):
                        if TAG_START.startswith(buffer[-l:]):
                            hold_len = l
                            break

                    if hold_len > 0:
                        safe_text = buffer[:-hold_len]
                        buffer = buffer[-hold_len:]
                    else:
                        safe_text = buffer
                        buffer = ""

                    if safe_text:
                        clean_text_accumulated += safe_text
                        yield f"data: {json.dumps({'type': 'chunk', 'text': safe_text})}\n\n"

        # If stream finished without finding TAG_START, flush remaining buffer
        if not found_tag and buffer:
            clean_text_accumulated += buffer
            yield f"data: {json.dumps({'type': 'chunk', 'text': buffer})}\n\n"

        # 5. Extract suggested questions if tag was present
        suggested_questions = []
        if found_tag or json_buffer:
            raw_json = json_buffer.replace(TAG_END, "").strip()
            suggested_questions = _extract_questions_from_json(raw_json)

        # 6. Save Assistant Message (clean text only)
        final_clean_text = clean_text_accumulated.strip()
        assistant_msg = Message(
            chat_id=chat_id,
            sender="assistant",
            content=final_clean_text
        )
        await self.message_repo.add(assistant_msg)

        # 7. Auto update chat title if default
        chat = await self.chat_repo.get_by_id(chat_id)
        if chat and chat.title == "새 대화":
            new_title = prompt[:20] + ("..." if len(prompt) > 20 else "")
            await self.chat_repo.update_title(chat_id, new_title)

        # 8. Yield suggested_questions SSE event if any
        if suggested_questions:
            yield f"data: {json.dumps({'type': 'suggested_questions', 'questions': suggested_questions})}\n\n"

        # 9. Yield done SSE event
        yield f"data: {json.dumps({'type': 'done', 'full_text': final_clean_text})}\n\n"
