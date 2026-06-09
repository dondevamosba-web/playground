import { useState, useMemo } from 'react';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import BodyRotator from './components/BodyRotator';
import RecommendationsPanel from './components/RecommendationsPanel';
import SearchPanel from './components/SearchPanel';
import WarmupPanel from './components/WarmupPanel';
import StatsPanel from './components/StatsPanel';
import { muscles } from './data/muscles';
import { makeMuscleStyle } from './utils/muscleColors';
import { useWorkoutLog, getRecoveryStatus, getTrainingIntensity } from './hooks/useWorkoutLog';

const MODES = [
  { key: 'trained', label: 'Trained',  icon: '🏋️', desc: 'post-workout · stretch · strengthen' },
  { key: 'hurts',   label: 'Hurts',    icon: '🤕', desc: 'pain · relief · recovery' },
  { key: 'search',  label: 'Search',   icon: '🔍', desc: 'exercise → muscles' },
  { key: 'warmup',  label: 'Warm-up',  icon: '🔥', desc: 'pre-workout routine' },
  { key: 'stats',   label: 'Stats',    icon: '📊', desc: 'imbalances · history' },
];

// Recovery legend colors
const RECOVERY_COLORS = {
  none:       { dot: '#7eb8e8', label: 'Not logged' },
  fresh:      { dot: '#f87171', label: 'Just trained (<24h)' },
  recovering: { dot: '#fbbf24', label: 'Recovering (24–48h)' },
  ready:      { dot: '#4ade80', label: 'Ready to train' },
};

