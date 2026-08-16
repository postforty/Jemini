// SVG #jemini-grad 전역 정의 — 의존성 버그 해결
export default function GradientDefs() {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }}>
      <defs>
        <linearGradient id="jemini-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#4285f4" />
          <stop offset="50%"  stopColor="#9b51e0" />
          <stop offset="100%" stopColor="#d93025" />
        </linearGradient>
      </defs>
    </svg>
  );
}
