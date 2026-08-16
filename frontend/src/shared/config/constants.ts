export const APP_NAME = 'Jemini';
export const INITIAL_CHATS = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    title: '커피 앱 기획 비판적 분석',
    model: 'gemini-3.5-flash',
    messages: [
      {
        id: 'm1',
        sender: 'user',
        content: '커피 주문 앱 기획안에 대해 비판적인 시각으로 분석해줘.',
        image_url: null,
      },
      {
        id: 'm2',
        sender: 'assistant',
        content: `커피 주문 앱 기획 시 고려해야 할 비판적 관점은 다음과 같습니다:

1. **기존 시장 과점 및 사용자 이탈 위험**: 스타벅스 사이렌 오더나 배달의민족 등 기존 강자들과 정면 대결해야 하므로 차별점 부재 시 유저 유입이 어렵습니다.
2. **매장 POS 시스템 연동 복잡성**: 각 커피 프랜차이즈 및 개인 카페의 POS 솔루션과 실시간 주문 연동 시 커스텀 개발 비용이 급증할 위험이 존재합니다.
3. **픽업 시간 예측의 정확도**: 출퇴근 시간 등 병목 시간대의 대기열 증가 시 사용자 불만이 폭증할 수 있습니다.`,
        image_url: null,
      }
    ]
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    title: '커피 주문 앱 개발 고려사항',
    model: 'gemini-3.1-flash-lite',
    messages: [
      {
        id: 'm3',
        sender: 'user',
        content: '커피 주문 앱 개발할 때 중요한 기술적 고려사항이 뭐야?',
        image_url: null,
      },
      {
        id: 'm4',
        sender: 'assistant',
        content: `주요 기술적 고려사항:

- **실시간 주문 상태 WebSocket 연동**
- **위치 기반(GPS/Geofencing) 주변 매장 탐색**
- **결제 게이트웨이(PG) 안전 연동**`,
        image_url: null,
      }
    ]
  }
];
