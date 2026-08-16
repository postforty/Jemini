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
    if (data.type === 'chunk' && data.text) params.onChunk(data.text);
  }
}
