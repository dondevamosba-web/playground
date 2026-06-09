import { useState } from 'react';
import { muscles } from '../data/muscles';
import { useTheme } from '../context/ThemeContext';

const TABS = {
  worked: [
    { key: 'stretch',    label: 'Stretch',    icon: '🧘' },
    { key: 'strengthen', label: 'Strengthen', icon: '💪' },
    { key: 'rest',       label: 'Rest',       icon: '😴' },
  ],
  hurts: [
    { key: 'immediate',  label: 'Right Now',  icon: '🧊' },
    { key: 'stretch',    label: 'Stretch',    icon: '🧘' },
    { key: 'strengthen', label: 'Strengthen', icon: '💪' },
    { key: 'see_doctor', label: 'See Doctor?', icon: '⚠️' },
  ],
};

function ExerciseCard({ exercise, c }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      onClick={() => setOpen(!open)}
      style={{
        background: c.card, border: `1px solid ${c.cardBorder}`,
        borderRadius: 10, padding: '10px 12px', marginBottom: 8, cursor: 'pointer',
        boxShadow: open ? '0 2px 8px rgba(0,0,0,0.07)' : 'none',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <strong style={{ fontSize: 13, color: c.text }}>{exercise.name}</strong>
        <span style={{ fontSize: 11, color: c.textMuted }}>{open ? '▲' : '▼'}</span>
      </div>
      {open && (
        <div style={{ marginTop: 8 }}>
          <p style={{ fontSize: 13, color: c.textSec, lineHeight: 1.6, margin: 0 }}>{exercise.how}</p>
          {exercise.duration && (
            <span style={{ display: 'inline-block', marginTop: 6, fontSize: 11, background: '#dbeafe', color: '#1d4ed8', borderRadius: 4, padding: '2px 6px' }}>
              ⏱ {exercise.duration}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function SingleMusclePanel({ muscleId, mode, c }) {
  const [activeTab, setActiveTab] = useState(mode === 'worked' ? 'stretch' : 'immediate');
  const data = muscles[muscleId];
  if (!data) return null;
  const tabs = TABS[mode];
  const modeData = data[mode];

  const renderContent = () => {
    const val = modeData[activeTab];
    if (activeTab === 'rest') return (
      <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 10, padding: 14 }}>
        <p style={{ margin: 0, fontSize: 13, color: '#166534', lineHeight: 1.6 }}>{val}</p>
      </div>
    );
    if (activeTab === 'see_doctor') return (
      <div style={{ background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: 10, padding: 14 }}>
        <p style={{ margin: 0, fontSize: 13, color: '#9a3412', lineHeight: 1.6 }}>
          <strong>Consult a doctor or physio if:</strong><br />{val}
        </p>
      </div>
    );
    if (Array.isArray(val)) return val.map((ex, i) => <ExerciseCard key={i} exercise={ex} c={c} />);
    return <p style={{ fontSize: 13, color: c.textSec }}>{val}</p>;
  };

  return (
    <>
      <div style={{ padding: '12px 16px 10px', borderBottom: `1px solid ${c.border}` }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: c.text }}>{data.name}</h2>
        <p style={{ margin: '3px 0 0', fontSize: 12, color: c.textMuted }}>{data.description}</p>
        {mode === 'hurts' && (
          <div style={{ marginTop: 8 }}>
            <p style={{ fontSize: 11, fontWeight: 600, color: c.textMuted, textTransform: 'uppercase', letterSpacing: 1, margin: '0 0 5px' }}>Common causes</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {data.hurts.likely_causes.map((cause, i) => (
                <span key={i} style={{ fontSize: 11, background: '#fef3c7', color: '#92400e', borderRadius: 10, padding: '2px 8px' }}>{cause}</span>
              ))}
            </div>
          </div>
        )}
      </div>
      <div style={{ display: 'flex', borderBottom: `1px solid ${c.border}`, overflowX: 'auto', flexShrink: 0 }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)} style={{
            padding: '9px 12px', border: 'none', background: 'none', cursor: 'pointer',
            fontSize: 12, fontWeight: activeTab === t.key ? 700 : 400,
            color: activeTab === t.key ? '#f97316' : c.textMuted,
            borderBottom: `2px solid ${activeTab === t.key ? '#f97316' : 'transparent'}`,
            whiteSpace: 'nowrap',
          }}>{t.icon} {t.label}</button>
        ))}
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: 14 }}>
        {renderContent()}
      </div>
    </>
  );
}

