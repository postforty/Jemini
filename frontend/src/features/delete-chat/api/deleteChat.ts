import { httpClient } from '@/shared/api/httpClient';

export async function deleteChat(id: string): Promise<void> {
  try {
    await httpClient.delete(`/api/chats/${id}`);
  } catch {
    // 백엔드 silent sync
  }
}
