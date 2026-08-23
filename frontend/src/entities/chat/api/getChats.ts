import { httpClient } from '@/shared/api';
import type { Chat } from '../model/types';
import type { Message } from '@/entities/message';

interface ChatDto {
  id: string;
  title: string;
  model: string;
  created_at: string;
  updated_at: string;
}

interface MessageDto {
  id: string;
  chat_id: string;
  sender: 'user' | 'assistant';
  content: string;
  image_url: string | null;
  created_at: string;
}

export async function fetchChats(): Promise<Chat[]> {
  try {
    const res = await httpClient.get('/api/chats');
    if (!res.ok) throw new Error('Failed to fetch chats');
    const data: ChatDto[] = await res.json();
    return data.map((item) => ({
      id: item.id,
      title: item.title,
      model: item.model,
      messages: [],
    }));
  } catch (error) {
    console.error('Error fetching chats from backend:', error);
    return [];
  }
}

export async function fetchChatMessages(chatId: string): Promise<Message[]> {
  try {
    const res = await httpClient.get(`/api/chats/${chatId}/messages`);
    if (!res.ok) throw new Error('Failed to fetch messages');
    const data: MessageDto[] = await res.json();
    return data.map((item) => ({
      id: item.id,
      sender: item.sender,
      content: item.content,
      image_url: item.image_url,
    }));
  } catch (error) {
    console.error(`Error fetching messages for chat ${chatId}:`, error);
    return [];
  }
}
