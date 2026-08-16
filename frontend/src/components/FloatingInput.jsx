import React, { useState, useRef } from 'react';
import { Plus, Send, ChevronDown, X } from 'lucide-react';

const MODELS = [
  { id: 'gemini-3.1-flash-lite', name: 'gemini-3.1-flash-lite', desc: '빠르고 경량화된 답변' },
  { id: 'gemini-3.5-flash', name: 'gemini-3.5-flash', desc: '균형 잡힌 성능 및 속도' },
  { id: 'gemini-3-flash-preview', name: 'gemini-3-flash-preview', desc: '최신 파서 및 지능 미리보기' }
];

export default function FloatingInput({ onSend, selectedModel, setSelectedModel, disabled }) {
  const [prompt, setPrompt] = useState('');
  const [attachedImage, setAttachedImage] = useState(null);
  const [showModelMenu, setShowModelMenu] = useState(false);
  const fileInputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachedImage(reader.result);
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

  const currentModelObj = MODELS.find(m => m.id === selectedModel) || MODELS[0];

  return (
    <div className="floating-input-wrapper">
      {attachedImage && (
        <div className="attachment-preview">
          <img src={attachedImage} alt="첨부 이미지" className="preview-thumb" />
          <button className="remove-thumb" onClick={() => setAttachedImage(null)}>
            <X size={14} />
          </button>
        </div>
      )}

      <div className="input-row">
        <button 
          className="icon-btn" 
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
          className="prompt-textarea"
          rows={1}
          placeholder="Jemini에게 물어보기"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
        />

        <div className="input-controls">
          {/* Model Selector Dropdown */}
          <div className="model-dropdown-container">
            <button 
              className="model-select-btn" 
              onClick={() => setShowModelMenu(!showModelMenu)}
            >
              <span>{currentModelObj.name}</span>
              <ChevronDown size={14} />
            </button>

            {showModelMenu && (
              <div className="model-menu">
                {MODELS.map((model) => (
                  <button
                    key={model.id}
                    className={`model-option ${selectedModel === model.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedModel(model.id);
                      setShowModelMenu(false);
                    }}
                  >
                    <span className="model-name">{model.name}</span>
                    <span className="model-desc">{model.desc}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Send Button (No Mic icon per user request) */}
          <button 
            className="send-btn" 
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
