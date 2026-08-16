import { create } from 'zustand';
import type { Chat } from './types';
import { chatStorage } from '@/shared/lib/localStorage';
import { INITIAL_CHATS } from '@/shared/config/constants';

interface ChatStore {
  chats: Chat[];
  currentChatId: string | null;
  selectedModel: string;
  isGenerating: boolean;
  isSidebarCollapsed: boolean;
  setChats: (updater: (prev: Chat[]) => Chat[]) => void;
  setCurrentChatId: (id: string | null) => void;
  setSelectedModel: (model: string) => void;
  setIsGenerating: (v: boolean) => void;
  setIsSidebarCollapsed: (v: boolean) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  chats: chatStorage.load() ?? INITIAL_CHATS,
  currentChatId: null,
  selectedModel: 'gemini-3.1-flash-lite',
  isGenerating: false,
  isSidebarCollapsed: false,
  setChats: (updater) =>
    set((s) => { const chats = updater(s.chats); chatStorage.save(chats); return { chats }; }),
  setCurrentChatId: (id) => set({ currentChatId: id }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  setIsGenerating: (v) => set({ isGenerating: v }),
  setIsSidebarCollapsed: (v) => set({ isSidebarCollapsed: v }),
}));
