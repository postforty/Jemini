import React from 'react';
import { 
  Plus, Search, Image as ImageIcon, Video, Bookmark, 
  Trash2, Settings, Menu, MessageSquare
} from 'lucide-react';
import { CURRENT_USER } from '@/entities/user';
import { useChatStore } from '@/entities/chat';
import { deleteChat } from '@/features/delete-chat';
import styles from './Sidebar.module.css';

export function Sidebar() {
  const collapsed = useChatStore((s) => s.isSidebarCollapsed);
  const setCollapsed = useChatStore((s) => s.setIsSidebarCollapsed);
  const chats = useChatStore((s) => s.chats);
  const currentChatId = useChatStore((s) => s.currentChatId);
  const setCurrentChatId = useChatStore((s) => s.setCurrentChatId);
  const setChats = useChatStore((s) => s.setChats);

  const handleNewChat = () => setCurrentChatId(null);
  
  const handleDeleteChat = async (id: string) => {
    setChats(prev => prev.filter(c => c.id !== id));
    if (currentChatId === id) setCurrentChatId(null);
    await deleteChat(id);
  };

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.sidebarHeader}>
        <button 
          className={styles.iconBtn} 
          onClick={() => setCollapsed(!collapsed)} 
          title={collapsed ? "사이드바 펼치기" : "사이드바 접기"}
        >
          <Menu size={20} />
        </button>
        
        {!collapsed && (
          <div className={styles.sidebarLogo}>
            <svg className={styles.sparkIcon} viewBox="0 0 24 24">
              <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#jemini-grad)" />
            </svg>
            <span>Jemini</span>
          </div>
        )}
      </div>

      <div className={styles.navGroup}>
        <button className={`${styles.navItem} ${styles.newChat}`} onClick={handleNewChat}>
          <Plus size={18} />
          {!collapsed && <span>새 채팅</span>}
        </button>

        <button className={styles.navItem}>
          <Search size={18} />
          {!collapsed && <span>채팅 검색</span>}
        </button>

        <button className={styles.navItem}>
          <ImageIcon size={18} />
          {!collapsed && <span>이미지</span>}
        </button>

        <button className={styles.navItem}>
          <Video size={18} />
          {!collapsed && <span>동영상</span>}
        </button>

        <button className={styles.navItem}>
          <Bookmark size={18} />
          {!collapsed && <span>라이브러리</span>}
        </button>
      </div>

      {!collapsed && (
        <div className={styles.navGroup}>
          <div className={styles.sectionTitle}>
            <span>노트북</span>
          </div>
          <button className={styles.navItem}>
            <Plus size={16} />
            <span>새 노트북</span>
          </button>
        </div>
      )}

      {!collapsed && (
        <>
          <div className={styles.sectionTitle}>
            <span>최근</span>
          </div>
          <div className={styles.recentList}>
            {chats.map((chat) => (
              <div 
                key={chat.id} 
                className={`${styles.recentItem} ${currentChatId === chat.id ? styles.active : ''}`}
                onClick={() => setCurrentChatId(chat.id)}
              >
                <MessageSquare size={15} style={{ marginRight: 8, flexShrink: 0, opacity: 0.7 }} />
                <span className={styles.recentTitle}>{chat.title}</span>
                <button 
                  className={styles.deleteBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChat(chat.id);
                  }}
                  title="삭제"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      <div className={styles.sidebarFooter}>
        <div className={styles.userProfile}>
          <div className={styles.avatar}>{CURRENT_USER.initials}</div>
          {!collapsed && <span className={styles.userName}>{CURRENT_USER.name}</span>}
        </div>
        {!collapsed && (
          <button className={styles.iconBtn} title="설정">
            <Settings size={18} />
          </button>
        )}
      </div>
    </aside>
  );
}
