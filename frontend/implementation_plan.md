# Jemini 프론트엔드 FSD 아키텍처 변환 계획

## 확정된 기술 선택

| 항목 | 선택 |
|------|------|
| 상태 관리 | **Zustand** |
| 언어 | **TypeScript** (`.jsx` → `.tsx`) |
| 스타일 | **CSS Modules** (`.module.css`) |

## 배경 및 목적

현재 프론트엔드는 모든 비즈니스 로직이 `App.jsx` 하나에 집중된 **God Component 패턴**으로 작성되어 있습니다.
FSD(Feature-Sliced Design) 아키텍처를 적용하여 **관심사 분리**, **재사용성 확보**, **테스트 가능성** 향상을 목표로 합니다.

> [!IMPORTANT]
> 기존 UI/기능은 그대로 유지하며 **구조 리팩토링만** 수행합니다. 새 기능 추가는 이번 범위에 포함되지 않습니다.

---

## FSD 레이어 의존성 방향

```
app → pages → widgets → features → entities → shared
```

- **각 레이어는 자신보다 하위 레이어에만 의존** 가능합니다.
- 같은 레이어 내 슬라이스 간 cross-import는 금지됩니다.

---

## 변환 전후 구조 비교

### Before (현재)
```
src/
├── App.jsx          ← 263줄, 모든 로직 혼재
├── main.jsx
├── index.css        ← 633줄, 전역 단일 파일
└── components/
    ├── ChatMessage.jsx
    ├── FloatingInput.jsx
    ├── Header.jsx
    └── Sidebar.jsx
```

### After (목표)
```
src/
├── app/
│   ├── App.tsx              ← 레이아웃 조합만 (30줄 이하 목표)
│   ├── main.tsx
│   └── styles/
│       └── global.css       ← CSS 변수, reset, body 기본 스타일만
│
├── pages/
│   └── chat/
│       ├── ui/ChatPage.tsx  ← 페이지 레이아웃
│       ├── model/useChatPage.ts ← 커스텀 훅 (Zustand store 연결)
│       └── index.ts
│
├── widgets/
│   ├── sidebar/
│   │   ├── ui/Sidebar.tsx
│   │   ├── ui/Sidebar.module.css
│   │   └── index.ts
│   └── chat-feed/
│       ├── ui/ChatFeed.tsx
│       ├── ui/ChatFeed.module.css
│       └── index.ts
│
├── features/
│   ├── send-message/
│   │   ├── api/sendMessage.ts  ← SSE 스트리밍 로직
│   │   ├── ui/FloatingInput.tsx
│   │   ├── ui/FloatingInput.module.css
│   │   └── index.ts
│   ├── model-selector/
│   │   ├── config/models.ts    ← MODELS 상수 분리
│   │   ├── ui/ModelSelector.tsx
│   │   ├── ui/ModelSelector.module.css
│   │   └── index.ts
│   └── delete-chat/
│       ├── api/deleteChat.ts
│       └── index.ts
│
├── entities/
│   ├── chat/
│   │   ├── model/types.ts      ← Chat 인터페이스 정의
│   │   ├── model/store.ts      ← Zustand store (핵심)
│   │   └── index.ts
│   ├── message/
│   │   ├── model/types.ts      ← Message 인터페이스 정의
│   │   ├── ui/ChatMessage.tsx  ← 이동
│   │   ├── ui/ChatMessage.module.css
│   │   └── index.ts
│   └── user/
│       ├── model/config.ts     ← 사용자 정보 (하드코딩 제거)
│       └── index.ts
│
└── shared/
    ├── api/
    │   ├── httpClient.ts       ← fetch 래퍼
    │   └── sseClient.ts        ← SSE 스트리밍 유틸 (async generator)
    ├── ui/
    │   ├── GradientDefs.tsx    ← SVG #jemini-grad 공용 정의
    │   └── IconButton.tsx      ← icon-btn 공용 컴포넌트
    ├── config/
    │   └── constants.ts        ← 앱 전역 상수, INITIAL_CHATS
    └── lib/
        └── localStorage.ts     ← localStorage 유틸
```

---

## 구현 Phase 상세

---

### Phase 1. 프로젝트 기반 세팅

**목표**: 폴더 구조 생성 및 경로 alias 설정

