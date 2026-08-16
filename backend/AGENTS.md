# Backend Agent Guidelines (Jemini Backend)

이 문서는 **AI 코딩 에이전트(LLM Coding Agent)**가 백엔드 코드를 작성, 리팩토링, 디버깅할 때 준수해야 하는 엄격한 개발 규칙과 아키텍처 제약 사항을 정의합니다.

> 💡 **사용자/개발자를 위한 백엔드 실행 가이드 및 설명서**는 [README.md](file:///d:/wsh/vibe-workspace/ch10/jemini/backend/README.md)를 참조하십시오.

---

## 🏛️ 1. 백엔드 아키텍처 규칙 (Clean Architecture)

에이전트는 모든 백엔드 코드 작성 시 아래의 **단방향 의존성 규칙**을 반드시 준수해야 합니다:
`Presentation` ➔ `Use Cases` ➔ `Domain` ⬅ `Infrastructure`

- **Domain 계층 (`app/domain/`)**:
  - 순수 Python 코드로만 작성합니다. (FastAPI, Supabase, SQLAlchemy 등 외부 프레임워크/라이브러리 종속성 절대 금지)
  - 핵심 엔티티(`entities.py`)와 추상 인터페이스(`repositories.py`, `services.py` 등의 ABC)만 정의합니다.
- **Use Cases 계층 (`app/usecases/`)**:
  - 비즈니스 유스케이스 흐름 제어 및 오케스트레이션을 담당합니다.
  - 오직 추상 인터페이스(`IChatRepository`, `IMessageRepository`, `ILLMService`)에만 의존하며, 구체적인 DB나 외부 API 클래스를 직접 임포트/참조하지 않습니다.
- **Infrastructure 계층 (`app/infrastructure/`)**:
  - DB(Supabase, InMemory) 및 외부 API(Gemini)의 구체적인 구현체를 작성합니다.
  - Domain 계층의 인터페이스를 상속받아 구현합니다.
- **Presentation 계층 (`app/presentation/`)**:
  - FastAPI 라우터(`api/v1/`), 요청/응답 Pydantic DTO(`schemas.py`), 의존성 주입 Container(`dependencies.py`)를 관리합니다.

---

## 🧪 2. TDD & 테스트 원칙

- **테스트 동시 작성/업데이트**: 비즈니스 로직 및 UseCase 추가/수정 시 `tests/` 디렉토리에 단위/통합/E2E 테스트를 반드시 함께 작성하거나 업데이트합니다.
- **검증 실행 의무**: 코드 변경 후 반드시 백엔드 루트(`backend/`) 디렉터리에서 `pytest`를 실행하여 모든 테스트가 통과하는지 검증합니다.
  ```bash
  uv run pytest
  ```
- **API 계약(Contract) 보존**: 프론트엔드와 통신하는 REST DTO 구조 및 SSE(Server-Sent Events) 스트리밍 데이터 포맷은 프론트엔드와 100% 호환되도록 유지합니다.

---

## 🚀 3. 도구 및 명령어 실행 규칙

- **패키지 관리자**: 오직 `uv`만을 사용합니다 (`pip` 직접 사용 지양).
- **의존성 설치/동기화**: `uv sync`
- **개발 서버 실행**: `uv run uvicorn main:app --reload --port 8000`
- **테스트 실행**: `uv run pytest`

---

## 📝 4. 코드 스타일 및 품질 제약

- **Type Hinting**: 모든 함수, 메서드 파라미터, 반환값에 명확한 Python Type Hinting을 적용합니다.
- **명시적 의존성 주입(DI)**: 클래스 및 유스케이스 내부에서 전역 싱글톤을 직접 생성하지 않고 생성자 주입(`__init__`)을 사용합니다.
- **불필요한 변경 방지**: 기존 주석, docstring 및 기존 테스트의 의도를 임의로 훼손하지 않습니다.
