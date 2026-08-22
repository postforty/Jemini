# Jemini Chatbot Frontend (Vite + React)

이 프로젝트는 **Vite**와 **React 18**을 기반으로 구축된 **Jemini** AI 챗봇 웹 애플리케이션 프론트엔드입니다.

> 🤖 **AI 에이전트 개발 지침 및 FSD 아키텍처 제약사항**은 [frontend/AGENTS.md](AGENTS.md)를 참조하십시오.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Core**: React 18, Vite, TypeScript
- **State Management**: Zustand
- **Icons**: Lucide React
- **Markdown & Syntax Highlighting**: React Markdown, PrismJS
- **Styling**: CSS Modules (`.module.css`) 및 글로벌 Jemini 테마 CSS

---

## 🚀 주요 기능 (Key Features)

1. **Gemini 스타일 대화형 UI & 멀티 벤더 지원**
   - 접기/펼치기가 가능한 반응형 사이드바 (대화 목록 관리 및 새 대화 생성)
   - 중앙 상단 **다중 벤더 모델 선택 드롭다운** (Google Gemini, OpenAI GPT-4o, Anthropic Claude 3.5, Ollama)
   - 플로팅 스타일의 메시지 입력창 및 파일/이미지 첨부 UI
2. **실시간 SSE 응답 스트리밍**
   - FastAPI 백엔드와의 Server-Sent Events (SSE) 연동을 통한 실시간 타이핑 스트리밍
3. **마크다운 & 코드 구문 강조**
   - AI 응답 텍스트의 Markdown 렌더링
   - PrismJS 기반의 다국어 코드 블록 하이라이팅 및 복사 기능
4. **FSD (Feature-Sliced Design) 구조**
   - 확장성과 유지보수성을 극대화한 계층형 컴포넌트 아키텍처

---

## 💻 실행 및 빌드 가이드 (Getting Started)

### 1. 의존성 패키지 설치
```bash
npm install
```

### 2. 개발 서버 실행 (`npm run dev`)
기본 설정으로 `http://localhost:3000`에서 개발 서버가 실행됩니다.
```bash
npm run dev
```

> 💡 **참고**: 원활한 API 통신을 위해 백엔드 서버(`http://localhost:8000`)를 사전에 실행해 두어야 합니다. (Vite 프록시 `/api` -> `http://localhost:8000` 자동 포워딩)

### 3. 프로덕션 빌드 및 미리보기
```bash
# 프로덕션 빌드
npm run build

# 빌드 결과물 로컬 미리보기
npm run preview
```

---

## 📁 디렉토리 구조 (FSD Architecture)

```text
frontend/
├── src/
│   ├── app/                # 메인 애플리케이션 진입점 및 글로벌 스타일
│   ├── pages/              # 라우팅 단위 페이지 레이아웃 조합 (ChatPage)
│   ├── widgets/            # 독립적인 복합 UI 블록 조합 (Sidebar, ChatFeed, Header)
│   ├── features/           # 사용자 인터랙션 단위 기능 (SendMessage, ModelSelector, DeleteChat)
│   ├── entities/           # 비즈니스 엔티티 모델 및 Zustand 상태 스토어
│   └── shared/             # 공통 UI 컴포넌트, API 클라이언트, 유틸리티, 상수
│
├── index.html              # HTML 진입점
├── package.json            # 프로젝트 메타데이터 및 의존성
├── tsconfig.json           # TypeScript 컴파일러 설정
└── vite.config.js          # Vite 번들러 및 프록시 설정
```
