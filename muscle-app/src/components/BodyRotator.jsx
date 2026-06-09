import { useState, useRef, useEffect, useCallback } from 'react';
import BodyMapFront from './BodyMapFront';
import BodyMapBack from './BodyMapBack';
import BodyMapSide from './BodyMapSide';

// 4 faces: 0=Front, 90=Right, 180=Back, 270=Left
const FACES = [
  { angle: 0,   label: 'FRONT',      component: (p) => <BodyMapFront {...p} /> },
  { angle: 90,  label: 'RIGHT SIDE', component: (p) => <BodyMapSide  {...p} flipped={true} /> },
  { angle: 180, label: 'BACK',       component: (p) => <BodyMapBack  {...p} /> },
  { angle: 270, label: 'LEFT SIDE',  component: (p) => <BodyMapSide  {...p} flipped={false} /> },
];

function normDeg(d) { return ((d % 360) + 360) % 360; }

// Which face is active and how far through the transition (0–1)
function getFaceState(deg) {
  const n = normDeg(deg);
  const faceIndex = Math.floor(n / 90) % 4;           // 0,1,2,3
  const progress  = (n % 90) / 90;                    // 0→1 within segment
  return { faceIndex, progress };
}

// cosine-based scaleX: 1 at face-on (0,180) → 0 at edge (90)
// Within a 90° segment, local angle goes 0→90
// We want scaleX=1 at 0, scaleX=0 at 45, scaleX=1 at 90
function sectionScaleX(progress) {
  return Math.abs(Math.cos(progress * Math.PI));
}

// When scaleX < threshold, the face swap should occur (at progress ≈ 0.5)
const SWAP_THRESHOLD = 0.5;

