import { createContext, useContext, useState, useEffect } from 'react';

const light = {
  bg: '#f8fafc',
  surface: '#ffffff',
  surfaceAlt: '#f1f5f9',
  border: '#e2e8f0',
  borderLight: '#f1f5f9',
  text: '#0f172a',
  textSec: '#475569',
  textMuted: '#94a3b8',
  textFaint: '#cbd5e1',
  card: '#f8fafc',
  cardBorder: '#e2e8f0',
  inputBg: '#f1f5f9',
  scrollbar: '#e2e8f0',
};

const dark = {
  bg: '#0f172a',
  surface: '#1e293b',
  surfaceAlt: '#0f172a',
  border: '#334155',
  borderLight: '#1e293b',
  text: '#f1f5f9',
  textSec: '#94a3b8',
  textMuted: '#64748b',
  textFaint: '#334155',
  card: '#1e293b',
  cardBorder: '#334155',
  inputBg: '#0f172a',
  scrollbar: '#334155',
};

const ThemeCtx = createContext({ isDark: false, c: light, toggle: () => {} });

export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    try { return localStorage.getItem('theme') === 'dark'; } catch { return false; }
  });

  useEffect(() => {
    try { localStorage.setItem('theme', isDark ? 'dark' : 'light'); } catch {}
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <ThemeCtx.Provider value={{ isDark, c: isDark ? dark : light, toggle: () => setIsDark(d => !d) }}>
      {children}
    </ThemeCtx.Provider>
  );
}

export const useTheme = () => useContext(ThemeCtx);
