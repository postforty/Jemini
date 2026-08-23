import React, { useState } from 'react';
import { ChevronDown, Lock, Sparkles } from 'lucide-react';
import { useUserStore } from '@/entities/user';
import { MODELS, isModelPro } from '../config/models';
import styles from './ModelSelector.module.css';

interface ModelSelectorProps {
  selectedModel: string;
  onSelect: (id: string) => void;
}

export function ModelSelector({ selectedModel, onSelect }: ModelSelectorProps) {
  const [showModelMenu, setShowModelMenu] = useState(false);
  const user = useUserStore((s) => s.user);
  const setAuthModalOpen = useUserStore((s) => s.setAuthModalOpen);
  const setPaymentModalOpen = useUserStore((s) => s.setPaymentModalOpen);

  const currentModelObj = MODELS.find((m) => m.id === selectedModel) || MODELS[0];
  const isCurrentPro = isModelPro(currentModelObj.id);

  const handleModelClick = (modelId: string) => {
    const isPro = isModelPro(modelId);

    if (isPro) {
      if (user.isGuest) {
        setShowModelMenu(false);
        setAuthModalOpen(true);
        return;
      }

      if (!user.isPro) {
        setShowModelMenu(false);
        setPaymentModalOpen(true, modelId);
        return;
      }
    }

    onSelect(modelId);
    setShowModelMenu(false);
  };

  return (
    <div className={styles.modelDropdownContainer}>
      <button 
        className={styles.modelSelectBtn} 
        onClick={() => setShowModelMenu(!showModelMenu)}
      >
        <span>{currentModelObj.name}</span>
        {isCurrentPro && (
          <span className={user.isPro ? styles.activeProBadge : styles.proBadge}>
            {user.isPro ? <Sparkles size={10} /> : <Lock size={10} />}
            PRO
          </span>
        )}
        <ChevronDown size={14} />
      </button>

      {showModelMenu && (
        <div className={styles.modelMenu}>
          {MODELS.map((model) => {
            const isPro = isModelPro(model.id);
            return (
              <button
                key={model.id}
                className={`${styles.modelOption} ${selectedModel === model.id ? styles.selected : ''}`}
                onClick={() => handleModelClick(model.id)}
              >
                <div className={styles.modelHeader}>
                  <span className={styles.modelName}>{model.name}</span>
                  {isPro && (
                    <span className={user.isPro ? styles.activeProBadge : styles.proBadge}>
                      {user.isPro ? <Sparkles size={10} /> : <Lock size={10} />}
                      PRO
                    </span>
                  )}
                </div>
                <span className={styles.modelDesc}>{model.desc}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