function AppInner() {
  const { c, isDark, toggle } = useTheme();
  const [selectedMuscles, setSelectedMuscles] = useState([]);
  const [mode, setMode] = useState('trained');
  const [searchMap, setSearchMap] = useState({});    // muscleId → 'primary'|'secondary'
  const { log, addEntry, clearLog } = useWorkoutLog();

  const handleSelect = (id) => {
    setSelectedMuscles(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleModeChange = (key) => {
    setMode(key);
    setSelectedMuscles([]);
    if (key !== 'search') setSearchMap({});
  };

  // Body map color mode
  const bodyColorMode = useMemo(() => {
    if (mode === 'search') return 'search';
    if (mode === 'stats') return 'heatmap';
    // trained/hurts/warmup: show recovery colors when nothing selected
    return selectedMuscles.length === 0 ? 'recovery' : 'default';
  }, [mode, selectedMuscles]);

  // Build recovery + heat maps
  const recoveryMap = useMemo(() =>
    Object.fromEntries(Object.keys(muscles).map(id => [id, getRecoveryStatus(id, log)])),
    [log]
  );

  const heatMap = useMemo(() =>
    Object.fromEntries(Object.keys(muscles).map(id => [id, getTrainingIntensity(id, log, 30)])),
    [log]
  );

  const getStyle = useMemo(() =>
    makeMuscleStyle({ selectedMuscles, mode: bodyColorMode, recoveryMap, heatMap, searchMap }),
    [selectedMuscles, bodyColorMode, recoveryMap, heatMap, searchMap]
  );

  const modeInfo = MODES.find(m => m.key === mode);

  // Sidebar bg adapts to mode
  const sideBg = isDark ? c.surface : '#fff';

  return (
    <div style={{ display: 'flex', height: '100dvh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', background: c.bg, overflow: 'hidden' }}>

      {/* ── LEFT PANEL ── */}
      <div style={{ width: 300, minWidth: 260, background: sideBg, borderRight: `1px solid ${c.border}`, display: 'flex', flexDirection: 'column', flexShrink: 0 }}>

        {/* Header */}
        <div style={{ padding: '16px 16px 10px', borderBottom: `1px solid ${c.borderLight}`, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 17, fontWeight: 800, color: c.text, letterSpacing: -0.5 }}>💪 MuscleMate</h1>
            <p style={{ margin: '2px 0 0', fontSize: 11, color: c.textMuted }}>
              {mode === 'stats' || bodyColorMode === 'recovery' ? 'Recovery heatmap active' : 'Click muscles to select'}
            </p>
          </div>
          <button onClick={toggle} style={{ background: 'none', border: `1px solid ${c.border}`, borderRadius: 8, padding: '5px 8px', cursor: 'pointer', fontSize: 14, color: c.textSec }}>
            {isDark ? '☀️' : '🌙'}
          </button>
        </div>

        {/* Mode toggle */}
        <div style={{ padding: '10px 12px', borderBottom: `1px solid ${c.borderLight}` }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 3 }}>
            {MODES.map(m => (
              <button
                key={m.key}
                onClick={() => handleModeChange(m.key)}
                title={m.desc}
                style={{
                  padding: '6px 0', borderRadius: 6, border: `1px solid ${mode === m.key ? '#6366f1' : c.border}`,
                  background: mode === m.key ? '#eef2ff' : c.inputBg,
                  cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1,
                }}
              >
                <span style={{ fontSize: 14 }}>{m.icon}</span>
                <span style={{ fontSize: 9, color: mode === m.key ? '#6366f1' : c.textMuted, fontWeight: mode === m.key ? 700 : 400 }}>{m.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 3D rotating body map */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <BodyRotator getStyle={getStyle} onSelect={handleSelect} />
        </div>

        {/* Recovery legend (when in recovery mode) */}
        {(bodyColorMode === 'recovery' || mode === 'stats') && (
          <div style={{ padding: '6px 12px', borderTop: `1px solid ${c.borderLight}` }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px 10px' }}>
              {Object.entries(RECOVERY_COLORS).map(([key, { dot, label }]) => (
                <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: 7, height: 7, borderRadius: '50%', background: dot }} />
                  <span style={{ fontSize: 9, color: c.textMuted }}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Selected muscle chips */}
        <div style={{ padding: '6px 12px 8px', borderTop: `1px solid ${c.borderLight}`, minHeight: 38 }}>
          {selectedMuscles.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
              {selectedMuscles.map(id => (
                <button
                  key={id}
                  onClick={() => handleSelect(id)}
                  style={{
                    fontSize: 10, padding: '3px 8px', borderRadius: 10, border: '1px solid #fed7aa',
                    background: '#fff7ed', color: '#c2410c', cursor: 'pointer', fontWeight: 600,
                    display: 'flex', alignItems: 'center', gap: 3,
                  }}
                >
                  {muscles[id]?.name} <span style={{ opacity: 0.5 }}>×</span>
                </button>
              ))}
              <button onClick={() => setSelectedMuscles([])} style={{ fontSize: 10, color: c.textMuted, background: 'none', border: 'none', cursor: 'pointer', padding: '2px 4px' }}>
                Clear
              </button>
            </div>
          ) : (
            <span style={{ fontSize: 11, color: c.textFaint }}>
              {mode === 'stats' ? 'Showing last 30d heatmap' : 'No muscles selected'}
            </span>
          )}
        </div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', minWidth: 0 }}>

        {/* Mode banner */}
        <div style={{
          padding: '10px 20px', borderBottom: `1px solid ${c.border}`, background: c.surface,
          display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0,
        }}>
          <span style={{ fontSize: 16 }}>{modeInfo.icon}</span>
          <span style={{ fontSize: 13, fontWeight: 700, color: c.text }}>{modeInfo.label}</span>
          <span style={{ fontSize: 12, color: c.textMuted }}>— {modeInfo.desc}</span>
        </div>

        {/* Panel content */}
        <div style={{ flex: 1, overflow: 'hidden', background: c.surface }}>
          {mode === 'search'  && <SearchPanel onHighlight={setSearchMap} />}
          {mode === 'warmup'  && <WarmupPanel selectedMuscles={selectedMuscles} />}
          {mode === 'stats'   && <StatsPanel log={log} onClear={clearLog} />}
          {(mode === 'trained' || mode === 'hurts') && (
            <RecommendationsPanel
              selectedMuscles={selectedMuscles}
              mode={mode === 'trained' ? 'worked' : 'hurts'}
              onLog={addEntry}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppInner />
    </ThemeProvider>
  );
}
