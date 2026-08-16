# Agent Project Guidelines (Jemini Workspace)

이 문서는 **AI 코딩 에이전트(LLM Coding Agent)**를 위한 프로젝트 전반의 작업 표준 및 서브 프로젝트별 에이전트 가이드 허브입니다.

> 💡 **사람(사용자/개발자)을 위한 프로젝트 안내서**는 [README.md](README.md)를 참조하십시오.

---

## 📌 문서 역할 구분 (AGENTS.md vs README.md)

- **`AGENTS.md` (AI 에이전트용)**:
  - AI 에이전트가 코드 생성, 리팩토링, 디버깅 시 엄격하게 준수해야 하는 **아키텍처 제약사항, 의존성 방향, 코딩 컨벤션, 검증 규칙**을 기술합니다.
- **`README.md` (사람 개발자/사용자용)**:
  - 프로젝트 소개, 주요 기능 설명, 환경 설정, 실행 방법, 화면 구조 등 **사람이 프로젝트를 이해하고 사용하는 데 필요한 정보**를 기술합니다.

---

## 📁 서브 프로젝트별 에이전트 가이드

각 서브 프로젝트의 세부 아키텍처 규칙, 계층 의존성 및 검증 절차는 하위 `AGENTS.md`를 필히 확인하고 준수하십시오.

| 서브 프로젝트 | 아키텍처 / 기술 스택 | 에이전트 가이드라인 |
|---|---|---|
| **Backend** (`backend/`) | Clean Architecture, FastAPI, `uv`, pytest | [Backend AGENTS.md](backend/AGENTS.md) |
| **Frontend** (`frontend/`) | Feature-Sliced Design (FSD), React, TypeScript, `npm` | [Frontend AGENTS.md](frontend/AGENTS.md) |

---

## 🤝 풀스택 공통 작업 표준 (Global Agent Rules)

1. **작업 디렉토리 격리**:
   - 백엔드 코드 수정 및 도구 실행은 반드시 `backend/` 디렉터리를 기준으로 수행합니다.
   - 프론트엔드 코드 수정 및 도구 실행은 반드시 `frontend/` 디렉터리를 기준으로 수행합니다.
2. **API 계약 보장 (Interface Integrity)**:
   - 백엔드 REST 엔드포인트 및 SSE 스트리밍 스펙 변경 시, 프론트엔드 API 클라이언트(`shared/api/`) 및 모델 인터페이스와의 100% 호환성을 사전/사후 검증합니다.
3. **서브 프로젝트별 검증 의무**:
   - 코드를 수정한 후에는 해당 하위 `AGENTS.md`에 명시된 검증 수단(백엔드: `uv run pytest`, 프론트엔드: `npm run build`)을 반드시 실행하여 오류가 없음을 검증합니다.
