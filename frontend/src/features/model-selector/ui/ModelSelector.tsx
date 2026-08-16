import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { MODELS } from '../config/models';
import styles from './ModelSelector.module.css';

interface ModelSelectorProps {
  selectedModel: string;
  onSelect: (id: string) => void;
}

export function ModelSelector({ selectedModel, onSelect }: ModelSelectorProps) {
  const [showModelMenu, setShowModelMenu] = useState(false);
  const currentModelObj = MODELS.find((m) => m.id === selectedModel) || MODELS[0];

  return (
    <div className={styles.modelDropdownContainer}>
      <button 
        className={styles.modelSelectBtn} 
        onClick={() => setShowModelMenu(!showModelMenu)}
      >
        <span>{currentModelObj.name}</span>
        <ChevronDown size={14} />
      </button>

      {showModelMenu && (
        <div className={styles.modelMenu}>
          {MODELS.map((model) => (
            <button
              key={model.id}
              className={`${styles.modelOption} ${selectedModel === model.id ? styles.selected : ''}`}
              onClick={() => {
                onSelect(model.id);
                setShowModelMenu(false);
              }}
            >
              <span className={styles.modelName}>{model.name}</span>
              <span className={styles.modelDesc}>{model.desc}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
