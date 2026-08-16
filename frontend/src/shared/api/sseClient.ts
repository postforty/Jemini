export interface SSEChunk {
  type: 'chat_id' | 'chunk' | 'done';
  text?: string;
  chat_id?: string;
  full_text?: string;
}

export async function* readSSEStream(response: Response): AsyncGenerator<SSEChunk> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop() || '';

    for (const part of parts) {
      for (const line of part.split('\n')) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          try {
            const data = JSON.parse(trimmed.slice(6)) as SSEChunk;
            yield data;
          } catch {
            /* ignore */
          }
        }
      }
    }
  }

  if (buffer.trim()) {
    for (const line of buffer.split('\n')) {
      const trimmed = line.trim();
      if (trimmed.startsWith('data: ')) {
        try {
          const data = JSON.parse(trimmed.slice(6)) as SSEChunk;
          yield data;
        } catch {
          /* ignore */
        }
      }
    }
  }
}