export default function BodyRotator({ getStyle, onSelect }) {
  const [deg, setDeg] = useState(0);           // snapped target (multiples of 90)
  const [liveDeg, setLiveDeg] = useState(0);   // live while dragging
  const [dragging, setDragging] = useState(false);
  const [transitioning, setTransitioning] = useState(false);
  const startX = useRef(null);
  const startDeg = useRef(0);
  const containerRef = useRef(null);

  const { faceIndex, progress } = getFaceState(liveDeg);
  const scaleX = sectionScaleX(progress);

  // Which face to actually render: swap at midpoint of each 90° segment
  const displayFace = progress >= SWAP_THRESHOLD
    ? (faceIndex + 1) % 4
    : faceIndex;

  // The displayed face's local rotation angle around its own Y axis
  // progress 0→0.5: rotate from 0° toward -90° (foreshortening going out)
  // progress 0.5→1: from +90° coming in → 0°
  const localAngle = progress < SWAP_THRESHOLD
    ? -(progress / SWAP_THRESHOLD) * 90          // 0 → -90
    : ((progress - SWAP_THRESHOLD) / SWAP_THRESHOLD) * 90 - 90; // -90 → 0 (but mirrored face)

  // ── drag handling ──
  const onDragStart = useCallback((clientX) => {
    setDragging(true);
    startX.current = clientX;
    startDeg.current = liveDeg;
  }, [liveDeg]);

  const onDragMove = useCallback((clientX) => {
    if (!dragging) return;
    const delta = (clientX - startX.current) * 0.7;
    setLiveDeg(startDeg.current - delta); // drag right = rotate clockwise
  }, [dragging]);

  const onDragEnd = useCallback(() => {
    if (!dragging) return;
    setDragging(false);
    const n = normDeg(liveDeg);
    const snapped = Math.round(n / 90) * 90 % 360;
    const base = liveDeg - n;
    setLiveDeg(base + snapped);
    setDeg(snapped);
  }, [dragging, liveDeg]);

  // global mouse
  useEffect(() => {
    if (!dragging) return;
    const mm = (e) => onDragMove(e.clientX);
    const mu = () => onDragEnd();
    window.addEventListener('mousemove', mm);
    window.addEventListener('mouseup', mu);
    return () => { window.removeEventListener('mousemove', mm); window.removeEventListener('mouseup', mu); };
  }, [dragging, onDragMove, onDragEnd]);

  // touch
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ts = (e) => { e.preventDefault(); onDragStart(e.touches[0].clientX); };
    const tm = (e) => { e.preventDefault(); onDragMove(e.touches[0].clientX); };
    const te = () => onDragEnd();
    el.addEventListener('touchstart', ts, { passive: false });
    el.addEventListener('touchmove', tm, { passive: false });
    el.addEventListener('touchend', te);
    return () => {
      el.removeEventListener('touchstart', ts);
      el.removeEventListener('touchmove', tm);
      el.removeEventListener('touchend', te);
    };
  }, [onDragStart, onDragMove, onDragEnd]);

  const rotateTo = (targetDeg) => {
    setDeg(targetDeg);
    setTransitioning(true);
    // Animate liveDeg toward target smoothly
    const start = liveDeg;
    const end = start + ((targetDeg - normDeg(start) + 540) % 360 - 180);
    const duration = 420;
    const t0 = performance.now();
    function step(now) {
      const t = Math.min((now - t0) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      setLiveDeg(start + (end - start) * ease);
      if (t < 1) requestAnimationFrame(step);
      else { setLiveDeg(end); setTransitioning(false); }
    }
    requestAnimationFrame(step);
  };

  const rotateLeft  = () => rotateTo((deg + 270) % 360);
  const rotateRight = () => rotateTo((deg + 90) % 360);

  const faceProps = { getStyle, onSelect };
  const norm = normDeg(liveDeg);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', userSelect: 'none' }}>

      {/* 3D flip zone */}
      <div
        ref={containerRef}
        onMouseDown={(e) => { if (!transitioning) onDragStart(e.clientX); }}
        style={{
          flex: 1,
          cursor: dragging ? 'grabbing' : 'grab',
          overflow: 'hidden',
          position: 'relative',
          perspective: '900px',
        }}
      >
        {/* Perspective wrapper */}
        <div style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{
            width: '100%',
            height: '100%',
            transform: dragging
              ? `perspective(700px) rotateY(${localAngle}deg) scaleX(${Math.max(scaleX, 0.02)})`
              : 'none',
            transition: dragging ? 'none' : 'transform 0.4s cubic-bezier(0.4,0,0.2,1)',
            transformOrigin: 'center center',
          }}>
            {FACES[displayFace].component(faceProps)}
          </div>
        </div>

        {/* Drag hint */}
        {!dragging && norm === 0 && (
          <div style={{
            position: 'absolute', bottom: 6, left: '50%', transform: 'translateX(-50%)',
            fontSize: 10, color: '#cbd5e1', pointerEvents: 'none', whiteSpace: 'nowrap',
          }}>
            ← drag to rotate →
          </div>
        )}
      </div>

      {/* ── Controls ── */}
      <div style={{ padding: '6px 14px 10px', flexShrink: 0 }}>
        {/* Face label */}
        <div style={{ textAlign: 'center', marginBottom: 6 }}>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 1.5, color: '#94a3b8' }}>
            {FACES[normDeg(deg) / 90 % 4 | 0].label}
          </span>
        </div>

        {/* Rotation buttons + arc */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={rotateLeft}  style={btnStyle}>◀</button>

          {/* 360 arc indicator */}
          <div style={{ flex: 1, position: 'relative', height: 20 }}>
            {/* Track */}
            <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: 3, marginTop: -1.5, borderRadius: 2, background: '#e2e8f0' }} />
            {/* Fill (wraps at 360) */}
            <div style={{
              position: 'absolute', top: '50%', left: 0,
              width: `${(norm / 360) * 100}%`,
              height: 3, marginTop: -1.5, borderRadius: 2,
              background: 'linear-gradient(to right, #3b82f6, #8b5cf6, #f97316)',
              transition: dragging ? 'none' : 'width 0.4s cubic-bezier(0.4,0,0.2,1)',
            }} />
            {/* Dot */}
            <div
              onMouseDown={(e) => { e.stopPropagation(); onDragStart(e.clientX); }}
              style={{
                position: 'absolute', top: '50%',
                left: `${(norm / 360) * 100}%`,
                transform: 'translate(-50%, -50%)',
                width: 14, height: 14, borderRadius: '50%',
                background: '#6366f1',
                border: '2px solid #fff',
                boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
                cursor: 'pointer',
                transition: dragging ? 'none' : 'left 0.4s cubic-bezier(0.4,0,0.2,1)',
              }}
            />
            {/* 4 tick marks */}
            {[0, 25, 50, 75].map((pct, i) => (
              <div key={i} style={{
                position: 'absolute', top: '50%',
                left: `${pct}%`,
                transform: 'translate(-50%, -50%)',
                width: 3, height: 10, background: '#e2e8f0',
                borderRadius: 1,
              }} />
            ))}
          </div>

          <button onClick={rotateRight} style={btnStyle}>▶</button>
        </div>

        {/* 4 face dots */}
        <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 6 }}>
          {FACES.map((f, i) => {
            const active = (normDeg(deg) / 90 | 0) === i;
            return (
              <button
                key={i}
                onClick={() => rotateTo(f.angle)}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, padding: '2px 4px',
                }}
              >
                <div style={{
                  width: 7, height: 7, borderRadius: '50%',
                  background: active ? '#6366f1' : '#e2e8f0',
                  transition: 'background 0.2s',
                }} />
                <span style={{ fontSize: 8, color: active ? '#6366f1' : '#cbd5e1', fontWeight: active ? 700 : 400, letterSpacing: 0.5 }}>
                  {f.label.split(' ')[0]}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

const btnStyle = {
  width: 28, height: 28, borderRadius: '50%',
  border: '1px solid #e2e8f0', background: '#f8fafc',
  cursor: 'pointer', fontSize: 11, display: 'flex',
  alignItems: 'center', justifyContent: 'center', flexShrink: 0,
  color: '#64748b', padding: 0,
};
