import { useState } from 'react';
import { warmups } from '../data/warmups';
import { muscles } from '../data/muscles';
import { useTheme } from '../context/ThemeContext';

const TYPE_META = {
  foam_roll:  { icon: '🟣', label: 'Foam Roll',  color: '#ede9fe', textColor: '#6d28d9' },
  dynamic:    { icon: '🔵', label: 'Dynamic',    color: '#dbeafe', textColor: '#1d4ed8' },
  activation: { icon: '🟡', label: 'Activate',   color: '#fef9c3', textColor: '#854d0e' },
  ramp:       { icon: '🟠', label: 'Ramp Up',    color: '#fed7aa', textColor: '#9a3412' },
  mobility:   { icon: '🟢', label: 'Mobility',   color: '#dcfce7', textColor: '#166534' },
};

function WarmupStep({ step, index, done, onToggle, c }) {
  const meta = TYPE_META[step.type] || TYPE_META.dynamic;
  return (
    <div
      onClick={onToggle}
      style={{
        display: 'flex', gap: 10, alignItems: 'flex-start',
        background: done ? c.surfaceAlt : c.card,
        border: `1px solid ${c.cardBorder}`,
        borderRadius: 10, padding: '10px 12px', marginBottom: 8,
        cursor: 'pointer', opacity: done ? 0.5 : 1,
        transition: 'opacity 0.2s',
      }}
    >
      <div style={{ width: 22, height: 22, borderRadius: '50%', border: `2px solid ${done ? '#4ade80' : c.border}`, background: done ? '#4ade80' : 'transparent', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: 1 }}>
        {done && <span style={{ fontSize: 12, color: '#fff' }}>✓</span>}
        {!done && <span style={{ fontSize: 11, color: c.textMuted, fontWeight: 700 }}>{index + 1}</span>}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
          <span style={{ fontWeight: 700, fontSize: 13, color: c.text }}>{step.name}</span>
          <span style={{ fontSize: 10, padding: '1px 6px', borderRadius: 8, background: meta.color, color: meta.textColor, fontWeight: 600 }}>
            {meta.icon} {meta.label}
          </span>
        </div>
        <p style={{ margin: 0, fontSize: 12, color: c.textSec }}>{step.cue}</p>
        <span style={{ fontSize: 11, color: c.textMuted, marginTop: 2, display: 'inline-block' }}>
          {step.duration || step.reps || step.sets}
        </span>
      </div>
    </div>
  );
}

export default function WarmupPanel({ selectedMuscles }) {
  const { c } = useTheme();
  const [done, setDone] = useState({});

  const toggle = (key) => setDone(d => ({ ...d, [key]: !d[key] }));
  const reset = () => setDone({});

  if (!selectedMuscles.length) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', padding: 24, textAlign: 'center' }}>
        <div style={{ fontSize: 40, marginBottom: 10 }}>🔥</div>
        <p style={{ fontSize: 15, fontWeight: 600, color: c.textSec, margin: 0 }}>Select muscles to warm up</p>
        <p style={{ fontSize: 13, color: c.textMuted, marginTop: 6 }}>Click muscles on the body map to generate your warm-up</p>
      </div>
    );
  }

  const totalSteps = selectedMuscles.reduce((acc, id) => acc + (warmups[id]?.length || 0), 0);
  const doneCount = Object.values(done).filter(Boolean).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '14px 16px 10px', borderBottom: `1px solid ${c.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: c.text }}>🔥 Warm-Up Plan</h2>
          <p style={{ margin: '2px 0 0', fontSize: 12, color: c.textMuted }}>
            {doneCount}/{totalSteps} steps · ~{Math.ceil(totalSteps * 1.2)} min
          </p>
        </div>
        <button onClick={reset} style={{ fontSize: 12, color: c.textMuted, background: 'none', border: `1px solid ${c.border}`, borderRadius: 6, padding: '4px 10px', cursor: 'pointer' }}>
          Reset
        </button>
      </div>

      {/* Progress bar */}
      <div style={{ height: 3, background: c.border }}>
        <div style={{ height: '100%', background: '#4ade80', width: `${(doneCount / totalSteps) * 100}%`, transition: 'width 0.3s' }} />
      </div>

      {/* Steps */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 16px' }}>
        {selectedMuscles.map(id => {
          const steps = warmups[id];
          if (!steps) return null;
          return (
            <div key={id} style={{ marginBottom: 16 }}>
              <p style={{ margin: '0 0 8px', fontSize: 12, fontWeight: 700, color: c.textSec, textTransform: 'uppercase', letterSpacing: 1 }}>
                {muscles[id]?.name || id}
              </p>
              {steps.map((step, i) => {
                const key = `${id}_${i}`;
                return (
                  <WarmupStep key={key} step={step} index={i} done={!!done[key]} onToggle={() => toggle(key)} c={c} />
                );
              })}
            </div>
          );
        })}

        {doneCount === totalSteps && totalSteps > 0 && (
          <div style={{ textAlign: 'center', padding: '16px 0', color: '#16a34a', fontWeight: 700, fontSize: 15 }}>
            ✅ Warm-up complete — go crush it!
          </div>
        )}
      </div>
    </div>
  );
}
