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
