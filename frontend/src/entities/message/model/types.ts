export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  image_url: string | null;
}
