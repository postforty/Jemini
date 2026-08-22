# Jemini Chatbot Backend

FastAPI 기반의 Jemini Chatbot 백엔드로, **Clean Architecture** 계층형 패턴과 **TDD (pytest)** 기반 테스트 슈트가 적용된 프로젝트입니다.
패키지 및 가상환경 관리자로 [uv](https://github.com/astral-sh/uv)를 사용합니다.

> 🤖 **AI 에이전트 개발 지침 및 아키텍처 제약사항**은 [backend/AGENTS.md](AGENTS.md)를 참조하십시오.

---

## 🏗️ 아키텍처 구조 (Clean Architecture)

```text
backend/
├── app/
│   ├── domain/                  # [Domain 계층] 순수 비즈니스 엔티티 및 추상 인터페이스
│   │   ├── entities.py          # Chat, Message
│   │   ├── repositories.py      # IChatRepository, IMessageRepository (ABC)
│   │   └── services.py          # ILLMService (인터페이스)
│   │
│   ├── usecases/                # [Application Use Case 계층] 비즈니스 흐름 제어
│   │   ├── chat_usecases.py      # List, Create, Delete, GetMessages UseCase
│   │   └── generate_usecase.py   # GenerateResponse UseCase (LLM 스트리밍 및 DB 저장)
│   │
│   ├── infrastructure/          # [Infrastructure 계층] DB 및 외부 서비스 구현체
│   │   ├── persistence/         # InMemoryRepository, SupabaseRepository
│   │   └── external/            # LangChainMultiVendorService, GeminiLLMService, SimulatedGeminiService
│   │
│   └── presentation/            # [Presentation 계층] FastAPI 라우터 및 DTO
│       ├── api/v1/              # chats_router, generate_router
│       ├── dependencies.py      # FastAPI 의존성 주입 Container
│       └── schemas.py           # Request / Response Pydantic DTOs
│
├── tests/                       # [TDD 테스트 슈트]
│   ├── unit/                    # Domain, UseCase 및 LangChain Service 단위 테스트
│   ├── integration/             # Repository CRUD 통합 테스트
│   └── e2e/                     # FastAPI TestClient API 엔드포인트 테스트
│
├── main.py                      # FastAPI App 엔트리포인트
└── pyproject.toml               # 의존성 및 프로젝트 메타데이터
```

---

## 🚀 빠른 시작 가이드 (uv)

### 1. 패키지 설치 및 가상환경 동기화
`pyproject.toml`에 명시된 가상환경과 의존성을 동기화합니다.
```bash
uv sync
```

### 2. 개발 서버 실행
`uv run`을 통해 별도의 가상환경 활성화(activate) 과정 없이 개발 서버를 즉시 실행합니다.
```bash
uv run uvicorn main:app --reload --port 8000
```
- **API 서버**: `http://localhost:8000`
- **API 대화형 문서 (Swagger UI)**: `http://localhost:8000/docs`
- **대체 문서 (ReDoc)**: `http://localhost:8000/redoc`

---

## 🧪 테스트 실행 가이드 (TDD)

`pytest` 및 `pytest-asyncio`를 활용하여 단위 테스트, 통합 테스트, E2E 테스트를 수행합니다.

### 전체 테스트 실행
```bash
uv run pytest
```

### 특정 테스트 계층별 실행
```bash
# 단위 테스트 (Unit Tests)
uv run pytest tests/unit

# 통합 테스트 (Integration Tests)
uv run pytest tests/integration

# API 엔드포인트 테스트 (E2E Tests)
uv run pytest tests/e2e
```

---

## 🔑 환경 변수 설정 (`.env`)

프로젝트 루트에 `.env` 파일을 생성하여 Supabase 및 다양한 벤더사의 LLM API 키를 설정할 수 있습니다.
API Key가 설정되지 않은 경우 자동으로 **In-Memory Fallback 저장소** 및 **Simulated LLM Service**로 안전하게 동작하여 별도 외부 설정 없이 즉시 로컬 실행이 가능합니다.

```env
# Supabase 설정 (선택 사항: 미설정 시 In-Memory 저장소로 동작)
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# LLM 벤더사별 API Key (선택 사항: 필요한 모델의 키 설정)
GEMINI_API_KEY=your-gemini-api-key       # Google Gemini 모델
OPENAI_API_KEY=your-openai-api-key       # OpenAI (GPT-4o, GPT-4o-mini 등)
ANTHROPIC_API_KEY=your-anthropic-api-key # Anthropic (Claude 3.5 Sonnet, Haiku 등)
OLLAMA_BASE_URL=http://localhost:11434   # Ollama 로컬 모델 서버 주소
```