#### [MODIFY] [vite.config.js](file:///d:/wsh/vibe-workspace/ch10/jemini/frontend/vite.config.js)

`@/` 경로 alias 추가로 상대경로 지옥(`../../../`) 방지:

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 3000,
    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
  },
});
```

#### [NEW] `tsconfig.json` + `tsconfig.node.json`
- TypeScript 컴파일러 설정 추가
- `paths` alias (`@/*`) 설정 추가

#### 패키지 설치
```bash
npm install zustand
npm install -D typescript
```

**작업**: 모든 슬라이스 폴더 및 `index.ts` 빈 파일 생성

---

### Phase 2. `shared` 레이어 구축

**목표**: 모든 레이어에서 공통으로 사용하는 인프라 코드 분리

#### [NEW] `shared/api/httpClient.ts`
```ts
export const httpClient = {
  delete: (url: string): Promise<Response> =>
    fetch(url, { method: 'DELETE' }),
  post: <T>(url: string, body: T): Promise<Response> =>
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
};
```

#### [NEW] `shared/api/sseClient.ts`
```ts
export interface SSEChunk {
  type: 'chunk';
  text: string;
}

export async function* readSSEStream(response: Response): AsyncGenerator<SSEChunk> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder('utf-8');
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const lines = decoder.decode(value).split('\n\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.replace('data: ', '')) as SSEChunk;
          yield data;
        } catch { /* ignore */ }
      }
    }
  }
}
```

#### [NEW] `shared/lib/localStorage.ts`
```ts
import type { Chat } from '@/entities/chat';

const CHATS_KEY = 'jemini_chats';
export const chatStorage = {
  load: (): Chat[] | null => {
    try { return JSON.parse(localStorage.getItem(CHATS_KEY) ?? 'null'); }
    catch { return null; }
  },
  save: (chats: Chat[]): void =>
    localStorage.setItem(CHATS_KEY, JSON.stringify(chats)),
};
```

#### [NEW] `shared/ui/GradientDefs.jsx`
```jsx
// SVG #jemini-grad 전역 정의 — 의존성 버그 해결
export default function GradientDefs() {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }}>
      <defs>
        <linearGradient id="jemini-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#4285f4" />
          <stop offset="50%"  stopColor="#9b51e0" />
          <stop offset="100%" stopColor="#d93025" />
        </linearGradient>
      </defs>
    </svg>
  );
}
```

#### [NEW] `shared/config/constants.js`
```js
export const APP_NAME = 'Jemini';
export const INITIAL_CHATS = [ /* 현재 App.jsx의 INITIAL_CHATS 이동 */ ];
```

---

### Phase 3. `entities` 레이어 구축

**목표**: 핵심 비즈니스 엔티티의 타입과 상태를 독립 모듈로 분리

#### [NEW] `entities/user/model/config.ts`
```ts
export interface User {
  name: string;
  initials: string;
}
export const CURRENT_USER: User = { name: '신희', initials: '신희' };
```

#### [NEW] `entities/chat/model/types.ts`
```ts
import type { Message } from '@/entities/message';

export interface Chat {
  id: string;
  title: string;
  model: string;
  messages: Message[];
}
```

#### [NEW] `entities/chat/model/store.ts` — Zustand Store (핵심)
```ts
import { create } from 'zustand';
import type { Chat } from './types';
import { chatStorage } from '@/shared/lib/localStorage';
import { INITIAL_CHATS } from '@/shared/config/constants';

