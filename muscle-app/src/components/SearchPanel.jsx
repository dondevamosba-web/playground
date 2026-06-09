import { useState, useMemo } from 'react';
import { exercises, exercisesByCategory } from '../data/exercises';
import { muscles } from '../data/muscles';
import { useTheme } from '../context/ThemeContext';

const CATEGORY_ICONS = {
  chest: '🫁', back: '🔙', shoulders: '🏋️', arms: '💪',
  legs: '🦵', core: '⚡', full_body: '🔥',
};

export default function SearchPanel({ onHighlight }) {
  const { c } = useTheme();
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return exercises.filter(e =>
      e.name.toLowerCase().includes(q) ||
      e.category.includes(q) ||
      e.primary.some(id => muscles[id]?.name.toLowerCase().includes(q))
    ).slice(0, 12);
  }, [query]);

  const selectExercise = (ex) => {
    setSelected(ex);
    const map = {};
    ex.primary.forEach(id => { map[id] = 'primary'; });
    ex.secondary.forEach(id => { if (!map[id]) map[id] = 'secondary'; });
    onHighlight(map);
  };

  const clear = () => { setSelected(null); setQuery(''); onHighlight({}); };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Search input */}
      <div style={{ padding: '14px 16px 10px', borderBottom: `1px solid ${c.border}` }}>
        <div style={{ position: 'relative' }}>
          <span style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', fontSize: 14, opacity: 0.5 }}>🔍</span>
          <input
            autoFocus
            value={query}
            onChange={e => { setQuery(e.target.value); if (selected) { setSelected(null); onHighlight({}); } }}
            placeholder="Search exercise (e.g. bench press, squat…)"
            style={{
              width: '100%', padding: '9px 32px 9px 32px', borderRadius: 8,
              border: `1px solid ${c.border}`, background: c.inputBg, color: c.text,
              fontSize: 13, outline: 'none', boxSizing: 'border-box',
            }}
          />
          {query && (
            <button onClick={clear} style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: c.textMuted, fontSize: 16 }}>×</button>
          )}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 16px' }}>
        {/* Selected exercise detail */}
        {selected && (
          <div style={{ marginBottom: 14, background: c.card, border: `1px solid ${c.cardBorder}`, borderRadius: 10, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: c.text }}>{selected.name}</h3>
                <span style={{ fontSize: 11, color: c.textMuted, textTransform: 'capitalize' }}>{CATEGORY_ICONS[selected.category]} {selected.category.replace('_', ' ')}</span>
              </div>
              <button onClick={clear} style={{ background: 'none', border: 'none', cursor: 'pointer', color: c.textMuted, fontSize: 18 }}>×</button>
            </div>
            <p style={{ margin: '8px 0 10px', fontSize: 13, color: c.textSec, lineHeight: 1.5 }}>💡 {selected.tips}</p>
            <div style={{ marginBottom: 6 }}>
              <p style={{ margin: '0 0 4px', fontSize: 11, fontWeight: 600, color: c.textMuted, textTransform: 'uppercase', letterSpacing: 0.8 }}>Primary muscles</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {selected.primary.map(id => (
                  <span key={id} style={{ fontSize: 11, background: '#fed7aa', color: '#9a3412', borderRadius: 10, padding: '2px 8px', fontWeight: 600 }}>
                    {muscles[id]?.name || id}
                  </span>
                ))}
              </div>
            </div>
            {selected.secondary.length > 0 && (
              <div>
                <p style={{ margin: '6px 0 4px', fontSize: 11, fontWeight: 600, color: c.textMuted, textTransform: 'uppercase', letterSpacing: 0.8 }}>Secondary</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {selected.secondary.map(id => (
                    <span key={id} style={{ fontSize: 11, background: '#fef9c3', color: '#854d0e', borderRadius: 10, padding: '2px 8px' }}>
                      {muscles[id]?.name || id}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <p style={{ margin: '10px 0 0', fontSize: 11, color: c.textMuted }}>← Body map shows highlighted muscles</p>
          </div>
        )}

        {/* Search results */}
        {results.length > 0 && !selected && (
          <div>
            {results.map(ex => (
              <button
                key={ex.id}
                onClick={() => selectExercise(ex)}
                style={{
                  width: '100%', textAlign: 'left', background: c.card,
                  border: `1px solid ${c.cardBorder}`, borderRadius: 8, padding: '10px 12px',
                  marginBottom: 6, cursor: 'pointer', color: c.text,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 14, fontWeight: 600 }}>{ex.name}</span>
                  <span style={{ fontSize: 10, color: c.textMuted, textTransform: 'capitalize' }}>{CATEGORY_ICONS[ex.category]} {ex.category.replace('_', ' ')}</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 3, marginTop: 4 }}>
                  {ex.primary.map(id => (
                    <span key={id} style={{ fontSize: 10, background: '#fef3c7', color: '#92400e', borderRadius: 8, padding: '1px 6px' }}>
                      {muscles[id]?.name || id}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Browse by category */}
        {!query && !selected && (
          <div>
            <p style={{ margin: '0 0 10px', fontSize: 11, fontWeight: 600, color: c.textMuted, textTransform: 'uppercase', letterSpacing: 1 }}>Browse by category</p>
            {Object.entries(exercisesByCategory).map(([cat, exs]) => (
              <div key={cat} style={{ marginBottom: 14 }}>
                <p style={{ margin: '0 0 6px', fontSize: 12, fontWeight: 700, color: c.textSec }}>
                  {CATEGORY_ICONS[cat]} {cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                  {exs.map(ex => (
                    <button
                      key={ex.id}
                      onClick={() => { setQuery(ex.name); selectExercise(ex); }}
                      style={{
                        fontSize: 11, padding: '4px 10px', borderRadius: 14,
                        border: `1px solid ${c.border}`, background: c.inputBg,
                        cursor: 'pointer', color: c.textSec,
                      }}
                    >
                      {ex.name}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {query && results.length === 0 && (
          <p style={{ textAlign: 'center', color: c.textMuted, fontSize: 13, marginTop: 32 }}>No exercises found for "{query}"</p>
        )}
      </div>
    </div>
  );
}
