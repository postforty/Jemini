import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Copy, RefreshCw, Check } from 'lucide-react';
import { CURRENT_USER } from '@/entities/user';
import type { Message } from '../model/types';
import styles from './ChatMessage.module.css';

interface ChatMessageProps {
  message: Message;
  onRegenerate?: (() => void) | null;
}

export function ChatMessage({ message, onRegenerate }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.sender === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`${styles.messageBubble} ${isUser ? styles.user : styles.assistant}`}>
      <div className={`${styles.avatarIcon} ${isUser ? styles.userAvatar : styles.aiAvatar}`}>
        {isUser ? (
          CURRENT_USER.initials
        ) : (
          <svg className={styles.sparkIcon} viewBox="0 0 24 24" style={{ width: 22, height: 22 }}>
            <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#jemini-grad)" />
          </svg>
        )}
      </div>

      <div className={styles.messageContent}>
        {isUser ? (
          <div className={styles.messageText}>
            <div>{message.content}</div>
            {message.image_url && (
              <img src={message.image_url} alt="첨부 이미지" className={styles.attachedImg} />
            )}
          </div>
        ) : (
          <>
            <ReactMarkdown className={styles.markdown}>{message.content}</ReactMarkdown>
            <div className={styles.messageActions}>
              <button className={styles.actionBtn} onClick={handleCopy} title="답변 복사">
                {copied ? <Check size={14} color="#1e8e3e" /> : <Copy size={14} />}
              </button>
              {onRegenerate && (
                <button className={styles.actionBtn} onClick={onRegenerate} title="다시 생성">
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
