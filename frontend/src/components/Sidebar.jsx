import React from 'react';
import { 
  Plus, 
  Search, 
  Image as ImageIcon, 
  Video, 
  Bookmark, 
  BookOpen, 
  Trash2, 
  Settings, 
  Menu, 
  MessageSquare
} from 'lucide-react';

export default function Sidebar({ 
  collapsed, 
  setCollapsed, 
  chats, 
  currentChatId, 
  onSelectChat, 
  onNewChat, 
  onDeleteChat 
}) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <button 
          className="icon-btn" 
          onClick={() => setCollapsed(!collapsed)} 
          title={collapsed ? "사이드바 펼치기" : "사이드바 접기"}
        >
          <Menu size={20} />
        </button>
        
        {!collapsed && (
          <div className="sidebar-logo">
            <svg className="spark-icon" viewBox="0 0 24 24">
              <defs>
                <linearGradient id="jemini-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#4285f4" />
                  <stop offset="50%" stopColor="#9b51e0" />
                  <stop offset="100%" stopColor="#d93025" />
                </linearGradient>
              </defs>
              <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" />
            </svg>
            <span>Jemini</span>
          </div>
        )}
      </div>

      {/* Main Nav Items */}
      <div className="nav-group">
        <button className="nav-item new-chat" onClick={onNewChat}>
          <Plus size={18} />
          {!collapsed && <span>새 채팅</span>}
        </button>

        <button className="nav-item">
          <Search size={18} />
          {!collapsed && <span>채팅 검색</span>}
        </button>

        <button className="nav-item">
          <ImageIcon size={18} />
          {!collapsed && <span>이미지</span>}
        </button>

        <button className="nav-item">
          <Video size={18} />
          {!collapsed && <span>동영상</span>}
        </button>

        <button className="nav-item">
          <Bookmark size={18} />
          {!collapsed && <span>라이브러리</span>}
        </button>
      </div>

      {/* Notebook Section */}
      {!collapsed && (
        <div className="nav-group">
          <div className="section-title">
            <span>노트북</span>
          </div>
          <button className="nav-item">
            <Plus size={16} />
            <span>새 노트북</span>
          </button>
        </div>
      )}

      {/* Recent Chats Section */}
      {!collapsed && (
        <>
          <div className="section-title">
            <span>최근</span>
          </div>
          <div className="recent-list">
            {chats.map((chat) => (
              <div 
                key={chat.id} 
                className={`recent-item ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
              >
                <MessageSquare size={15} style={{ marginRight: 8, flexShrink: 0, opacity: 0.7 }} />
                <span className="recent-title">{chat.title}</span>
                <button 
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
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

      {/* Footer Profile */}
      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="avatar">신희</div>
          {!collapsed && <span className="user-name">신희</span>}
        </div>
        {!collapsed && (
          <button className="icon-btn" title="설정">
            <Settings size={18} />
          </button>
        )}
      </div>
    </aside>
  );
}
