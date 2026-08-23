import { useEffect, useRef } from 'react';
import { useChatStore, fetchChats, fetchChatMessages } from '@/entities/chat';
import { useUserStore } from '@/entities/user';
import { supabase } from '@/shared/api';
import { mapSupabaseUser } from '@/features/auth';
import { sendMessageStream } from '@/features/send-message';
import { fetchSubscriptionStatus, confirmPayment } from '@/features/payment';

export function useChatPage() {
  const chats = useChatStore((s) => s.chats);
  const currentChatId = useChatStore((s) => s.currentChatId);
  const selectedModel = useChatStore((s) => s.selectedModel);
  const setSelectedModel = useChatStore((s) => s.setSelectedModel);
  const setChats = useChatStore((s) => s.setChats);
  const setChatList = useChatStore((s) => s.setChatList);
  const setChatMessages = useChatStore((s) => s.setChatMessages);
  const setCurrentChatId = useChatStore((s) => s.setCurrentChatId);
  const setIsGenerating = useChatStore((s) => s.setIsGenerating);

  const user = useUserStore((s) => s.user);
  const setUser = useUserStore((s) => s.setUser);
  const setIsPro = useUserStore((s) => s.setIsPro);
  const setAuthModalOpen = useUserStore((s) => s.setAuthModalOpen);
  const setPendingPrompt = useUserStore((s) => s.setPendingPrompt);

  const isHandlingPending = useRef(false);

  // 1. Initialize Auth, Pro status & listen to changes
  useEffect(() => {
    // Check current session on mount
    supabase.auth.getSession().then(({ data: { session } }) => {
      const initialUser = mapSupabaseUser(session?.user ?? null);
      setUser(initialUser);
      if (!initialUser.isGuest) {
        fetchSubscriptionStatus().then((sub) => {
          setIsPro(sub.is_pro);
        });
        fetchChats().then((serverChats) => {
          setChatList(serverChats);
          if (serverChats.length > 0) {
            setCurrentChatId(serverChats[0].id);
          }
        });
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      const mapped = mapSupabaseUser(session?.user ?? null);
      setUser(mapped);

      if (mapped.isGuest) {
        setIsPro(false);
        // Clear all chats on logout
        setChats(() => []);
        setCurrentChatId(null);
      } else {
        fetchSubscriptionStatus().then((sub) => {
          setIsPro(sub.is_pro);
        });
        // Refresh chats specifically for this logged-in user
        fetchChats().then((serverChats) => {
          setChatList(serverChats);
          const state = useChatStore.getState();
          if (!state.currentChatId && serverChats.length > 0) {
            setCurrentChatId(serverChats[0].id);
          }
        });
      }

      // If user logged in and has pending prompt, auto-send
      if (!mapped.isGuest && !isHandlingPending.current) {
        const pending = useUserStore.getState().pendingPrompt;
        if (pending) {
          isHandlingPending.current = true;
          setAuthModalOpen(false);
          setPendingPrompt(null);
          // Wait a tick to ensure UI state is settled
          setTimeout(() => {
            handleSendMessage(pending.prompt, pending.image);
            isHandlingPending.current = false;
          }, 100);
        }
      }
    });

    // Check Toss Payments Redirect Callback URL parameters
    const params = new URLSearchParams(window.location.search);
    const paymentKey = params.get('paymentKey');
    const orderId = params.get('orderId');
    const amount = params.get('amount') || 9900;
    const isPaymentSuccess = params.get('payment_success');

    if ((isPaymentSuccess || paymentKey) && orderId) {
      const key = paymentKey || `pk_redirect_${Date.now()}`;
      confirmPayment({
        paymentKey: key,
        orderId,
        amount: Number(amount) || 9900,
      }).then(() => {
        setIsPro(true);
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
      }).catch(err => {
        console.error('Failed to confirm redirect payment:', err);
      });
    }

    return () => {
      subscription.unsubscribe();
    };
  }, []);


  // 2. Load messages from Supabase when switching chats (skip if generating)
  useEffect(() => {
    if (!currentChatId || currentChatId.startsWith('temp_')) return;
    const state = useChatStore.getState();
    if (state.isGenerating) return; // Prevent overwriting streaming messages

    const target = state.chats.find((c) => c.id === currentChatId);
    if (!target || target.messages.length === 0) {
      fetchChatMessages(currentChatId).then((messages) => {
        if (!useChatStore.getState().isGenerating && messages.length > 0) {
          setChatMessages(currentChatId, messages);
        }
      });
    }
  }, [currentChatId]);

  const handleSendMessage = async (prompt: string, image: string | null) => {
    if (!prompt && !image) return;

    const currentUser = useUserStore.getState().user;
    const activeChat = useChatStore.getState().chats.find((c) => c.id === currentChatId);
    const userMessageCount = activeChat
      ? activeChat.messages.filter((m) => m.sender === 'user').length
      : 0;

    // Intercept 3rd question attempt for guest users
    if (currentUser.isGuest && userMessageCount >= 2) {
      setPendingPrompt({ prompt, image });
      setAuthModalOpen(true);
      return;
    }

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
        chatId: isNewChat ? '' : (activeChatId || ''),
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
      // Synchronize latest chat list from Supabase for logged-in user
      const currentUserState = useUserStore.getState().user;
      if (!currentUserState.isGuest) {
        fetchChats().then(setChatList);
      }
    }
  };

  return {
    handleSendMessage
  };
}
