# 추천 후속 질문 버튼 기능 추가 — 코드베이스 분석 보고서

## 1. 현재 아키텍처 요약

```
frontend/  (FSD: Feature-Sliced Design)
  entities/
    message/model/types.ts      → Message 타입 정의
    chat/model/store.ts         → Zustand 글로벌 스토어
  features/send-message/api/   → sendMessageStream (SSE 기반)
  widgets/chat-feed/ui/        → ChatFeed (메시지 렌더링 + 재생성 로직)
  entities/message/ui/         → ChatMessage (단일 메시지 UI)
  shared/api/sseClient.ts      → SSE 스트림 파서 (type: chat_id | chunk | done)

backend/  (Clean Architecture)
  domain/
    entities.py                → Message, Chat 도메인 객체
    services.py                → ILLMService (generate_stream 추상 메서드)
  infrastructure/external/
    gemini_service.py          → GeminiLLMService + SimulatedGeminiService
  usecases/
    generate_usecase.py        → GenerateResponseUseCase (SSE 이벤트 생성)
  presentation/api/v1/
    generate_router.py         → POST /api/generate → StreamingResponse
```

---

## 2. 기능 개요

AI 응답 생성이 완료된 후, 해당 응답 하단에 사용자가 클릭할 수 있는 **추천 후속 질문 버튼**을 3~4개 제공합니다.  
버튼을 클릭하면 해당 텍스트가 사용자 입력처럼 바로 전송됩니다.

---

## 3. 고려해야 할 사항

### 3-A. 추천 질문 생성 전략 선택 (가장 중요한 설계 결정)

두 가지 방식이 있으며, 트레이드오프가 큰 결정입니다.

| 방식 | 장점 | 단점 |
|---|---|---|
| **백엔드에서 별도 LLM 호출** | 품질 높음, 맥락 활용 가능 | 추가 API 비용, 지연 발생 |
| **SSE `done` 이벤트에 함께 포함** | 네트워크 왕복 1회로 해결 | 스트리밍 완료 후에만 전달 가능 |
| **프론트엔드에서 규칙 기반 생성** | 서버 비용 없음, 즉시 처리 | 품질 낮음, 일반적 패턴만 가능 |

> **권장**: `done` 이벤트에 `suggested_questions` 필드를 추가하는 방식. 스트리밍 완료 후 자연스럽게 노출되며, 네트워크 왕복이 추가되지 않음.

---

### 3-B. 백엔드 변경사항

#### `generate_usecase.py` — Step 7 `done` 이벤트 확장

현재 코드:
```python
# 7. Yield done SSE event
yield f"data: {json.dumps({'type': 'done', 'full_text': full_response})}\n\n"
```

변경 필요:
```python
# 7. Generate suggested questions
suggested = await self.llm_service.generate_suggested_questions(
    prompt=prompt,
    response=full_response,
    history=history
)
yield f"data: {json.dumps({'type': 'done', 'full_text': full_response, 'suggested_questions': suggested})}\n\n"
```

#### `domain/services.py` — ILLMService 추상 메서드 추가

```python
@abstractmethod
async def generate_suggested_questions(
    self,
    prompt: str,
    response: str,
    history: Optional[List[Message]] = None
) -> List[str]:
    """Generates 3-4 follow-up question suggestions."""
    pass
```

#### `infrastructure/external/gemini_service.py`

- `GeminiLLMService`: 실제 Gemini API 호출로 질문 생성
- `SimulatedGeminiService`: 하드코딩된 더미 질문 목록 반환

> ⚠️ **주의**: `generate_suggested_questions`는 스트리밍이 끝난 뒤에 호출됩니다.  
> Gemini API를 2번 호출하므로 **추가 비용과 최대 1~2초의 지연**이 발생합니다.  
> 비용 절감을 원한다면, 메인 프롬프트에 "답변 마지막에 JSON으로 추천 질문 포함" 지시를 추가하고 파싱하는 방식도 고려하세요.

---

### 3-C. SSE 프로토콜 & 프론트엔드 API 계약 변경

#### `shared/api/sseClient.ts` — SSEChunk 타입 확장

