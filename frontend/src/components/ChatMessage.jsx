import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Copy, RefreshCw, Check } from 'lucide-react';

export default function ChatMessage({ message, onRegenerate }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.sender === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar-icon ${isUser ? 'user-avatar' : 'ai-avatar'}`}>
        {isUser ? (
          '신희'
        ) : (
          <svg className="spark-icon" viewBox="0 0 24 24" style={{ width: 22, height: 22 }}>
            <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#jemini-grad)" />
          </svg>
        )}
      </div>

      <div className="message-content">
        {isUser ? (
          <div className="message-text">
            <div>{message.content}</div>
            {message.image_url && (
              <img src={message.image_url} alt="첨부 이미지" className="attached-img" />
            )}
          </div>
        ) : (
          <>
            <ReactMarkdown>{message.content}</ReactMarkdown>
            <div className="message-actions">
              <button className="action-btn" onClick={handleCopy} title="답변 복사">
                {copied ? <Check size={14} color="#1e8e3e" /> : <Copy size={14} />}
              </button>
              {onRegenerate && (
                <button className="action-btn" onClick={onRegenerate} title="다시 생성">
                  <RefreshCw size={14} />
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
