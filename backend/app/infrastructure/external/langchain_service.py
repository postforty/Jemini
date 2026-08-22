import asyncio
import os
from typing import AsyncGenerator, Optional, List, Any, Union
from app.domain.entities import Message
from app.domain.services import ILLMService

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_core.language_models.chat_models import BaseChatModel

DEFAULT_SYSTEM_INSTRUCTION = (
    "당신은 유용하고 지적인 AI 어시스턴트입니다.\n"
    "사용자의 질문에 성실하고 명확하게 답변하세요.\n"
    "답변 본문 작성이 끝난 후, 반드시 맨 마지막에 사용자가 이어서 질문할 만한 '추천 후속 질문 3개'를 아래와 같이 <suggestions> 태그로 감싼 순수 JSON 배열 형식으로 작성하세요.\n"
    "<suggestions>\n"
    '[\n  "추천 후속 질문 1",\n  "추천 후속 질문 2",\n  "추천 후속 질문 3"\n]\n'
    "</suggestions>"
)

class LangChainMultiVendorService(ILLMService):
    """
    Multi-Vendor LLM Service adapter implemented via LangChain.
    Supports Google Gemini, OpenAI, Anthropic, and Ollama models.
    """

    def __init__(
        self,
        google_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION,
    ):
        self.google_api_key = google_api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.system_instruction = system_instruction
        self._model_cache: dict[str, BaseChatModel] = {}

    def _create_chat_model(self, model: str) -> BaseChatModel:
        clean_model = model.strip()

        # 1. Google Gemini (e.g., "gemini-3.1-flash-lite", "google:gemini-3.5-flash")
        if clean_model.startswith("gemini-") or clean_model.startswith("google:"):
            actual_model = clean_model.removeprefix("google:")
            if not self.google_api_key or "your-gemini-api-key" in self.google_api_key:
                raise ValueError(
                    f"Google Gemini API Key가 설정되지 않았습니다. ({clean_model})"
                )
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=actual_model,
                google_api_key=self.google_api_key,
                temperature=0.7,
            )

        # 2. OpenAI (e.g., "gpt-4o", "gpt-4o-mini", "o1-mini", "openai:gpt-4o")
        if (
            clean_model.startswith("gpt-")
            or clean_model.startswith("o1-")
            or clean_model.startswith("o3-")
            or clean_model.startswith("openai:")
        ):
            actual_model = clean_model.removeprefix("openai:")
            if not self.openai_api_key or "your-openai-api-key" in self.openai_api_key:
                raise ValueError(
                    f"OpenAI API Key가 설정되지 않았습니다. ({clean_model})"
                )
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=actual_model,
                api_key=self.openai_api_key,
                temperature=0.7,
                streaming=True,
            )

        # 3. Anthropic (e.g., "claude-3-5-sonnet-latest", "anthropic:claude-3-5-haiku")
        if clean_model.startswith("claude-") or clean_model.startswith("anthropic:"):
            actual_model = clean_model.removeprefix("anthropic:")
            if not self.anthropic_api_key or "your-anthropic-api-key" in self.anthropic_api_key:
                raise ValueError(
                    f"Anthropic API Key가 설정되지 않았습니다. ({clean_model})"
                )
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=actual_model,
                api_key=self.anthropic_api_key,
                temperature=0.7,
                streaming=True,
            )

        # 4. Ollama (e.g., "ollama:llama3.2", "ollama:deepseek-r1")
        if clean_model.startswith("ollama:"):
            actual_model = clean_model.removeprefix("ollama:")
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=actual_model,
                base_url=self.ollama_base_url,
                temperature=0.7,
            )

        # Default fallback to Google if starts with default names, else try OpenAI
        if self.google_api_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=clean_model,
                google_api_key=self.google_api_key,
                temperature=0.7,
            )
        elif self.openai_api_key:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=clean_model,
                api_key=self.openai_api_key,
                temperature=0.7,
                streaming=True,
            )

        raise ValueError(f"지원되지 않거나 API Key가 없는 모델입니다: {clean_model}")

    def _get_model(self, model: str) -> BaseChatModel:
        if model not in self._model_cache:
            self._model_cache[model] = self._create_chat_model(model)
        return self._model_cache[model]

    def _build_messages(
        self,
        prompt: str,
        history: Optional[List[Message]] = None,
        image_url: Optional[str] = None,
    ) -> List[BaseMessage]:
        messages: List[BaseMessage] = [
            SystemMessage(content=self.system_instruction)
        ]

        # 1. Conversation history
        if history:
            for msg in history:
                if msg.sender == "user":
                    messages.append(HumanMessage(content=msg.content or ""))
                elif msg.sender == "assistant":
                    messages.append(AIMessage(content=msg.content or ""))

        # 2. Current turn message (with optional image)
        if image_url:
            content_blocks: List[Union[dict, str]] = []
            if prompt:
                content_blocks.append({"type": "text", "text": prompt})
            content_blocks.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
            messages.append(HumanMessage(content=content_blocks))
        else:
            messages.append(HumanMessage(content=prompt or ""))

        return messages

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        history: Optional[List[Message]] = None,
        image_url: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        model_name = model or "gemini-3.1-flash-lite"

        try:
            chat_model = self._get_model(model_name)
            messages = self._build_messages(prompt, history, image_url)

            async for chunk in chat_model.astream(messages):
                if chunk.content:
                    if isinstance(chunk.content, str):
                        yield chunk.content
                    elif isinstance(chunk.content, list):
                        for part in chunk.content:
                            if isinstance(part, str):
                                yield part
                            elif isinstance(part, dict) and "text" in part:
                                yield part["text"]
        except Exception as e:
            error_message = (
                f"[오류 발생] 모델 '{model_name}' 호출 중 문제가 발생했습니다: {str(e)}\n\n"
                "<suggestions>\n"
                '[\n  "다른 모델을 선택해볼까요?",\n  "API Key 설정을 확인하는 방법은?",\n  "다시 시도해줘"\n]\n'
                "</suggestions>"
            )
            yield error_message
