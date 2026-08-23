import { create } from 'zustand';
import type { Chat } from './types';
import type { Message } from '@/entities/message';

interface ChatStore {
  chats: Chat[];
  currentChatId: string | null;
  selectedModel: string;
  isGenerating: boolean;
  isSidebarCollapsed: boolean;
  setChats: (updater: (prev: Chat[]) => Chat[]) => void;
  setChatList: (chats: Chat[]) => void;
  setChatMessages: (chatId: string, messages: Message[]) => void;
  setCurrentChatId: (id: string | null) => void;
  setSelectedModel: (model: string) => void;
  setIsGenerating: (v: boolean) => void;
  setIsSidebarCollapsed: (v: boolean) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  chats: [],
  currentChatId: null,
  selectedModel: 'gemini-3.1-flash-lite',
  isGenerating: false,
  isSidebarCollapsed: false,
  setChats: (updater) => set((s) => ({ chats: updater(s.chats) })),
  setChatList: (newChats) =>
    set((s) => {
      // Preserve existing loaded messages when updating chat list from Supabase
      const merged = newChats.map((nc) => {
        const existing = s.chats.find((c) => c.id === nc.id);
        return existing && existing.messages.length > 0
          ? { ...nc, messages: existing.messages }
          : nc;
      });
      return { chats: merged };
    }),
  setChatMessages: (chatId, messages) =>
    set((s) => ({
      chats: s.chats.map((c) => (c.id === chatId ? { ...c, messages } : c)),
    })),
  setCurrentChatId: (id) => set({ currentChatId: id }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  setIsGenerating: (v) => set({ isGenerating: v }),
  setIsSidebarCollapsed: (v) => set({ isSidebarCollapsed: v }),
}));
