import asyncio
import base64
from typing import AsyncGenerator, Optional, List
from app.domain.entities import Message
from app.domain.services import ILLMService

class GeminiLLMService(ILLMService):
    def __init__(self, api_key: str):
        self.api_key = api_key
        from google import genai
        self.client = genai.Client(api_key=api_key)

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        history: Optional[List[Message]] = None,
        image_url: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        from google.genai import types

        model_name = model or "gemini-3.1-flash-lite"
        contents: List[types.Content] = []

        # 1. Build conversation history
        if history:
            for msg in history:
                role = "user" if msg.sender == "user" else "model"
                parts = []
                if msg.content:
                    parts.append(types.Part.from_text(text=msg.content))
                if parts:
                    contents.append(types.Content(role=role, parts=parts))

        # 2. Build current turn user content (with optional image)
        current_parts = []
        if image_url:
            try:
                if "," in image_url:
                    header, base64_data = image_url.split(",", 1)
                    mime_type = "image/png"
                    if "data:" in header and ";base64" in header:
                        mime_type = header.split("data:")[1].split(";base64")[0]
                    image_bytes = base64.b64decode(base64_data)
                    current_parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
            except Exception as img_err:
                print(f"Failed to parse image attachment: {img_err}")

        if prompt:
            current_parts.append(types.Part.from_text(text=prompt))
        elif not current_parts:
            current_parts.append(types.Part.from_text(text=""))

        contents.append(types.Content(role="user", parts=current_parts))

        # 3. Call client.aio.models.generate_content_stream
        system_instruction = (
            "당신은 유용하고 지적인 AI 어시스턴트입니다.\n"
            "사용자의 질문에 성실하고 명확하게 답변하세요.\n"
            "답변 본문 작성이 끝난 후, 반드시 맨 마지막에 사용자가 이어서 질문할 만한 '추천 후속 질문 3개'를 아래와 같이 <suggestions> 태그로 감싼 순수 JSON 배열 형식으로 작성하세요.\n"
            "<suggestions>\n"
            '[\n  "추천 후속 질문 1",\n  "추천 후속 질문 2",\n  "추천 후속 질문 3"\n]\n'
            "</suggestions>"
        )

        response = await self.client.aio.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text


class SimulatedGeminiService(ILLMService):
    def __init__(self, chunk_size: int = 3, delay: float = 0.02):
        self.chunk_size = chunk_size
        self.delay = delay

    async def generate_stream(
        self,
        prompt: str,
        model: str,
        history: Optional[List[Message]] = None,
        image_url: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        model_name = model or "gemini-3.1-flash-lite"
        prompt_lower = prompt.lower()

        if "안녕" in prompt_lower or "hello" in prompt_lower:
            answer_text = (
                f"안녕하세요! 저는 **{model_name}** 모델로 동작하는 AI 어시스턴트입니다. 어떤 도움이 필요하신가요?\n\n"
                "<suggestions>\n"
                '[\n  "어떤 작업을 도와줄 수 있나요?",\n  "Jemini의 주요 기능은 무엇인가요?",\n  "간단한 파이썬 예제 코드를 보여줘"\n]\n'
                "</suggestions>"
            )
        elif "커피" in prompt_lower:
            answer_text = (
                f"커피 앱 관련해서 비판적이고 체계적인 분석을 해드릴게요!\n\n"
                f"### 1. 주요 타겟 및 사용자 니즈\n"
                f"- **빠른 픽업(오더앤페이)**: 바쁜 직장인 대상의 대기시간 단축가치\n"
                f"- **맞춤형 스페셜티 추천**: 개개인의 원두 취향 분석\n\n"
                f"```python\n"
                f"# 간단한 커피 주문 추천 알고리즘 예시\n"
                f"def recommend_coffee(user_preference):\n"
                f"    if user_preference == 'acidic':\n"
                f"        return '에티오피아 예가체프 드립'\n"
                f"    return '고소한 브라질 세라도 아메리카노'\n"
                f"```\n\n"
                f"추가로 알고 싶으신 세부 기획 요소가 있으신가요?\n\n"
                "<suggestions>\n"
                '[\n  "스페셜티 원두 추천 알고리즘을 더 자세히 설명해줘",\n  "오더앤페이 기능 구현 시 고려할 점은 무엇인가요?",\n  "커피 주문 앱의 UI/UX 디자인 팁을 알려줘"\n]\n'
                "</suggestions>"
            )
        elif "코드" in prompt_lower or "code" in prompt_lower or "파이썬" in prompt_lower or "javascript" in prompt_lower:
            answer_text = (
                f"요청하신 코드 예시를 **{model_name}** 성능에 맞춰 작성해 드립니다:\n\n"
                f"```javascript\n"
                f"// Jemini Chat Assistant Controller\n"
                f"async function handleSendMessage(prompt, model) {{\n"
                f"  const response = await fetch('/api/generate', {{\n"
                f"    method: 'POST',\n"
                f"    headers: {{ 'Content-Type': 'application/json' }},\n"
                f"    body: JSON.stringify({{ prompt, model }})\n"
                f"  }});\n"
                f"  return response;\n"
                f"}}\n"
                f"```\n\n"
                f"필요한 추가 기능이나 리팩토링이 필요하시면 말씀해주세요!\n\n"
                "<suggestions>\n"
                '[\n  "에러 핸들링 로직을 추가해줘",\n  "TypeScript로 타입을 정의해줘",\n  "SSE 스트리밍 수신 처리 코드를 작성해줘"\n]\n'
                "</suggestions>"
            )
        else:
            answer_text = (
                f"질문해주신 **\"{prompt}\"**에 대한 답변입니다.\n\n"
                f"**{model_name}** 모델이 분석한 결과, 요청하신 항목을 성공적으로 처리할 수 있습니다. 추가적인 세부사항이 필요하시다면 언제든 질문해주세요!\n\n"
                "<suggestions>\n"
                '[\n  "이에 대해 더 자세히 설명해줘",\n  "관련된 실제 사례나 예시를 들어줘",\n  "다른 대안이나 해결책이 있을까?"\n]\n'
                "</suggestions>"
            )

        for i in range(0, len(answer_text), self.chunk_size):
            chunk = answer_text[i:i+self.chunk_size]
            yield chunk
            if self.delay > 0:
                await asyncio.sleep(self.delay)
