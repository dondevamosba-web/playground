import { useState } from 'react';
import { muscles } from '../data/muscles';
import { getTrainingIntensity } from '../hooks/useWorkoutLog';
import { useTheme } from '../context/ThemeContext';

const RECOVERY_LABELS = {
  none: { label: 'Not tracked', color: '#94a3b8' },
  fresh: { label: 'Just trained', color: '#ef4444' },
  recovering: { label: 'Recovering', color: '#f59e0b' },
  ready: { label: 'Ready', color: '#22c55e' },
};

const DAYS_OPTIONS = [7, 14, 30];

export default function StatsPanel({ log, onClear }) {
  const { c } = useTheme();
  const [days, setDays] = useState(30);

  const muscleIds = Object.keys(muscles);

  const intensities = muscleIds.map(id => ({
    id,
    name: muscles[id].name,
    count: log.filter(e => e.muscleId === id && e.type === 'trained' && e.ts > Date.now() - days * 86_400_000).length,
    intensity: getTrainingIntensity(id, log, days),
  })).sort((a, b) => b.count - a.count);

  const trained = intensities.filter(m => m.count > 0);
  const untrained = intensities.filter(m => m.count === 0);

  // Push / pull balance
  const pushIds = ['chest', 'shoulders', 'triceps', 'serratus'];
  const pullIds = ['upper_back', 'lats', 'biceps', 'rotator_cuff', 'traps_front'];
  const pushCount = log.filter(e => pushIds.includes(e.muscleId) && e.type === 'trained' && e.ts > Date.now() - days * 86_400_000).length;
  const pullCount = log.filter(e => pullIds.includes(e.muscleId) && e.type === 'trained' && e.ts > Date.now() - days * 86_400_000).length;
  const total = pushCount + pullCount || 1;
  const pushRatio = pushCount / total;

  const recentSessions = log.filter(e => e.type === 'trained').slice(0, 20);

  function timeAgo(ts) {
    const h = (Date.now() - ts) / 3_600_000;
    if (h < 1) return 'Just now';
    if (h < 24) return `${Math.floor(h)}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '14px 16px 10px', borderBottom: `1px solid ${c.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: c.text }}>📊 Training Stats</h2>
        <div style={{ display: 'flex', gap: 4 }}>
          {DAYS_OPTIONS.map(d => (
            <button key={d} onClick={() => setDays(d)} style={{
              fontSize: 11, padding: '3px 8px', borderRadius: 6, cursor: 'pointer',
              border: `1px solid ${days === d ? '#6366f1' : c.border}`,
              background: days === d ? '#eef2ff' : c.inputBg,
              color: days === d ? '#6366f1' : c.textMuted,
              fontWeight: days === d ? 700 : 400,
            }}>{d}d</button>
          ))}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px' }}>
        {log.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: c.textMuted }}>
            <div style={{ fontSize: 40 }}>📋</div>
            <p style={{ fontSize: 14, marginTop: 8 }}>No training logged yet.</p>
            <p style={{ fontSize: 12, marginTop: 4 }}>Use 🏋️ Trained mode and tap "Log this session".</p>
          </div>
        ) : (
          <>
            {/* Push / Pull Balance */}
            <div style={{ background: c.card, border: `1px solid ${c.cardBorder}`, borderRadius: 10, padding: 14, marginBottom: 14 }}>
              <p style={{ margin: '0 0 8px', fontSize: 12, fontWeight: 700, color: c.textSec, textTransform: 'uppercase', letterSpacing: 0.8 }}>Push / Pull Balance</p>
              <div style={{ display: 'flex', borderRadius: 6, overflow: 'hidden', height: 18, marginBottom: 6 }}>
                <div style={{ width: `${pushRatio * 100}%`, background: '#f97316', transition: 'width 0.4s' }} />
                <div style={{ flex: 1, background: '#3b82f6' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: c.textMuted }}>
                <span style={{ color: '#f97316', fontWeight: 600 }}>Push {pushCount}</span>
                <span>{Math.abs(pushCount - pullCount) <= 2 ? '✅ Balanced' : pushCount > pullCount ? '⚠️ Push-heavy' : '⚠️ Pull-heavy'}</span>
                <span style={{ color: '#3b82f6', fontWeight: 600 }}>Pull {pullCount}</span>
              </div>
            </div>

            {/* Most trained */}
            {trained.length > 0 && (
              <div style={{ marginBottom: 14 }}>
                <p style={{ margin: '0 0 8px', fontSize: 12, fontWeight: 700, color: c.textSec, textTransform: 'uppercase', letterSpacing: 0.8 }}>
                  Most Trained (last {days}d)
                </p>
                {trained.slice(0, 8).map(m => (
                  <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span style={{ fontSize: 12, color: c.text, width: 140, flexShrink: 0 }}>{m.name}</span>
                    <div style={{ flex: 1, height: 6, background: c.border, borderRadius: 3 }}>
                      <div style={{ width: `${m.intensity * 100}%`, height: '100%', background: m.intensity > 0.75 ? '#ef4444' : m.intensity > 0.4 ? '#22c55e' : '#3b82f6', borderRadius: 3, transition: 'width 0.4s' }} />
                    </div>
                    <span style={{ fontSize: 11, color: c.textMuted, width: 30, textAlign: 'right' }}>{m.count}×</span>
                  </div>
                ))}
              </div>
            )}

            {/* Undertrained */}
            {untrained.length > 0 && (
              <div style={{ marginBottom: 14 }}>
                <p style={{ margin: '0 0 8px', fontSize: 12, fontWeight: 700, color: c.textSec, textTransform: 'uppercase', letterSpacing: 0.8 }}>
                  ⚠️ Not trained in {days}d
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                  {untrained.map(m => (
                    <span key={m.id} style={{ fontSize: 11, background: '#dbeafe', color: '#1d4ed8', borderRadius: 10, padding: '3px 9px' }}>
                      {m.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recent history */}
            <div style={{ marginBottom: 10 }}>
              <p style={{ margin: '0 0 8px', fontSize: 12, fontWeight: 700, color: c.textSec, textTransform: 'uppercase', letterSpacing: 0.8 }}>Recent Sessions</p>
              {recentSessions.map((e, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: `1px solid ${c.borderLight}` }}>
                  <span style={{ fontSize: 13, color: c.text }}>{muscles[e.muscleId]?.name || e.muscleId}</span>
                  <span style={{ fontSize: 11, color: c.textMuted }}>{timeAgo(e.ts)}</span>
                </div>
              ))}
            </div>

            <button onClick={onClear} style={{ fontSize: 12, color: '#ef4444', background: 'none', border: `1px solid #fecaca`, borderRadius: 6, padding: '6px 12px', cursor: 'pointer', marginTop: 8 }}>
              Clear all data
            </button>
          </>
        )}
      </div>
    </div>
  );
}
