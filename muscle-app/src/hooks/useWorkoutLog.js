import { useState, useCallback } from 'react';

const KEY = 'musclemate_log';

function load() {
  try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; }
}

function save(log) {
  try { localStorage.setItem(KEY, JSON.stringify(log)); } catch {}
}

// Returns recovery status for a muscle based on its most recent 'trained' entry
export function getRecoveryStatus(muscleId, log) {
  const entries = log
    .filter(e => e.muscleId === muscleId && e.type === 'trained')
    .sort((a, b) => b.ts - a.ts);
  if (!entries.length) return 'none';
  const h = (Date.now() - entries[0].ts) / 3_600_000;
  if (h < 24) return 'fresh';
  if (h < 48) return 'recovering';
  return 'ready';
}

// Returns 0–1 training intensity over the last `days` days (for heatmap)
export function getTrainingIntensity(muscleId, log, days = 30) {
  const since = Date.now() - days * 86_400_000;
  const count = log.filter(e => e.muscleId === muscleId && e.type === 'trained' && e.ts > since).length;
  // normalise: assume 3+ sessions in period = "high"
  return Math.min(count / 3, 1);
}

export function useWorkoutLog() {
  const [log, setLog] = useState(load);

  const addEntry = useCallback((muscleId, type = 'trained') => {
    setLog(prev => {
      const next = [{ muscleId, type, ts: Date.now() }, ...prev];
      save(next);
      return next;
    });
  }, []);

  const removeEntry = useCallback((idx) => {
    setLog(prev => {
      const next = prev.filter((_, i) => i !== idx);
      save(next);
      return next;
    });
  }, []);

  const clearLog = useCallback(() => {
    setLog([]);
    save([]);
  }, []);

  return { log, addEntry, removeEntry, clearLog };
}
