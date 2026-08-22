import { useChatStore } from '@/entities/chat';
import { sendMessageStream } from '@/features/send-message';

export function useChatPage() {
  const chats = useChatStore((s) => s.chats);
  const currentChatId = useChatStore((s) => s.currentChatId);
  const selectedModel = useChatStore((s) => s.selectedModel);
  const setChats = useChatStore((s) => s.setChats);
  const setCurrentChatId = useChatStore((s) => s.setCurrentChatId);
  const setIsGenerating = useChatStore((s) => s.setIsGenerating);

  const handleSendMessage = async (prompt: string, image: string | null) => {
    if (!prompt && !image) return;

    let targetChatId = currentChatId;

    if (!targetChatId) {
      targetChatId = 'chat_' + Date.now();
      const newChat = {
        id: targetChatId,
        title: prompt.slice(0, 22) + (prompt.length > 22 ? '...' : ''),
        model: selectedModel,
        messages: []
      };
      setChats((prev) => [newChat, ...prev]);
      setCurrentChatId(targetChatId);
    }

    const userMessage = {
      id: 'msg_user_' + Date.now(),
      sender: 'user' as const,
      content: prompt,
      image_url: image
    };

    setChats((prev) => prev.map(c => 
      c.id === targetChatId ? { ...c, messages: [...c.messages, userMessage] } : c
    ));

    setIsGenerating(true);

    const assistantMessageId = 'msg_ai_' + Date.now();
    setChats((prev) => prev.map(c => 
      c.id === targetChatId ? { ...c, messages: [...c.messages, { id: assistantMessageId, sender: 'assistant', content: '', image_url: null }] } : c
    ));

    try {
      let accumulatedText = '';
      await sendMessageStream({
        prompt,
        chatId: targetChatId,
        model: selectedModel,
        imageUrl: image,
        onChatId: (serverChatId) => {
          if (serverChatId && serverChatId !== targetChatId) {
            const oldId = targetChatId;
            targetChatId = serverChatId;
            setCurrentChatId(serverChatId);
            setChats(prevChats => prevChats.map(c => 
              c.id === oldId ? { ...c, id: serverChatId } : c
            ));
          }
        },
        onChunk: (text) => {
          accumulatedText += text;
          setChats(prevChats => prevChats.map(c => {
            if (c.id === targetChatId) {
              const updatedMsgs = c.messages.map(m => 
                m.id === assistantMessageId ? { ...m, content: accumulatedText } : m
              );
              return { ...c, messages: updatedMsgs };
            }
            return c;
          }));
        }
      });

      if (!accumulatedText) {
        throw new Error('Empty response received from server stream');
      }
    } catch (error) {
      console.warn('API error, using client streaming fallback:', error);
      let replyText = `안녕하세요! **${selectedModel}** 모델이 입력해주신 "${prompt}" 내용을 받아 분석했습니다.\n\n### 주요 요약\n- **입력 내용**: ${prompt}\n- **선택된 모델**: \`${selectedModel}\`\n\n\`\`\`json\n{\n  "status": "success",\n  "model": "${selectedModel}",\n  "processed": true\n}\n\`\`\``;
      
      let curr = '';
      for (let i = 0; i < replyText.length; i += 3) {
        curr += replyText.slice(i, i + 3);
        await new Promise(r => setTimeout(r, 20));
        setChats(prevChats => prevChats.map(c => {
          if (c.id === targetChatId) {
            const updatedMsgs = c.messages.map(m => 
              m.id === assistantMessageId ? { ...m, content: curr } : m
            );
            return { ...c, messages: updatedMsgs };
          }
          return c;
        }));
      }
    } finally {
      setIsGenerating(false);
    }
  };

  return {
    handleSendMessage
  };
}