function MultiMusclePanel({ muscleIds, mode, c }) {
  const [activeTab, setActiveTab] = useState(mode === 'worked' ? 'stretch' : 'immediate');
  const tabs = TABS[mode];

  const allItems = muscleIds.flatMap(id => {
    const d = muscles[id];
    if (!d) return [];
    const modeData = d[mode];
    const items = modeData[activeTab];
    if (!Array.isArray(items)) return [];
    return items.map(item => ({ ...item, muscle: d.name }));
  });

  return (
    <>
      <div style={{ padding: '12px 16px 10px', borderBottom: `1px solid ${c.border}` }}>
        <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: c.text }}>
          Combined Plan — {muscleIds.length} muscles
        </h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
          {muscleIds.map(id => (
            <span key={id} style={{ fontSize: 11, background: '#fed7aa', color: '#9a3412', borderRadius: 10, padding: '2px 8px', fontWeight: 600 }}>
              {muscles[id]?.name}
            </span>
          ))}
        </div>
      </div>
      <div style={{ display: 'flex', borderBottom: `1px solid ${c.border}`, overflowX: 'auto', flexShrink: 0 }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)} style={{
            padding: '9px 12px', border: 'none', background: 'none', cursor: 'pointer',
            fontSize: 12, fontWeight: activeTab === t.key ? 700 : 400,
            color: activeTab === t.key ? '#f97316' : c.textMuted,
            borderBottom: `2px solid ${activeTab === t.key ? '#f97316' : 'transparent'}`,
            whiteSpace: 'nowrap',
          }}>{t.icon} {t.label}</button>
        ))}
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: 14 }}>
        {allItems.length === 0 ? (
          <p style={{ fontSize: 13, color: c.textMuted }}>No exercises in this category for the selected muscles.</p>
        ) : (
          allItems.map((ex, i) => (
            <div key={i}>
              {(i === 0 || allItems[i - 1].muscle !== ex.muscle) && (
                <p style={{ fontSize: 10, fontWeight: 700, color: c.textMuted, textTransform: 'uppercase', letterSpacing: 1, margin: '10px 0 6px' }}>
                  {ex.muscle}
                </p>
              )}
              <ExerciseCard exercise={ex} c={c} />
            </div>
          ))
        )}
      </div>
    </>
  );
}

export default function RecommendationsPanel({ selectedMuscles, mode, onLog }) {
  const { c } = useTheme();
  const [logFlash, setLogFlash] = useState(false);

  const handleLog = () => {
    selectedMuscles.forEach(id => onLog(id, mode === 'hurts' ? 'hurt' : 'trained'));
    setLogFlash(true);
    setTimeout(() => setLogFlash(false), 1800);
  };

  if (!selectedMuscles.length) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: c.textMuted, textAlign: 'center', padding: 24 }}>
        <div style={{ fontSize: 48, marginBottom: 12 }}>👈</div>
        <p style={{ fontSize: 15, fontWeight: 600, color: c.textSec, margin: 0 }}>Select a muscle</p>
        <p style={{ fontSize: 13, marginTop: 6 }}>Click any highlighted region on the body map — or select multiple for a combined plan</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {selectedMuscles.length === 1
        ? <SingleMusclePanel muscleId={selectedMuscles[0]} mode={mode} c={c} />
        : <MultiMusclePanel muscleIds={selectedMuscles} mode={mode} c={c} />
      }

      {/* Log button */}
      <div style={{ padding: '8px 14px', borderTop: `1px solid ${c.border}`, flexShrink: 0 }}>
        <button
          onClick={handleLog}
          style={{
            width: '100%', padding: '9px 0', borderRadius: 8,
            background: logFlash ? '#4ade80' : (mode === 'hurts' ? '#fef2f2' : '#eff6ff'),
            border: `1px solid ${logFlash ? '#4ade80' : (mode === 'hurts' ? '#fecaca' : '#bfdbfe')}`,
            color: logFlash ? '#fff' : (mode === 'hurts' ? '#dc2626' : '#1d4ed8'),
            fontWeight: 600, fontSize: 13, cursor: 'pointer', transition: 'all 0.3s',
          }}
        >
          {logFlash ? '✅ Logged!' : (mode === 'hurts' ? '📝 Log this pain' : '📝 Log this session')}
        </button>
      </div>
    </div>
  );
}
