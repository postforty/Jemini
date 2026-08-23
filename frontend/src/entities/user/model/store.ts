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
  isPaymentModalOpen: boolean;
  targetProModel: string | null;
  pendingPrompt: PendingPrompt | null;
  setUser: (user: User) => void;
  setIsPro: (isPro: boolean) => void;
  setAuthModalOpen: (open: boolean) => void;
  setPaymentModalOpen: (open: boolean, targetModel?: string | null) => void;
  setPendingPrompt: (pending: PendingPrompt | null) => void;
  logout: () => void;
}

const PENDING_PROMPT_KEY = 'jemini_pending_prompt';

export const useUserStore = create<UserStore>((set) => ({
  user: GUEST_USER,
  isAuthModalOpen: false,
  isPaymentModalOpen: false,
  targetProModel: null,
  pendingPrompt: (() => {
    try {
      const saved = sessionStorage.getItem(PENDING_PROMPT_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  })(),
  setUser: (user) => set({ user }),
  setIsPro: (isPro) =>
    set((state) => ({
      user: { ...state.user, isPro },
    })),
  setAuthModalOpen: (open) => set({ isAuthModalOpen: open }),
  setPaymentModalOpen: (open, targetModel = null) =>
    set({ isPaymentModalOpen: open, targetProModel: targetModel }),
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
    set({ user: GUEST_USER, pendingPrompt: null, isPaymentModalOpen: false, targetProModel: null });
  },
}));

