import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.domain.entities import Message
from app.infrastructure.external.gemini_service import SimulatedGeminiService, GeminiLLMService

@pytest.mark.asyncio
async def test_simulated_gemini_service_streaming():
    service = SimulatedGeminiService(chunk_size=5, delay=0.0)
    chunks = []
    async for chunk in service.generate_stream(prompt="안녕하세요", model="gemini-3.1-flash-lite"):
        chunks.append(chunk)

    full_text = "".join(chunks)
    assert len(chunks) > 1
    assert "안녕하세요" in full_text
    assert "gemini-3.1-flash-lite" in full_text

@pytest.mark.asyncio
async def test_simulated_gemini_service_with_history():
    service = SimulatedGeminiService(chunk_size=5, delay=0.0)
    history = [
        Message(chat_id="c1", sender="user", content="이전 질문"),
        Message(chat_id="c1", sender="assistant", content="이전 답변")
    ]
    chunks = []
    async for chunk in service.generate_stream(prompt="커피 추천해줘", model="gemini-3.5-flash", history=history):
        chunks.append(chunk)

    full_text = "".join(chunks)
    assert "커피" in full_text

@pytest.mark.asyncio
async def test_gemini_llm_service_streaming():
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "Gemini "
    mock_chunk2 = MagicMock()
    mock_chunk2.text = "3.1 Flash Response"

    async def async_chunk_generator():
        for ch in [mock_chunk1, mock_chunk2]:
            yield ch

    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.aio.models.generate_content_stream = AsyncMock(return_value=async_chunk_generator())

        service = GeminiLLMService(api_key="test_api_key")
        history = [Message(chat_id="c1", sender="user", content="Hello")]
        
        chunks = []
        async for chunk in service.generate_stream(
            prompt="Tell me about AI",
            model="gemini-3.1-flash-lite",
            history=history,
            image_url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        ):
            chunks.append(chunk)

        assert "".join(chunks) == "Gemini 3.1 Flash Response"
        mock_client.aio.models.generate_content_stream.assert_called_once()
