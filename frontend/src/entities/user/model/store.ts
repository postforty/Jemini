import { create } from 'zustand';
import type { User } from './types';
import { GUEST_USER } from './types';

export interface PendingPrompt {
  prompt: string;
  image: string | null;
}

interface UserStore {
  user: User;
  isAuthModalOpen: boolean;
  pendingPrompt: PendingPrompt | null;
  setUser: (user: User) => void;
  setAuthModalOpen: (open: boolean) => void;
  setPendingPrompt: (pending: PendingPrompt | null) => void;
  logout: () => void;
}

const PENDING_PROMPT_KEY = 'jemini_pending_prompt';

export const useUserStore = create<UserStore>((set) => ({
  user: GUEST_USER,
  isAuthModalOpen: false,
  pendingPrompt: (() => {
    try {
      const saved = sessionStorage.getItem(PENDING_PROMPT_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  })(),
  setUser: (user) => set({ user }),
  setAuthModalOpen: (open) => set({ isAuthModalOpen: open }),
  setPendingPrompt: (pendingPrompt) => {
    try {
      if (pendingPrompt) {
        sessionStorage.setItem(PENDING_PROMPT_KEY, JSON.stringify(pendingPrompt));
      } else {
        sessionStorage.removeItem(PENDING_PROMPT_KEY);
      }
    } catch (e) {
      console.error('Failed to save pending prompt to sessionStorage:', e);
    }
    set({ pendingPrompt });
  },
  logout: () => {
    try {
      sessionStorage.removeItem(PENDING_PROMPT_KEY);
    } catch {}
    set({ user: GUEST_USER, pendingPrompt: null });
  },
}));
