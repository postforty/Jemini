import React, { useRef, useEffect } from 'react';
import { useChatStore } from '@/entities/chat';
import { ChatMessage } from '@/entities/message';
import { sendMessageStream } from '@/features/send-message';
import { useUserStore } from '@/entities/user';
import styles from './ChatFeed.module.css';

interface ChatFeedProps {
  onSelectQuestion?: (question: string) => void;
}

export function ChatFeed({ onSelectQuestion }: ChatFeedProps) {
  const chats = useChatStore((s) => s.chats);
  const currentChatId = useChatStore((s) => s.currentChatId);
  const selectedModel = useChatStore((s) => s.selectedModel);
  const setChats = useChatStore((s) => s.setChats);
  const isGenerating = useChatStore((s) => s.isGenerating);
  const setIsGenerating = useChatStore((s) => s.setIsGenerating);
  
  const activeChat = chats.find(c => c.id === currentChatId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeChat?.messages]);

  const handleRegenerate = async (prompt: string) => {
    if (!prompt || !currentChatId) return;

    // Remove the last assistant message
    setChats(prev => prev.map(c => {
      if (c.id === currentChatId) {
        const lastMsg = c.messages[c.messages.length - 1];
        if (lastMsg.sender === 'assistant') {
          return { ...c, messages: c.messages.slice(0, -1) };
        }
      }
      return c;
    }));

    setIsGenerating(true);

    const assistantMessageId = 'msg_ai_' + Date.now();
    setChats(prev => prev.map(c => {
      if (c.id === currentChatId) {
        return { 
          ...c, 
          messages: [...c.messages, { id: assistantMessageId, sender: 'assistant', content: '', image_url: null }] 
        };
      }
      return c;
    }));

    try {
      let accumulatedText = '';
      await sendMessageStream({
        prompt,
        chatId: currentChatId,
        model: selectedModel,
        imageUrl: null,
        onChunk: (text) => {
          accumulatedText += text;
          setChats(prevChats => prevChats.map(c => {
            if (c.id === currentChatId) {
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
            if (c.id === currentChatId) {
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
      let replyText = `재생성 실패: 서버에 연결할 수 없습니다.`;
      setChats(prevChats => prevChats.map(c => {
        if (c.id === currentChatId) {
          const updatedMsgs = c.messages.map(m => 
            m.id === assistantMessageId ? { ...m, content: replyText } : m
          );
          return { ...c, messages: updatedMsgs };
        }
        return c;
      }));
    } finally {
      setIsGenerating(false);
    }
  };

  const user = useUserStore((s) => s.user);

  return (
    <div className={styles.chatViewport}>
      {!activeChat || activeChat.messages.length === 0 ? (
        <div className={styles.heroGreeting}>
          <h1 className={styles.heroTitle}>
            {user.isGuest ? '게스트님, 안녕하세요. 어떻게 도와드릴까요?' : `${user.name}님, 안녕하세요. 어떻게 도와드릴까요?`}
          </h1>
        </div>
      ) : (
        <div className={styles.messageList}>
          {activeChat.messages.map((msg, idx) => {
            const isLastAssistant = msg.sender === 'assistant' && idx === activeChat.messages.length - 1;
            const previousUserMessage = activeChat.messages[idx - 1]?.content;

            return (
              <ChatMessage 
                key={msg.id} 
                message={msg} 
                onRegenerate={isLastAssistant ? () => handleRegenerate(previousUserMessage || '') : null}
                onSelectQuestion={isLastAssistant ? onSelectQuestion : undefined}
                isGenerating={isGenerating}
              />
            );
          })}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
}
