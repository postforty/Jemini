import type { Message } from '@/entities/message';

export interface Chat {
  id: string;
  title: string;
  model: string;
  messages: Message[];
}