interface ChatStore {
  chats: Chat[];
  currentChatId: string | null;
  selectedModel: string;
  isGenerating: boolean;
  setChats: (updater: (prev: Chat[]) => Chat[]) => void;
  setCurrentChatId: (id: string | null) => void;
  setSelectedModel: (model: string) => void;
  setIsGenerating: (v: boolean) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  chats: chatStorage.load() ?? INITIAL_CHATS,
  currentChatId: null,
  selectedModel: 'gemini-3.1-flash-lite',
  isGenerating: false,
  setChats: (updater) =>
    set((s) => { const chats = updater(s.chats); chatStorage.save(chats); return { chats }; }),
  setCurrentChatId: (id) => set({ currentChatId: id }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  setIsGenerating: (v) => set({ isGenerating: v }),
}));
```

#### [NEW] `entities/message/model/types.ts`
```ts
export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  image_url: string | null;
}
```

#### [MOVE+REFACTOR] `entities/message/ui/ChatMessage.tsx`
- `src/components/ChatMessage.jsx` → `src/entities/message/ui/ChatMessage.tsx`
- `CURRENT_USER` import 적용으로 하드코딩 제거
- CSS Module (`ChatMessage.module.css`) 적용
- `GradientDefs`는 `app/App.tsx`에서 한번만 렌더링

---

### Phase 4. `features` 레이어 구축

**목표**: 사용자 행동 단위의 기능을 독립 슬라이스로 분리

#### [NEW] `features/model-selector/config/models.ts`
```ts
export interface ModelOption {
  id: string;
  name: string;
  desc: string;
}
export const MODELS: ModelOption[] = [
  { id: 'gemini-3.1-flash-lite', name: 'gemini-3.1-flash-lite', desc: '빠르고 경량화된 답변' },
  { id: 'gemini-3.5-flash',      name: 'gemini-3.5-flash',      desc: '균형 잡힌 성능 및 속도' },
  { id: 'gemini-3-flash-preview',name: 'gemini-3-flash-preview', desc: '최신 파서 및 지능 미리보기' },
];
export const DEFAULT_MODEL = MODELS[0].id;
```

#### [NEW] `features/model-selector/ui/ModelSelector.tsx`
- `FloatingInput.jsx`의 모델 드롭다운 UI 부분만 독립 컴포넌트로 추출
- Props: `selectedModel: string`, `onSelect: (id: string) => void`
- CSS Module 적용

#### [NEW] `features/delete-chat/api/deleteChat.ts`
```ts
import { httpClient } from '@/shared/api/httpClient';

export async function deleteChat(id: string): Promise<void> {
  try {
    await httpClient.delete(`/api/chats/${id}`);
  } catch {
    // 백엔드 silent sync
  }
}
```

#### [NEW] `features/send-message/api/sendMessage.ts`
```ts
import { httpClient } from '@/shared/api/httpClient';
import { readSSEStream } from '@/shared/api/sseClient';

interface SendMessageParams {
  prompt: string;
  chatId: string;
  model: string;
  imageUrl: string | null;
  onChunk: (text: string) => void;
}

export async function sendMessageStream(params: SendMessageParams): Promise<void> {
  const response = await httpClient.post('/api/generate', {
    prompt: params.prompt,
    chat_id: params.chatId,
    model: params.model,
    image_url: params.imageUrl,
  });
  if (!response.ok || !response.body) throw new Error('API request failed');
  for await (const data of readSSEStream(response)) {
    if (data.type === 'chunk') params.onChunk(data.text);
  }
}
```

#### [MOVE+REFACTOR] `features/send-message/ui/FloatingInput.tsx`
- `src/components/FloatingInput.jsx` → `src/features/send-message/ui/FloatingInput.tsx`
- `ModelSelector` 컴포넌트 import로 내부 드롭다운 교체
- Zustand store에서 `selectedModel`, `setSelectedModel` 직접 구독 (Prop Drilling 제거)
- CSS Module 적용

---

### Phase 5. `widgets` 레이어 구축

**목표**: 여러 entities/features를 조합한 복합 UI 블록

#### [MOVE+REFACTOR] `widgets/sidebar/ui/Sidebar.tsx`
- `src/components/Sidebar.jsx` → `src/widgets/sidebar/ui/Sidebar.tsx`
- `CURRENT_USER` import로 하드코딩 '신희' 제거
- SVG `<defs>` 블록 제거 (GradientDefs로 이전)
- **Zustand store에서 `chats`, `currentChatId` 직접 구독** → props 수 대폭 감소
- `collapsed` 상태도 Zustand store로 이전하여 `setCollapsed` prop 제거
- CSS Module 적용

#### [NEW] `widgets/chat-feed/ui/ChatFeed.tsx`
- `App.jsx`의 `chat-viewport` + `hero-greeting` + `message-list` 블록을 담당
- **Zustand store에서 `activeChat` 직접 구독** → props 최소화
- CSS Module 적용

---

### Phase 6. `pages` 레이어 구축

**목표**: 레이아웃 조합 전담 컴포넌트

#### [NEW] `pages/chat/ui/ChatPage.tsx`
- `App.jsx`에서 레이아웃 관련 JSX 추출
- 비즈니스 로직은 없고 Widgets 조합만 담당

```tsx
// ChatPage.tsx 예시 — 매우 단순한 레이아웃 조합
import { Sidebar } from '@/widgets/sidebar';
import { ChatFeed } from '@/widgets/chat-feed';
import { FloatingInput } from '@/features/send-message';
import { Header } from '@/widgets/header';