```typescript
export interface SSEChunk {
  type: 'chat_id' | 'chunk' | 'done';
  text?: string;
  chat_id?: string;
  full_text?: string;
  suggested_questions?: string[];  // ← 추가
}
```

#### `features/send-message/api/sendMessage.ts` — 콜백 추가

```typescript
interface SendMessageParams {
  // ... 기존 필드
  onSuggestedQuestions?: (questions: string[]) => void;  // ← 추가
}

// done 이벤트 처리에서:
if (data.type === 'done' && data.suggested_questions && params.onSuggestedQuestions) {
  params.onSuggestedQuestions(data.suggested_questions);
}
```

---

### 3-D. 상태 관리 (Zustand Store)

추천 질문을 **어느 레벨에서 관리**할지 결정해야 합니다.

#### 옵션 1: `Message` 타입에 포함 (권장)

```typescript
// entities/message/model/types.ts
export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  image_url: string | null;
  suggested_questions?: string[];  // ← 추가
}
```

- **장점**: 채팅 히스토리와 함께 localStorage에 자동 영속화, 과거 메시지 재방문 시에도 버튼 유지
- **단점**: `Message` 타입이 약간 비대해짐

#### 옵션 2: ChatFeed의 로컬 상태 `useState`

- **장점**: 가장 간단한 구현
- **단점**: 페이지 새로고침 시 소멸, 다른 채팅 이동 후 복귀 시 사라짐

> **권장**: 옵션 1 (Message 타입 확장). 사용자 경험상 이전 AI 응답의 추천 질문도 다시 볼 수 있어야 자연스럽습니다.

---

### 3-E. UI 컴포넌트 변경

#### `entities/message/ui/ChatMessage.tsx` — 추천 질문 렌더링

```tsx
interface ChatMessageProps {
  message: Message;
  onRegenerate?: (() => void) | null;
  onFollowUpQuestion?: (question: string) => void;  // ← 추가
}

// AI 응답 하단에 추가:
{message.suggested_questions && message.suggested_questions.length > 0 && (
  <div className={styles.suggestedQuestions}>
    {message.suggested_questions.map((q, i) => (
      <button
        key={i}
        className={styles.suggestedBtn}
        onClick={() => onFollowUpQuestion?.(q)}
      >
        {q}
      </button>
    ))}
  </div>
)}
```

#### `ChatMessage.module.css` — 버튼 스타일 추가

```css
.suggestedQuestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.suggestedBtn {
  background: transparent;
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 14px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background-color 0.15s, border-color 0.15s;
}

.suggestedBtn:hover {
  background-color: #f1f3f4;
  border-color: var(--text-secondary);
}
```

#### `widgets/chat-feed/ui/ChatFeed.tsx` — prop 전달 및 클릭 핸들러

```tsx
const handleFollowUpQuestion = (question: string) => {
  // sendMessage feature의 handleSend를 직접 호출하거나,
  // 전역 이벤트/ref를 통해 MessageInput에 텍스트 주입
};
```

> ⚠️ **FSD 레이어 경계 주의**: `ChatFeed`(widget)에서 `send-message`(feature)를 호출하는 것은 FSD 규칙상 허용됩니다.  
> 그러나 `ChatMessage`(entity)에서 직접 메시지 전송 로직을 호출하는 것은 **FSD 위반**입니다.  
> 콜백 prop(`onFollowUpQuestion`)을 통해 위젯 레이어로 제어권을 위임해야 합니다.

---

### 3-F. 재생성(Regenerate) 시 처리

현재 `ChatFeed.tsx`의 `handleRegenerate`는 마지막 assistant 메시지를 삭제하고 재생성합니다.  
재생성 완료 후에도 새 추천 질문이 업데이트되어야 합니다.  
`sendMessageStream`의 `onSuggestedQuestions` 콜백을 `handleRegenerate` 내부에서도 동일하게 연결해야 합니다.

---

### 3-G. UX 타이밍 고려사항

