import React from 'react';
import { Sidebar } from '@/widgets/sidebar';
import { ChatFeed } from '@/widgets/chat-feed';
import { Header } from '@/widgets/header';
import { FloatingInput } from '@/features/send-message';
import { useChatPage } from '../model/useChatPage';
import styles from './ChatPage.module.css';

export function ChatPage() {
  const { handleSendMessage } = useChatPage();

  return (
    <div className={styles.appContainer}>
      <Sidebar />
      <main className={styles.mainContent}>
        <Header />
        <ChatFeed />
        <FloatingInput onSend={handleSendMessage} />
      </main>
    </div>
  );
}
