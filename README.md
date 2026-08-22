# Jemini (Full-Stack AI Chatbot)

Google Gemini 스타일의 UI와 Clean Architecture 기반의 FastAPI 백엔드로 구성된 풀스택 AI 챗봇 모노레포 프로젝트입니다.

---

## 📁 서브 프로젝트 안내

각 서브 프로젝트의 상세한 아키텍처, 환경 설정 및 기능 설명은 하위 디렉터리의 `README.md`를 참조하십시오.

| 서브 프로젝트 | 기술 스택 | 설명서 |
|---|---|---|
| **Backend** (`backend/`) | Python, FastAPI, Clean Architecture, LangChain (Multi-Vendor), `uv`, pytest | [backend/README.md](backend/README.md) |
| **Frontend** (`frontend/`) | React 18, Vite, TypeScript, FSD, Zustand | [frontend/README.md](frontend/README.md) |

---

## 🚀 빠른 시작 (Quick Start)

### 1. 백엔드 실행
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```
- API 서버: `http://localhost:8000` (Swagger: `http://localhost:8000/docs`)

### 2. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```
- 웹 애플리케이션: `http://localhost:3000`

---

## 🤖 AI 에이전트 가이드

AI 코딩 에이전트를 위한 개발 규칙 및 아키텍처 제약사항은 [AGENTS.md](AGENTS.md)를 참조하십시오.