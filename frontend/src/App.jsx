import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import FloatingInput from './components/FloatingInput';
import ChatMessage from './components/ChatMessage';

const INITIAL_CHATS = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    title: '커피 앱 기획 비판적 분석',
    model: 'gemini-3.5-flash',
    messages: [
      {
        id: 'm1',
        sender: 'user',
        content: '커피 주문 앱 기획안에 대해 비판적인 시각으로 분석해줘.',
        image_url: null,
      },
      {
        id: 'm2',
        sender: 'assistant',
        content: `커피 주문 앱 기획 시 고려해야 할 비판적 관점은 다음과 같습니다:

1. **기존 시장 과점 및 사용자 이탈 위험**: 스타벅스 사이렌 오더나 배달의민족 등 기존 강자들과의 차별점 부재 시 유저 유입이 어렵습니다.
2. **매장 POS 시스템 연동 복잡성**: 각 커피 프랜차이즈 및 개인 카페의 POS 솔루션과 실시간 주문 연동 시 커스텀 개발 비용이 증가합니다.
3. **픽업 시간 예측의 정확도**: 출퇴근 시간 대기열 증가 시 사용자 불만이 폭증할 수 있습니다.`,
      }
    ]
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    title: '커피 주문 앱 개발 고려사항',
    model: 'gemini-3.1-flash-lite',
    messages: [
      {
        id: 'm3',
        sender: 'user',
        content: '커피 주문 앱 개발할 때 중요한 기술적 고려사항이 뭐야?',
        image_url: null,
      },
      {
        id: 'm4',
        sender: 'assistant',
        content: `주요 기술적 고려사항:

- **실시간 주문 상태 WebSocket 연동**
- **위치 기반(GPS/Geofencing) 주변 매장 탐색**
- **결제 게이트웨이(PG) 안전 연동**`,
      }
    ]
  }
];

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('jemini_chats');
    return saved ? JSON.parse(saved) : INITIAL_CHATS;
  });
  const [currentChatId, setCurrentChatId] = useState(null);
  const [selectedModel, setSelectedModel] = useState('gemini-3.1-flash-lite');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    localStorage.setItem('jemini_chats', JSON.stringify(chats));
  }, [chats]);

  const activeChat = chats.find(c => c.id === currentChatId);

  const handleNewChat = () => {
    setCurrentChatId(null);
  };

  const handleSelectChat = (id) => {
    setCurrentChatId(id);
  };

  const handleDeleteChat = async (id) => {
    setChats(prev => prev.filter(c => c.id !== id));
    if (currentChatId === id) {
      setCurrentChatId(null);
    }
    try {
      await fetch(`/api/chats/${id}`, { method: 'DELETE' });
    } catch (e) {
      // Backend silent sync
    }
  };

  const handleSendMessage = async (prompt, image) => {
    if (!prompt && !image) return;

    let targetChatId = currentChatId;
    let updatedChats = [...chats];

    // If on greeting screen, create new chat entry
    if (!targetChatId) {
      const newChatId = 'chat_' + Date.now();
      const newChat = {
        id: newChatId,
        title: prompt.slice(0, 22) + (prompt.length > 22 ? '...' : ''),
        model: selectedModel,
        messages: []
      };
      updatedChats = [newChat, ...updatedChats];
      targetChatId = newChatId;
      setCurrentChatId(newChatId);
    }

    const userMessage = {
      id: 'msg_user_' + Date.now(),
      sender: 'user',
      content: prompt,
      image_url: image
    };

    // Append user message
    updatedChats = updatedChats.map(c => {
      if (c.id === targetChatId) {
        return { ...c, messages: [...c.messages, userMessage] };
      }
      return c;
    });

    setChats(updatedChats);
    setIsGenerating(true);

    // Initial empty assistant message for streaming
    const assistantMessageId = 'msg_ai_' + Date.now();
    const initialAssistantMessage = {
      id: assistantMessageId,
      sender: 'assistant',
      content: ''
    };

    updatedChats = updatedChats.map(c => {
      if (c.id === targetChatId) {
        return { ...c, messages: [...c.messages, initialAssistantMessage] };
      }
      return c;
    });
    setChats(updatedChats);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          chat_id: targetChatId,
          model: selectedModel,
          image_url: image
        })
      });

      if (response.ok && response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let accumulatedText = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunkStr = decoder.decode(value);
          const lines = chunkStr.split('\n\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.replace('data: ', ''));
                if (data.type === 'chunk') {
                  accumulatedText += data.text;
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
              } catch (err) {
                // Ignore parse errors on raw lines
              }
            }
          }
        }
      } else {
        throw new Error('API request failed');
      }
    } catch (error) {
      // Fallback local streaming response if API is unreachable
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

  return (
    <div className="app-container">
      {/* Sidebar Component */}
      <Sidebar 
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        chats={chats}
        currentChatId={currentChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      {/* Main Content Area */}
      <main className="main-content">
        <Header />

        <div className="chat-viewport">
          {!activeChat || activeChat.messages.length === 0 ? (
            /* Screenshot-matching Hero Greeting */
            <div className="hero-greeting">
              <h1 className="hero-title">신희님, 안녕하세요. 어떻게 도와드릴까요?</h1>
            </div>
          ) : (
            /* Message History */
            <div className="message-list">
              {activeChat.messages.map((msg) => (
                <ChatMessage 
                  key={msg.id} 
                  message={msg} 
                  onRegenerate={msg.sender === 'assistant' ? () => handleSendMessage(activeChat.messages[activeChat.messages.length - 2]?.content || '', null) : null}
                />
              ))}
            </div>
          )}
        </div>

        {/* Floating Input Component */}
        <FloatingInput 
          onSend={handleSendMessage}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
          disabled={isGenerating}
        />
      </main>
    </div>
  );
}
