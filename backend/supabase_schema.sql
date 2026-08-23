-- ==========================================
-- Supabase PostgreSQL Schema for Jemini Chatbot
-- ==========================================

-- 1. Chats Table (대화 세션)
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT '새 대화',
    model VARCHAR(100) NOT NULL DEFAULT 'gemini-3.1-flash-lite',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster query by user_id
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);

-- 2. Messages Table (메시지 내역)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'assistant')),
    content TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster query by chat_id
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);

-- Sample Initial Data (스크린샷 대화 목록 데이터)
INSERT INTO chats (id, title, model, created_at) VALUES
('11111111-1111-1111-1111-111111111111', '커피 앱 기획 비판적 분석', 'gemini-3.5-flash', NOW() - INTERVAL '1 hour'),
('22222222-2222-2222-2222-222222222222', '커피 주문 앱 개발 고려사항', 'gemini-3.1-flash-lite', NOW() - INTERVAL '2 hours')
ON CONFLICT (id) DO NOTHING;

INSERT INTO messages (chat_id, sender, content, created_at) VALUES
('11111111-1111-1111-1111-111111111111', 'user', '커피 주문 앱 기획안에 대해 비판적인 시각으로 분석해줘.', NOW() - INTERVAL '1 hour'),
('11111111-1111-1111-1111-111111111111', 'assistant', '커피 주문 앱 기획 시 고려해야 할 비판적 관점은 다음과 같습니다:\n\n1. **기존 시장 과점 및 사용자 이탈 위험**: 스타벅스 사이렌 오더나 배달의민족 등 기존 강자들과의 차별점 부재 시 유저 유입이 어렵습니다.\n2. **매장 POS 시스템 연동 복잡성**: 각 커피 프랜차이즈 및 개인 카페의 POS 솔루션과 실시간 주문 연동 시 커스텀 개발 비용이 증가합니다.\n3. **픽업 시간 예측의 정확도**: 출퇴근 시간 대기열 증가 시 사용자 불만이 폭증할 수 있습니다.', NOW() - INTERVAL '59 minutes'),
('22222222-2222-2222-2222-222222222222', 'user', '커피 주문 앱 개발할 때 중요한 기술적 고려사항이 뭐야?', NOW() - INTERVAL '2 hours'),
('22222222-2222-2222-2222-222222222222', 'assistant', '주요 기술적 고려사항:\n- **실시간 주문 상태 WebSocket 연동**\n- **위치 기반(GPS/Geofencing) 주변 매장 탐색**\n- **결제 게이트웨이(PG) 안전 연동**', NOW() - INTERVAL '1 hour 59 minutes')
ON CONFLICT DO NOTHING;
