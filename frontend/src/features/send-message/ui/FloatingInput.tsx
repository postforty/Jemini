import React, { useState, useRef } from 'react';
import { Plus, Send, X } from 'lucide-react';
import { useChatStore } from '@/entities/chat';
import { ModelSelector } from '@/features/model-selector';
import styles from './FloatingInput.module.css';

interface FloatingInputProps {
  onSend: (prompt: string, image: string | null) => void;
}

export function FloatingInput({ onSend }: FloatingInputProps) {
  const [prompt, setPrompt] = useState('');
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selectedModel = useChatStore((state) => state.selectedModel);
  const setSelectedModel = useChatStore((state) => state.setSelectedModel);
  const disabled = useChatStore((state) => state.isGenerating);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = () => {
    if ((!prompt.trim() && !attachedImage) || disabled) return;
    onSend(prompt.trim(), attachedImage);
    setPrompt('');
    setAttachedImage(null);
  };

  return (
    <div className={styles.floatingInputWrapper}>
      {attachedImage && (
        <div className={styles.attachmentPreview}>
          <img src={attachedImage} alt="첨부 이미지" className={styles.previewThumb} />
          <button className={styles.removeThumb} onClick={() => setAttachedImage(null)}>
            <X size={14} />
          </button>
        </div>
      )}

      <div className={styles.inputRow}>
        <button 
          className={styles.iconBtn} 
          onClick={() => fileInputRef.current?.click()}
          title="파일/이미지 첨부"
        >
          <Plus size={20} />
        </button>
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/*" 
          style={{ display: 'none' }} 
        />

        <textarea
          className={styles.promptTextarea}
          rows={1}
          placeholder="Jemini에게 물어보기"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
        />

        <div className={styles.inputControls}>
          <ModelSelector 
            selectedModel={selectedModel}
            onSelect={setSelectedModel}
          />

          <button 
            className={styles.sendBtn} 
            onClick={handleSubmit} 
            disabled={(!prompt.trim() && !attachedImage) || disabled}
            title="전송"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
