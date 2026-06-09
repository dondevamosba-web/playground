// Centralised muscle style calculator.
// Returns a getStyle(muscleId) function for use in body map SVGs.

const BASE = { cursor: 'pointer', transition: 'all 0.18s ease' };

const RECOVERY_COLORS = {
  none:       { fill: '#7eb8e8', stroke: '#2d6fa8' },
  fresh:      { fill: '#f87171', stroke: '#dc2626' },
  recovering: { fill: '#fbbf24', stroke: '#d97706' },
  ready:      { fill: '#4ade80', stroke: '#16a34a' },
};

function heatColor(t) {
  // 0 = cold blue, 0.5 = green, 1 = hot red
  if (t < 0.25) return { fill: '#93c5fd', stroke: '#3b82f6' };
  if (t < 0.5)  return { fill: '#4ade80', stroke: '#16a34a' };
  if (t < 0.75) return { fill: '#fbbf24', stroke: '#d97706' };
  return              { fill: '#f87171', stroke: '#dc2626' };
}

export function makeMuscleStyle({
  selectedMuscles = [],
  mode = 'default',       // 'default' | 'recovery' | 'heatmap' | 'search'
  recoveryMap = {},       // muscleId → 'none'|'fresh'|'recovering'|'ready'
  heatMap = {},           // muscleId → 0–1
  searchMap = {},         // muscleId → 'primary'|'secondary'
}) {
  return (id) => {
    const isSelected = selectedMuscles.includes(id);
    const anySelected = selectedMuscles.length > 0;

    if (isSelected) {
      return {
        ...BASE,
        fill: '#f97316', stroke: '#c2410c', strokeWidth: 1.8,
        opacity: 0.95,
        filter: 'drop-shadow(0 0 5px rgba(249,115,22,0.65))',
      };
    }

    if (mode === 'search') {
      const hit = searchMap[id];
      if (hit === 'primary')   return { ...BASE, fill: '#fb923c', stroke: '#c2410c', strokeWidth: 1.4, opacity: 0.9, filter: 'drop-shadow(0 0 3px rgba(251,146,60,0.5))' };
      if (hit === 'secondary') return { ...BASE, fill: '#fde68a', stroke: '#d97706', strokeWidth: 1,   opacity: 0.85, filter: 'none' };
      return { ...BASE, fill: '#7eb8e8', stroke: '#2d6fa8', strokeWidth: 0.8, opacity: 0.25, filter: 'none' };
    }

    if (mode === 'recovery') {
      const c = RECOVERY_COLORS[recoveryMap[id] || 'none'];
      return { ...BASE, ...c, strokeWidth: 0.8, opacity: 0.82, filter: 'none' };
    }

    if (mode === 'heatmap') {
      const c = heatColor(heatMap[id] || 0);
      return { ...BASE, ...c, strokeWidth: 0.8, opacity: 0.82, filter: 'none' };
    }

    // default
    return {
      ...BASE,
      fill: '#7eb8e8', stroke: '#2d6fa8', strokeWidth: 0.8,
      opacity: anySelected ? 0.35 : 0.82,
      filter: 'none',
    };
  };
}
