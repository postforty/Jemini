import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.domain.entities import Message
from app.infrastructure.external.langchain_service import LangChainMultiVendorService
from langchain_core.messages import AIMessageChunk, HumanMessage, AIMessage, SystemMessage

@pytest.fixture
def service():
    return LangChainMultiVendorService(
        google_api_key="test-google-key",
        openai_api_key="test-openai-key",
        anthropic_api_key="test-anthropic-key",
        ollama_base_url="http://localhost:11434",
    )

def test_model_resolution_google(service):
    model = service._get_model("gemini-3.1-flash-lite")
    assert model.__class__.__name__ == "ChatGoogleGenerativeAI"
    assert model.model == "gemini-3.1-flash-lite"

def test_model_resolution_openai(service):
    model = service._get_model("gpt-4o-mini")
    assert model.__class__.__name__ == "ChatOpenAI"
    assert model.model_name == "gpt-4o-mini"

def test_model_resolution_anthropic(service):
    model = service._get_model("claude-3-5-haiku-latest")
    assert model.__class__.__name__ == "ChatAnthropic"
    assert model.model == "claude-3-5-haiku-latest"

def test_model_resolution_ollama(service):
    model = service._get_model("ollama:gemma3:270m")
    assert model.__class__.__name__ == "ChatOllama"
    assert model.model == "gemma3:270m"

    # Direct gemma prefix without ollama:
    direct_model = service._get_model("gemma3:270m")
    assert direct_model.__class__.__name__ == "ChatOllama"
    assert direct_model.model == "gemma3:270m"

def test_build_messages_with_history_and_image(service):
    history = [
        Message(chat_id="c1", sender="user", content="이전 질문"),
        Message(chat_id="c1", sender="assistant", content="이전 답변"),
    ]
    image_url = "data:image/png;base64,abcdef"
    messages = service._build_messages(
        prompt="이미지 분석해줘",
        history=history,
        image_url=image_url,
    )

    assert len(messages) == 4
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert messages[1].content == "이전 질문"
    assert isinstance(messages[2], AIMessage)
    assert messages[2].content == "이전 답변"
    assert isinstance(messages[3], HumanMessage)
    # Multimodal content block
    assert isinstance(messages[3].content, list)
    assert messages[3].content[0] == {"type": "text", "text": "이미지 분석해줘"}
    assert messages[3].content[1] == {"type": "image_url", "image_url": {"url": image_url}}

@pytest.mark.asyncio
async def test_generate_stream_success(service):
    mock_llm = MagicMock()
    async def mock_astream(messages):
        yield AIMessageChunk(content="안녕하세요! ")
        yield AIMessageChunk(content="LangChain Multi-Vendor 응답입니다.")

    mock_llm.astream = mock_astream
    service._model_cache["gpt-4o-mini"] = mock_llm

    chunks = []
    async for chunk in service.generate_stream(prompt="테스트", model="gpt-4o-mini"):
        chunks.append(chunk)

    full_text = "".join(chunks)
    assert full_text == "안녕하세요! LangChain Multi-Vendor 응답입니다."

@pytest.mark.asyncio
async def test_generate_stream_missing_api_key():
    service_no_keys = LangChainMultiVendorService(
        google_api_key="",
        openai_api_key="",
        anthropic_api_key="",
    )

    chunks = []
    async for chunk in service_no_keys.generate_stream(prompt="테스트", model="gpt-4o-mini"):
        chunks.append(chunk)

    full_text = "".join(chunks)
    assert "[오류 발생]" in full_text
    assert "OpenAI API Key가 설정되지 않았습니다" in full_text
    assert "<suggestions>" in full_text
