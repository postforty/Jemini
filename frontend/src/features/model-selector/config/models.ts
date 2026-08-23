export interface ModelOption {
  id: string;
  name: string;
  desc: string;
  provider?: string;
  isPro?: boolean;
}

export function isModelPro(modelId: string): boolean {
  if (!modelId) return false;
  if (modelId === 'gemini-3.1-flash-lite') return false;
  if (modelId.startsWith('ollama')) return false;
  return true;
}

export const MODELS: ModelOption[] = [
  // Google Gemini (Free & Pro)
  { id: 'gemini-3.1-flash-lite', name: 'gemini-3.1-flash-lite', desc: '빠르고 경량화된 답변 (Google)', provider: 'Google', isPro: false },
  { id: 'gemini-3.5-flash',      name: 'gemini-3.5-flash',      desc: '균형 잡힌 성능 및 멀티모달 (Google)', provider: 'Google', isPro: true },
  { id: 'gemini-3-flash-preview',name: 'gemini-3-flash-preview', desc: '최신 파서 및 지능 미리보기 (Google)', provider: 'Google', isPro: true },
  
  // OpenAI (Pro)
  { id: 'gpt-4o-mini',           name: 'gpt-4o-mini',           desc: '고성능 경량 AI 모델 (OpenAI)', provider: 'OpenAI', isPro: true },
  { id: 'gpt-4o',                name: 'gpt-4o',                desc: '최상위 플래그십 AI 모델 (OpenAI)', provider: 'OpenAI', isPro: true },
  
  // Anthropic (Pro)
  { id: 'claude-3-5-haiku-latest',  name: 'claude-3-5-haiku',    desc: '초고속 고지능 모델 (Anthropic)', provider: 'Anthropic', isPro: true },
  { id: 'claude-3-5-sonnet-latest', name: 'claude-3-5-sonnet',   desc: '정밀 코딩 및 분석 특화 (Anthropic)', provider: 'Anthropic', isPro: true },

  // Ollama (Free Local)
  { id: 'ollama:gemma3:270m',    name: 'ollama:gemma3:270m',    desc: '로컬 경량 오픈소스 모델 (Ollama)', provider: 'Ollama', isPro: false },
];

export const DEFAULT_MODEL = MODELS[0].id;

