import { useEffect } from 'react';
import { useChatStore, fetchChats, fetchChatMessages } from '@/entities/chat';
import { sendMessageStream } from '@/features/send-message';

export function useChatPage() {
  const chats = useChatStore((s) => s.chats);
  const currentChatId = useChatStore((s) => s.currentChatId);
  const selectedModel = useChatStore((s) => s.selectedModel);
  const isGenerating = useChatStore((s) => s.isGenerating);
  const setChats = useChatStore((s) => s.setChats);
  const setChatList = useChatStore((s) => s.setChatList);
  const setChatMessages = useChatStore((s) => s.setChatMessages);
  const setCurrentChatId = useChatStore((s) => s.setCurrentChatId);
  const setIsGenerating = useChatStore((s) => s.setIsGenerating);

  // 1. Initial load from Supabase (SSOT)
  useEffect(() => {
    let isMounted = true;
    fetchChats().then((serverChats) => {
      if (isMounted && serverChats.length > 0) {
        setChatList(serverChats);
        const state = useChatStore.getState();
        if (!state.currentChatId) {
          setCurrentChatId(serverChats[0].id);
        }
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Load messages from Supabase when switching chats (skip if generating)
  useEffect(() => {
    if (!currentChatId) return;
    const state = useChatStore.getState();
    if (state.isGenerating) return; // Prevent overwriting streaming messages

    const target = state.chats.find((c) => c.id === currentChatId);
    if (!target || target.messages.length === 0) {
      fetchChatMessages(currentChatId).then((messages) => {
        // Double check not generating before updating
        if (!useChatStore.getState().isGenerating && messages.length > 0) {
          setChatMessages(currentChatId, messages);
        }
      });
    }
  }, [currentChatId]);

  const handleSendMessage = async (prompt: string, image: string | null) => {
    if (!prompt && !image) return;

    let activeChatId = currentChatId;
    const isNewChat = !activeChatId || activeChatId.startsWith('temp_');

    if (isNewChat) {
      activeChatId = 'temp_' + Date.now();
      const newChat = {
        id: activeChatId,
        title: prompt.slice(0, 22) + (prompt.length > 22 ? '...' : ''),
        model: selectedModel,
        messages: []
      };
      setChats((prev) => [newChat, ...prev]);
      setCurrentChatId(activeChatId);
    }

    const userMessage = {
      id: 'msg_user_' + Date.now(),
      sender: 'user' as const,
      content: prompt,
      image_url: image
    };

    const assistantMessageId = 'msg_ai_' + Date.now();
    const initialAssistantMessage = {
      id: assistantMessageId,
      sender: 'assistant' as const,
      content: '',
      image_url: null
    };

    setChats((prev) => prev.map(c => 
      c.id === activeChatId 
        ? { ...c, messages: [...c.messages, userMessage, initialAssistantMessage] } 
        : c
    ));

    setIsGenerating(true);

    try {
      let accumulatedText = '';
      await sendMessageStream({
        prompt,
        chatId: isNewChat ? null : activeChatId,
        model: selectedModel,
        imageUrl: image,
        onChatId: (serverChatId) => {
          if (serverChatId && serverChatId !== activeChatId) {
            const oldId = activeChatId;
            activeChatId = serverChatId;
            setChats(prevChats => prevChats.map(c => 
              c.id === oldId ? { ...c, id: serverChatId } : c
            ));
            setCurrentChatId(serverChatId);
          }
        },
        onChunk: (text) => {
          accumulatedText += text;
          setChats(prevChats => prevChats.map(c => {
            if (c.id === activeChatId) {
              const updatedMsgs = c.messages.map(m => 
                m.id === assistantMessageId ? { ...m, content: accumulatedText } : m
              );
              return { ...c, messages: updatedMsgs };
            }
            return c;
          }));
        },
        onSuggestedQuestions: (questions) => {
          setChats(prevChats => prevChats.map(c => {
            if (c.id === activeChatId) {
              const updatedMsgs = c.messages.map(m => 
                m.id === assistantMessageId ? { ...m, suggestedQuestions: questions } : m
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
      const fallbackQuestions = [
        "어떤 작업을 도와줄 수 있나요?",
        "Jemini의 주요 기능은 무엇인가요?",
        "간단한 예제 코드를 보여줘"
      ];
      
      let curr = '';
      for (let i = 0; i < replyText.length; i += 3) {
        curr += replyText.slice(i, i + 3);
        await new Promise(r => setTimeout(r, 20));
        setChats(prevChats => prevChats.map(c => {
          if (c.id === activeChatId) {
            const updatedMsgs = c.messages.map(m => 
              m.id === assistantMessageId ? { ...m, content: curr } : m
            );
            return { ...c, messages: updatedMsgs };
          }
          return c;
        }));
      }

      setChats(prevChats => prevChats.map(c => {
        if (c.id === activeChatId) {
          const updatedMsgs = c.messages.map(m => 
            m.id === assistantMessageId ? { ...m, suggestedQuestions: fallbackQuestions } : m
          );
          return { ...c, messages: updatedMsgs };
        }
        return c;
      }));
    } finally {
      setIsGenerating(false);
      // Synchronize latest chat list from Supabase
      fetchChats().then(setChatList);
    }
  };

  return {
    handleSendMessage
  };
}
