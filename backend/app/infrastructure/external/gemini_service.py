import asyncio
from typing import AsyncGenerator
from app.domain.services import ILLMService

class SimulatedGeminiService(ILLMService):
    def __init__(self, chunk_size: int = 3, delay: float = 0.02):
        self.chunk_size = chunk_size
        self.delay = delay

    async def generate_stream(self, prompt: str, model: str) -> AsyncGenerator[str, None]:
        model_name = model or "gemini-3.1-flash-lite"
        prompt_lower = prompt.lower()

        if "안녕" in prompt_lower or "hello" in prompt_lower:
            answer_text = f"안녕하세요! 저는 **{model_name}** 모델로 동작하는 AI 어시스턴트입니다. 어떤 도움이 필요하신가요?"
        elif "커피" in prompt_lower:
            answer_text = f"""커피 앱 관련해서 비판적이고 체계적인 분석을 해드릴게요!\n\n### 1. 주요 타겟 및 사용자 니즈\n- **빠른 픽업(오더앤페이)**: 바쁜 직장인 대상의 대기시간 단축가치\n- **맞춤형 스페셜티 추천**: 개개인의 원두 취향 분석\n\n```python\n# 간단한 커피 주문 추천 알고리즘 예시\ndef recommend_coffee(user_preference):\n    if user_preference == 'acidic':\n        return '에티오피아 예가체프 드립'\n    return '고소한 브라질 세라도 아메리카노'\n```\n\n추가로 알고 싶으신 세부 기획 요소가 있으신가요?"""
        elif "코드" in prompt_lower or "code" in prompt_lower or "파이썬" in prompt_lower or "javascript" in prompt_lower:
            answer_text = f"""요청하신 코드 예시를 **{model_name}** 성능에 맞춰 작성해 드립니다:\n\n```javascript\n// Jemini Chat Assistant Controller\nasync function handleSendMessage(prompt, model) {{\n  const response = await fetch('/api/generate', {{\n    method: 'POST',\n    headers: {{ 'Content-Type': 'application/json' }},\n    body: JSON.stringify({{ prompt, model }})\n  }});\n  return response;\n}}\n```\n\n필요한 추가 기능이나 리팩토링이 필요하시면 말씀해주세요!"""
        else:
            answer_text = f"""질문해주신 **"{prompt}"**에 대한 답변입니다.\n\n**{model_name}** 모델이 분석한 결과, 요청하신 항목을 성공적으로 처리할 수 있습니다. 추가적인 세부사항이 필요하시다면 언제든 질문해주세요!"""

        for i in range(0, len(answer_text), self.chunk_size):
            chunk = answer_text[i:i+self.chunk_size]
            yield chunk
            if self.delay > 0:
                await asyncio.sleep(self.delay)
