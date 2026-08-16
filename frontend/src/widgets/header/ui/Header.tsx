import React from 'react';
import { Edit3 } from 'lucide-react';
import styles from './Header.module.css';
import { useChatStore } from '@/entities/chat';

export function Header() {
  const setCurrentChatId = useChatStore(s => s.setCurrentChatId);
  return (
    <header className={styles.topHeader}>
      <button className={styles.upgradeBtn}>
        <span>✦ 업그레이드</span>
      </button>
      <button className={styles.iconBtn} title="새 노트 작성" onClick={() => setCurrentChatId(null)}>
        <Edit3 size={18} />
      </button>
    </header>
  );
}
