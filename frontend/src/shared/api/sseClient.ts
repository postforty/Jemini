export interface SSEChunk {
  type: 'chunk';
  text: string;
}

export async function* readSSEStream(response: Response): AsyncGenerator<SSEChunk> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder('utf-8');
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const lines = decoder.decode(value).split('\n\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.replace('data: ', '')) as SSEChunk;
          yield data;
        } catch { /* ignore */ }
      }
    }
  }
}
