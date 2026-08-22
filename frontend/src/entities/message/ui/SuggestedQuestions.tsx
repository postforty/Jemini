import React from 'react';
import { Sparkles } from 'lucide-react';
import styles from './SuggestedQuestions.module.css';

interface SuggestedQuestionsProps {
  questions?: string[];
  onSelectQuestion?: (question: string) => void;
  disabled?: boolean;
}

export function SuggestedQuestions({
  questions,
  onSelectQuestion,
  disabled = false,
}: SuggestedQuestionsProps) {
  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Sparkles size={14} className={styles.sparkleIcon} />
        <span>추천 후속 질문</span>
      </div>
      <div className={styles.chipsContainer}>
        {questions.map((question, idx) => (
          <button
            key={idx}
            type="button"
            className={styles.questionChip}
            onClick={() => onSelectQuestion?.(question)}
            disabled={disabled}
            title={question}
          >
            <span>{question}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
