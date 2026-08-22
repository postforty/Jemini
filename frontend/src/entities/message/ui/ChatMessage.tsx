import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Copy, RefreshCw, Check, ThumbsUp, ThumbsDown, MoreHorizontal } from 'lucide-react';
import type { Message } from '../model/types';
import { SuggestedQuestions } from './SuggestedQuestions';
import styles from './ChatMessage.module.css';

interface ChatMessageProps {
  message: Message;
  onRegenerate?: (() => void) | null;
  onSelectQuestion?: (question: string) => void;
  isGenerating?: boolean;
}

export function ChatMessage({ message, onRegenerate, onSelectQuestion, isGenerating }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.sender === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // 사용자 메시지: 오른쪽 정렬 말풍선
  if (isUser) {
    return (
      <div className={styles.userMessageRow}>
        <div className={styles.userBubble}>
          <div className={styles.messageText}>
            <span>{message.content}</span>
            {message.image_url && (
              <img src={message.image_url} alt="첨부 이미지" className={styles.attachedImg} />
            )}
          </div>
        </div>
      </div>
    );
  }

  // AI 응답: 왼쪽 정렬, 배경 없음
  return (
    <div className={styles.assistantMessageRow}>
      <div className={styles.messageContent}>
        <ReactMarkdown className={styles.markdown}>{message.content}</ReactMarkdown>
        <div className={styles.messageActions}>
          <button className={styles.actionBtn} title="좋아요">
            <ThumbsUp size={16} />
          </button>
          <button className={styles.actionBtn} title="싫어요">
            <ThumbsDown size={16} />
          </button>
          <button className={styles.actionBtn} onClick={handleCopy} title="답변 복사">
            {copied ? <Check size={16} color="#1e8e3e" /> : <Copy size={16} />}
          </button>
          <button className={styles.actionBtn} title="더보기">
            <MoreHorizontal size={16} />
          </button>
          {onRegenerate && (
            <button className={styles.actionBtn} onClick={onRegenerate} title="다시 생성">
              <RefreshCw size={16} />
            </button>
          )}
        </div>
        {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
          <SuggestedQuestions
            questions={message.suggestedQuestions}
            onSelectQuestion={onSelectQuestion}
            disabled={isGenerating}
          />
        )}
      </div>
    </div>
  );
}
