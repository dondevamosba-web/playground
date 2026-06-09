/* OLA Digital — Logo variations
   4 concepts × 3 background contexts (color on light, white on dark, reversed/mono)
   Each artboard renders at 600×400 in the canvas. */

const OLA_GRADIENT = "linear-gradient(90deg, #0C4A6E 0%, #0369A1 22%, #0EA5E9 50%, #06B6D4 76%, #38BDF8 100%)";

// Wave mark — three rising arcs evoking signal + ocean.
function WaveMark({ size = 64, stroke = "#0EA5E9", strokeAlt, gradientId, glow = false, neon = false }) {
  const s = size;
  const sw = s * 0.14;
  return (
    <svg width={s} height={s} viewBox="0 0 100 100" fill="none" style={{ overflow: "visible", flexShrink: 0 }}>
      {gradientId && (
        <defs>
          <linearGradient id={gradientId} x1="0" y1="50" x2="100" y2="50" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0EA5E9" />
            <stop offset="55%" stopColor="#06B6D4" />
            <stop offset="100%" stopColor="#F97316" />
          </linearGradient>
        </defs>
      )}
      {neon && (
        <defs>
          <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      )}
      <g
        filter={neon ? "url(#neonGlow)" : undefined}
        stroke={gradientId ? `url(#${gradientId})` : stroke}
        strokeWidth={sw}
        strokeLinecap="round"
        fill="none"
      >
        <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
        <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
        <path d="M8 48 Q 30 16, 50 26 T 92 14" />
      </g>
    </svg>
  );
}

// Reusable wordmark
function Wordmark({ color = "#0F172A", subColor, size = 56, tracked = false, stacked = false }) {
  const sub = subColor || color;
  if (stacked) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", lineHeight: 0.9 }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: size, color, letterSpacing: "-0.03em" }}>OLA</div>
        <div style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: size * 0.26, color: sub, letterSpacing: "0.32em", marginTop: size * 0.08 }}>
          DIGITAL
        </div>
      </div>
    );
  }
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: size * 0.22, fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <span style={{ fontWeight: 800, fontSize: size, color, letterSpacing: "-0.03em", lineHeight: 1 }}>OLA</span>
      <span
        style={{
          fontFamily: "'Inter', sans-serif",
          fontWeight: tracked ? 500 : 600,
          fontSize: tracked ? size * 0.28 : size * 0.34,
          color: sub,
          letterSpacing: tracked ? "0.42em" : "0.18em",
          textTransform: "uppercase",
          lineHeight: 1,
        }}
      >
        Digital
      </span>
    </div>
  );
}

// --- Concept 1: Neon / dark electric --------------------------------------
function LogoNeonDark() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#0A0F1E", display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
      <WaveMark size={120} stroke="#22D3EE" neon />
      <div style={{ display: "flex", alignItems: "baseline", gap: 18, filter: "drop-shadow(0 0 18px rgba(34,211,238,.55))" }}>
        <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 96, color: "#E0F2FE", letterSpacing: "-0.03em", lineHeight: 1 }}>OLA</span>
        <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 30, color: "#22D3EE", letterSpacing: "0.32em", textTransform: "uppercase" }}>Digital</span>
      </div>
    </div>
  );
}
function LogoNeonOnGrad() {
  return (
    <div style={{ width: "100%", height: "100%", background: OLA_GRADIENT, display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
      <WaveMark size={120} stroke="#FFFFFF" />
      <Wordmark color="#FFFFFF" subColor="#E0F2FE" size={84} />
    </div>
  );
}
function LogoNeonMono() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
      <WaveMark size={120} stroke="#0F172A" />
      <Wordmark color="#0F172A" subColor="#334155" size={84} />
    </div>
  );
}

// --- Concept 2: Minimal wordmark ------------------------------------------
function LogoMinimalLight() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Wordmark color="#0F172A" subColor="#0EA5E9" size={104} tracked />
    </div>
  );
}
function LogoMinimalDark() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#0A0F1E", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Wordmark color="#FFFFFF" subColor="#38BDF8" size={104} tracked />
    </div>
  );
}
function LogoMinimalReversed() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#0EA5E9", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Wordmark color="#FFFFFF" subColor="#E0F2FE" size={104} tracked />
    </div>
  );
}

// --- Concept 3: Motion / gradient -----------------------------------------
function LogoGradLight() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
      <WaveMark size={120} gradientId="g3a" />
      <Wordmark color="#0F172A" subColor="#0369A1" size={84} />
    </div>
  );
}
function LogoGradDark() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#0A0F1E", display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
      <WaveMark size={120} gradientId="g3b" />
      <Wordmark color="#FFFFFF" subColor="#38BDF8" size={84} />
    </div>
  );
}
function LogoGradReversed() {
  return (
    <div style={{ width: "100%", height: "100%", background: OLA_GRADIENT, display: "flex", alignItems: "center", justifyContent: "center", gap: 28 }}>
      <WaveMark size={120} stroke="#FFFFFF" />
      <Wordmark color="#FFFFFF" subColor="#FFFFFF" size={84} />
    </div>
  );
}

// --- Concept 4: Stacked badge ---------------------------------------------
function Badge({ bg, fg, sub, accent }) {
  return (
    <div style={{ width: "100%", height: "100%", background: bg === "grad" ? OLA_GRADIENT : bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          width: 280,
          height: 280,
          borderRadius: 56,
          background: bg === "#FFFFFF" ? "#0F172A" : bg === "#0A0F1E" ? "#0EA5E9" : "#FFFFFF",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
          boxShadow: bg === "#FFFFFF" ? "0 18px 40px -16px rgba(15,23,42,.35)" : "0 18px 40px -12px rgba(0,0,0,.35)",
        }}
      >
        <div style={{ marginBottom: 6 }}>
          <WaveMark size={64} stroke={accent} />
        </div>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 78, color: fg, letterSpacing: "-0.04em", lineHeight: 0.9 }}>OLA</div>
        <div style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 18, color: sub, letterSpacing: "0.42em" }}>DIGITAL</div>
      </div>
    </div>
  );
}
function LogoBadgeLight()   { return <Badge bg="#F0F9FF" fg="#0F172A" sub="#0EA5E9" accent="#0EA5E9" />; }
function LogoBadgeDark()    { return <Badge bg="#0A0F1E" fg="#FFFFFF" sub="#0A0F1E" accent="#0A0F1E" />; }
function LogoBadgeOnGrad()  { return <Badge bg="grad"    fg="#0F172A" sub="#0EA5E9" accent="#0EA5E9" />; }

Object.assign(window, {
  WaveMark, Wordmark, OLA_GRADIENT,
  LogoNeonDark, LogoNeonOnGrad, LogoNeonMono,
  LogoMinimalLight, LogoMinimalDark, LogoMinimalReversed,
  LogoGradLight, LogoGradDark, LogoGradReversed,
  LogoBadgeLight, LogoBadgeDark, LogoBadgeOnGrad,
});
