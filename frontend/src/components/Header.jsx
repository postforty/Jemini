import React from 'react';
import { Edit3 } from 'lucide-react';

export default function Header() {
  return (
    <header className="top-header">
      <button className="upgrade-btn">
        <span>✦ 업그레이드</span>
      </button>
      <button className="icon-btn" title="새 노트 작성">
        <Edit3 size={18} />
      </button>
    </header>
  );
}