export default function ChatPage() {
  return (
    <div className={styles.container}>
      <Sidebar />
      <main className={styles.main}>
        <Header />
        <ChatFeed />
        <FloatingInput />
      </main>
    </div>
  );
}
```

#### [NEW] `pages/chat/model/useChatPage.ts`
- `App.jsx`에 남아있는 핸들러 로직(`handleSendMessage`, `handleDeleteChat`, `handleNewChat`)을 커스텀 훅으로 추출
- Zustand `useChatStore` + `sendMessageStream` + `deleteChat` 조합
- SSE 에러 시 로컬 폴백 스트리밍 로직 포함

---

### Phase 7. `app` 레이어 정리

**목표**: App.jsx를 최대한 단순화, 글로벌 스타일 분리

#### [MODIFY→RENAME] `App.jsx` → `app/App.tsx`
```tsx
import GradientDefs from '@/shared/ui/GradientDefs';
import ChatPage from '@/pages/chat';
import './styles/global.css';

export default function App() {
  return (
    <>
      <GradientDefs />   {/* SVG gradient 전역 1회 렌더 */}
      <ChatPage />
    </>
  );
}
```

#### [MODIFY] `app/styles/global.css` (기존 `index.css`에서 추출)
- `:root` CSS 변수만 유지
- `*`, `body`, `#root` 전역 reset
- **`.app-container`, `.main-content` 레이아웃 클래스** → `pages/chat/ui/ChatPage.module.css`로 이동
- 나머지 컴포넌트별 스타일은 각 슬라이스 `.module.css`로 이동

#### [DELETE] `src/index.css`
- 내용을 `global.css` + 각 슬라이스 `.module.css`로 분산 후 삭제

---

## 확정된 기술 결정

> [!NOTE]
> 아래 세 가지 모두 사용자에 의해 확정되었습니다.
> - **상태 관리**: Zustand
> - **언어**: TypeScript (`.tsx`)
> - **스타일**: CSS Modules (`.module.css`)

---

## 검증 계획

### 각 Phase 완료 시
- [ ] `npm run dev`로 앱 정상 실행 확인
- [ ] 기존 UI (채팅 목록, 메시지 전송, SSE 스트리밍, 삭제) 기능 동일하게 동작 확인
- [ ] 브라우저 콘솔 에러 없음 확인
- [ ] TypeScript 컴파일 에러 없음 (`tsc --noEmit`)

### Phase 7 완료 시
- [ ] `App.tsx` 20줄 이하 달성 확인
- [ ] 모든 cross-layer import 방향이 FSD 규칙 준수하는지 확인
- [ ] SVG gradient 버그 (`#jemini-grad`) 해결 확인
- [ ] Zustand store가 `entities/chat`에만 존재하는지 확인
- [ ] `src/components/` 폴더 완전 제거 확인

---

## Phase별 예상 작업량

| Phase | 작업 내용 | 예상 소요 |
|-------|----------|---------|
| 1 | 폴더 구조 생성, vite.config alias, tsconfig, Zustand 설치 | 15분 |
| 2 | shared 레이어 (httpClient, sseClient, localStorage, GradientDefs) | 25분 |
| 3 | entities 레이어 (types, Zustand store, ChatMessage.tsx 이동) | 30분 |
| 4 | features 레이어 (send-message, model-selector, delete-chat) | 35분 |
| 5 | widgets 레이어 (Sidebar.tsx, ChatFeed.tsx) | 25분 |
| 6 | pages 레이어 (ChatPage.tsx, useChatPage.ts) | 30분 |
| 7 | App.tsx 정리, CSS 분리, 구 파일 삭제 | 20분 |
| **합계** | | **~3시간** |