| 타이밍 | 설명 | 권장 여부 |
|---|---|---|
| 스트리밍 중 노출 | 응답이 아직 타이핑 중에 버튼 표시 | ❌ 어색함 |
| `done` 이벤트 수신 후 | 스트리밍 완료 즉시 노출 | ✅ 자연스러움 |
| 페이드인 애니메이션 | 버튼 등장 시 `opacity: 0 → 1` 트랜지션 | ✅ 권장 |
| 최신 메시지에만 표시 | 이전 메시지 버튼은 숨기거나 dim 처리 | 선택사항 |

---

### 3-H. 성능 & 비용 관리

- **Gemini API 추가 호출 비용**: `generate_suggested_questions`는 짧은 프롬프트지만 별도 API 호출 발생
- **캐싱**: 동일 (prompt, response) 쌍에 대한 질문은 캐싱 가능 (단기적으론 불필요)
- **실패 처리**: 질문 생성에 실패해도 **본 답변에는 영향 없어야 함** — try/except로 격리, 실패 시 빈 배열 반환

```python
try:
    suggested = await self.llm_service.generate_suggested_questions(...)
except Exception:
    suggested = []  # 실패해도 done 이벤트는 정상 전송
```

---

### 3-I. 테스트 고려사항

| 레이어 | 테스트 항목 |
|---|---|
| Backend unit | `generate_suggested_questions`의 Mock LLM 반환값 파싱 |
| Backend integration | `done` SSE 이벤트에 `suggested_questions` 포함 여부 |
| Frontend unit | `SSEChunk` 타입 확장 후 파싱 정상 동작 |
| Frontend unit | `ChatMessage`에서 버튼 렌더링 및 클릭 핸들러 |
| E2E | 버튼 클릭 → 메시지 전송 전체 플로우 |

---

## 4. 변경이 필요한 파일 목록

### 백엔드

| 파일 | 변경 유형 |
|---|---|
| [`domain/services.py`](file:///d:/wsh/vibe-workspace/ch10/jemini/backend/app/domain/services.py) | `generate_suggested_questions` 추상 메서드 추가 |
| [`infrastructure/external/gemini_service.py`](file:///d:/wsh/vibe-workspace/ch10/jemini/backend/app/infrastructure/external/gemini_service.py) | `GeminiLLMService` & `SimulatedGeminiService` 구현 추가 |
| [`usecases/generate_usecase.py`](file:///d:/wsh/vibe-workspace/ch10/jemini/backend/app/usecases/generate_usecase.py) | Step 7 `done` 이벤트에 `suggested_questions` 포함 |

### 프론트엔드

| 파일 | 변경 유형 |
|---|---|
| [`entities/message/model/types.ts`](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/src/entities/message/model/types.ts) | `Message` 타입에 `suggested_questions?: string[]` 추가 |
| [`shared/api/sseClient.ts`](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/src/shared/api/sseClient.ts) | `SSEChunk` 타입 확장 |
| [`features/send-message/api/sendMessage.ts`](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/src/features/send-message/api/sendMessage.ts) | `onSuggestedQuestions` 콜백 처리 추가 |
| [`entities/message/ui/ChatMessage.tsx`](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/src/entities/message/ui/ChatMessage.tsx) | 추천 질문 버튼 렌더링 추가 |
| [`entities/message/ui/ChatMessage.module.css`](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/src/entities/message/ui/ChatMessage.module.css) | `.suggestedQuestions`, `.suggestedBtn` 스타일 추가 |
| [`widgets/chat-feed/ui/ChatFeed.tsx`](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/src/widgets/chat-feed/ui/ChatFeed.tsx) | `onSuggestedQuestions` 연결, `handleFollowUpQuestion` 구현 |

---

## 5. 핵심 리스크 요약

> [!WARNING]
> **추가 LLM 비용**: 매 응답마다 Gemini API를 한 번 더 호출합니다. 프로덕션에서는 호출 비용이 누적됩니다.

> [!IMPORTANT]
> **FSD 레이어 경계**: `ChatMessage`(entity)에서 메시지 전송을 직접 호출하면 FSD 위반. 반드시 콜백 prop 패턴을 사용하세요.

> [!NOTE]
> **기능 선택성**: `suggested_questions`가 없는 메시지(이전 메시지, 생성 실패)에도 UI가 깨지지 않도록 옵셔널(`?`) 타입으로 처리해야 합니다.
