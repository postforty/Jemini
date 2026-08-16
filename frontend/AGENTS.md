# Frontend Agent Guidelines (Jemini Frontend)

이 문서는 **AI 코딩 에이전트(LLM Coding Agent)**가 프론트엔드 코드를 작성, 리팩토링, 디버깅할 때 준수해야 하는 엄격한 개발 규칙과 아키텍처 제약 사항을 정의합니다.

> 💡 **사용자/개발자를 위한 프론트엔드 실행 가이드 및 설명서**는 [README.md](frontend/README.md)를 참조하십시오.

---

## 🎨 1. 프론트엔드 아키텍처 규칙 (FSD - Feature-Sliced Design)

에이전트는 모든 프론트엔드 코드 작성 시 아래의 **계층 단방향 의존성 규칙**을 엄격히 준수해야 합니다:
`app` ➔ `pages` ➔ `widgets` ➔ `features` ➔ `entities` ➔ `shared`

- **계층 간 참조 규칙**:
  - 각 레이어는 오직 **자신보다 하위 레이어**만 import할 수 있습니다.
  - **동일 계층 내 슬라이스 간 직접 참조(cross-import)는 엄격히 금지**됩니다. (예: `features/a`에서 `features/b`를 직접 import 불가)
  - 하위 레이어에서 상위 레이어를 역참조하는 것은 절대 금지됩니다.
- **주요 레이어 역할 (`src/`)**:
  - `app/`: 글로벌 스타일, 프로바이더 설정 및 애플리케이션 진입점.
  - `pages/`: 라우팅 단위 페이지 레이아웃 및 뷰 조합.
  - `widgets/`: 독립적으로 동작 가능한 복합 UI 블록 (예: Sidebar, ChatFeed, Header).
  - `features/`: 사용자 인터랙션 단위 기능 로직 (예: SendMessage, ModelSelector, DeleteChat).
  - `entities/`: 핵심 비즈니스 도메인 데이터 모델, 인터페이스 타입, 글로벌 상태 스토어(Zustand).
  - `shared/`: 재사용 가능한 기본 UI 컴포넌트, 공통 API 클라이언트, 유틸리티, 상수.

---

## 🛠️ 2. 기술 표준 및 구현 제약

- **언어**: `TypeScript`를 기본으로 사용하며, `any` 타입 사용을 지양하고 DTO 및 Props 인터페이스를 엄격하게 정의합니다.
- **상태 관리**: `Zustand`를 사용하며, 도메인 상태 스토어는 반드시 `entities/` 계층에 위치시킵니다.
- **스타일링**: 컴포넌트별 `CSS Modules`(`.module.css`)를 사용하여 스타일 충돌을 방지합니다. 인라인 스타일의 남용을 지양합니다.
- **경로 참조**: 상대 경로(`../../`) 대신 Vite 설정된 `@/` alias(`src/` 기준)를 우선적으로 사용합니다.

---

## 🚀 3. 도구 및 명령어 실행 규칙

- **패키지 관리자**: `npm` 사용
- **의존성 설치**: `npm install`
- **개발 서버 실행**: `npm run dev`
- **빌드 및 타입 검증**: `npm run build`

---

## 📝 4. 코드 스타일 및 컴포넌트 설계 가이드

- **컴포넌트 분리**: 함수형 컴포넌트(`FC`)를 사용하며, 복잡한 비즈니스 로직은 Custom Hook으로 분리하여 뷰와 로직의 관심사를 명확히 구분합니다.
- **백엔드 연동 계약 준수**: 백엔드 REST API 및 SSE 스트림 변경 시 `shared/api/` 및 관련 모델 타입을 동기화하여 런타임 오류를 방지합니다.
