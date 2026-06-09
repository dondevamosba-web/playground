/* OLA Digital — June Series
   33 pieces · 1080×1080 · #0F172A navy · #0EA5E9 blue · #F97316 orange
   9 single posts (A–I) + 6 carousels × 4 slides (24)

   Hard rules applied to every piece:
   - Background #0F172A (no gradients on these — flat)
   - Body text white, highlights in blue or orange
   - "OLA DIGITAL" wordmark bottom-right (small)
   - WhatsApp CTA on every piece
*/

const J = {
  bg: "#0F172A",
  blue: "#0EA5E9",
  blueLite: "#7DD3FC",
  orange: "#F97316",
  orangeLite: "#FDBA74",
  white: "#FFFFFF",
  muted: "#94A3B8",
  faint: "#1E293B",
  ink: "#0A0F1E",
  greenWA: "#22C55E",
};

// Small bottom-right wordmark — fixed position across the series
function JLogo({ caso, location, side = "right" }) {
  return (
    <div style={{
      position: "absolute", bottom: 36, right: side === "right" ? 44 : "auto", left: side === "left" ? 44 : "auto",
      display: "flex", alignItems: "center", gap: 10,
      fontFamily: "'Inter', sans-serif",
    }}>
      <svg width="22" height="22" viewBox="0 0 100 100">
        <g stroke={J.blue} strokeWidth="16" strokeLinecap="round" fill="none">
          <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.7" />
          <path d="M8 48 Q 30 16, 50 26 T 92 14" />
        </g>
      </svg>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 18, color: J.white, letterSpacing: "-0.01em" }}>OLA</span>
        <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 10, color: J.blueLite, letterSpacing: "0.32em" }}>DIGITAL</span>
        {(caso || location) && (
          <span style={{ marginLeft: 8, paddingLeft: 8, borderLeft: `1px solid ${J.faint}`, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 10, color: J.muted, letterSpacing: "0.16em" }}>
            {[caso, location].filter(Boolean).join(" · ").toUpperCase()}
          </span>
        )}
      </div>
    </div>
  );
}

// WhatsApp CTA pill — small, bottom-left
function JCTA({ label = "Escribinos por WhatsApp", side = "left", variant = "solid" }) {
  const solid = variant === "solid";
  return (
    <div style={{
      position: "absolute", bottom: 32, left: side === "left" ? 44 : "auto", right: side === "right" ? 44 : "auto",
      display: "inline-flex", alignItems: "center", gap: 10,
      background: solid ? J.orange : "transparent",
      border: solid ? "none" : `1.5px solid ${J.orange}`,
      color: solid ? J.white : J.orange,
      padding: "10px 18px", borderRadius: 999,
      fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 16,
      letterSpacing: "-0.01em",
      boxShadow: solid ? `0 10px 28px -10px rgba(249,115,22,.55)` : "none",
    }}>
      <svg width="18" height="18" viewBox="0 0 32 32" fill={solid ? J.white : J.orange}>
        <path d="M16 3C9 3 3.4 8.6 3.4 15.6c0 2.3.6 4.5 1.7 6.4L3 29l7.2-2c1.8 1 3.8 1.5 5.9 1.5 7 0 12.6-5.6 12.6-12.6S23 3 16 3z" />
      </svg>
      {label}
    </div>
  );
}

// Section frame — flat dark navy, with a hairline corner grid for visual structure
function JFrame({ children, accent }) {
  return (
    <div style={{
      width: 1080, height: 1080, position: "relative", overflow: "hidden",
      background: J.bg, color: J.white, fontFamily: "'Inter', sans-serif",
    }}>
      {/* hairline frame */}
      <div style={{ position: "absolute", inset: 32, border: `1px solid ${J.faint}`, borderRadius: 0, pointerEvents: "none" }}></div>
      {/* corner accents */}
      <div style={{ position: "absolute", top: 32, left: 32, width: 60, height: 2, background: accent || J.blue }}></div>
      <div style={{ position: "absolute", top: 32, left: 32, width: 2, height: 60, background: accent || J.blue }}></div>
      {children}
    </div>
  );
}

// Small dot for ornament
const Dot = ({ c }) => <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: 999, background: c }}></span>;

// Tiny labels used at top of posts
function JEyebrow({ children, color = J.blue }) {
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 10, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color, letterSpacing: "0.22em", textTransform: "uppercase" }}>
      <Dot c={color} />
      {children}
    </div>
  );
}

// ─── small icon set used inline ───────────────────────────────────────
const Ico = {
  Pin: ({ c = J.blue, s = 64 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-7 8-13a8 8 0 1 0-16 0c0 6 8 13 8 13z" /><circle cx="12" cy="9" r="3" />
    </svg>
  ),
  Play: ({ c = J.blue, s = 64 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><polygon points="10,8 16,12 10,16" fill={c} stroke="none" />
    </svg>
  ),
  Store: ({ c = J.blue, s = 64, muted }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={muted ? "#475569" : c} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l2-5h14l2 5" /><path d="M3 9v11h18V9" /><path d="M9 20v-6h6v6" />
    </svg>
  ),
  Cal: ({ c = J.blue, s = 64, full }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 9h18M8 3v4M16 3v4" />
      {full && [...Array(9)].map((_, i) => <rect key={i} x={5 + (i%3)*5} y={11 + Math.floor(i/3)*3} width="3" height="2" fill={c} stroke="none" />)}
    </svg>
  ),
  X: ({ c = J.orange, s = 36 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.4" strokeLinecap="round"><path d="M5 5l14 14M19 5L5 19" /></svg>
  ),
  Check: ({ c = J.blue, s = 28 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"><polyline points="4,12 10,18 20,6" /></svg>
  ),
};

// ════════════════════════════════════════════════════════════════════════
// SINGLE POSTS A – I
// ════════════════════════════════════════════════════════════════════════

// POST A — "De 2 a 15 reservas"
function PostA() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>CASO REAL · OLAVARRÍA</JEyebrow>
      </div>

      {/* central stat */}
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 48 }}>
        <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 20, color: J.muted, letterSpacing: "0.18em", textTransform: "uppercase" }}>en 90 días pasamos de</div>

        <div style={{ display: "flex", alignItems: "center", gap: 64, position: "relative" }}>
          {/* left number */}
          <div style={{ textAlign: "center" }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 280, color: J.white, lineHeight: 0.85, letterSpacing: "-0.06em", opacity: 0.35 }}>2</div>
            <div style={{ marginTop: 8, fontSize: 22, color: J.muted, fontWeight: 600 }}>consultas / mes</div>
          </div>

          {/* arrow */}
          <svg width="100" height="60" viewBox="0 0 100 60" fill="none">
            <path d="M6 30 L86 30" stroke={J.orange} strokeWidth="4" strokeLinecap="round" />
            <path d="M74 14 L92 30 L74 46" stroke={J.orange} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>

          {/* right number */}
          <div style={{ textAlign: "center" }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 360, color: J.blue, lineHeight: 0.85, letterSpacing: "-0.06em", textShadow: `0 0 60px ${J.blue}66` }}>15</div>
            <div style={{ marginTop: 8, fontSize: 22, color: J.blueLite, fontWeight: 600 }}>reservas / mes</div>
          </div>
        </div>

        <div style={{ width: 320, height: 1, background: J.faint }}></div>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 28, color: J.white, textAlign: "center", maxWidth: 720, letterSpacing: "-0.015em" }}>
          Una panadería del centro. Mismo equipo. Otra estrategia.
        </div>
      </div>

      <JCTA />
      <JLogo caso="Caso real" location="Olavarría" />
    </JFrame>
  );
}

// POST B — Google My Business 8/10
function PostB() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", alignItems: "center", gap: 16 }}>
        <Ico.Pin s={48} />
        <JEyebrow>GOOGLE MAPS · TIP</JEyebrow>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "200px 80px 180px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 32 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 96, lineHeight: 0.96, letterSpacing: "-0.035em", margin: 0, color: J.white }}>
          <span style={{ color: J.orange }}>8 de cada 10</span><br />pymes pierden<br />clientes en<br />Google Maps.
        </h1>

        <div style={{ display: "flex", alignItems: "center", gap: 18, paddingTop: 24, borderTop: `1px solid ${J.faint}`, maxWidth: 820 }}>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 56, color: J.blue, letterSpacing: "-0.03em" }}>20'</div>
          <div style={{ fontSize: 22, color: J.muted, lineHeight: 1.35 }}>
            <span style={{ color: J.white, fontWeight: 600 }}>Veinte minutos.</span> Eso es todo lo que lleva arreglarlo.
          </div>
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// POST C — "89%"
function PostC() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>DATO · SEO LOCAL</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 140, left: 60, right: 60, bottom: 280, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 640,
          color: J.blue, lineHeight: 0.78, letterSpacing: "-0.08em",
          textShadow: `0 0 80px ${J.blue}55`,
        }}>89%</div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 180 }}>
        <div style={{ width: 80, height: 4, background: J.orange, marginBottom: 22 }}></div>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 34, color: J.white, lineHeight: 1.2, letterSpacing: "-0.015em", maxWidth: 820 }}>
          de búsquedas locales que no te encuentran van directo a <span style={{ color: J.orange }}>tu competencia</span>.
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// POST D — Reels al público correcto
function PostD() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", alignItems: "center", gap: 16 }}>
        <Ico.Play s={48} />
        <JEyebrow>REELS · TARGETING</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 180, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 80, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Los reels<br />funcionan.<br />Pero solo si llegan al <span style={{ color: J.blue }}>público correcto</span>.
        </h1>
      </div>

      {/* two-column comparison */}
      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ border: `1px solid ${J.faint}`, borderRadius: 14, padding: 22, opacity: 0.7 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 14, color: J.muted, letterSpacing: "0.18em", textTransform: "uppercase", fontWeight: 600 }}>
            <Ico.X s={20} c="#475569" /> AL VOLEO
          </div>
          <div style={{ marginTop: 12, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 22, color: J.muted, lineHeight: 1.2 }}>
            70k vistas.<br />0 clientes.
          </div>
        </div>
        <div style={{ background: "rgba(14,165,233,.08)", border: `1px solid ${J.blue}`, borderRadius: 14, padding: 22 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 14, color: J.blueLite, letterSpacing: "0.18em", textTransform: "uppercase", fontWeight: 600 }}>
            <Ico.Check s={20} /> AL PÚBLICO REAL
          </div>
          <div style={{ marginTop: 12, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 22, color: J.white, lineHeight: 1.2 }}>
            3k vistas.<br /><span style={{ color: J.blue }}>+22 consultas.</span>
          </div>
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// POST E — Tu perfil = tu vidriera
function PostE() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>INSTAGRAM · PERFIL</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 180, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 80, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Tu perfil de Instagram es la <span style={{ color: J.blue }}>vidriera</span> de tu negocio.
        </h1>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ border: `1px solid ${J.faint}`, borderRadius: 14, padding: 28, opacity: 0.65, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: 16 }}>
          <div style={{ filter: "blur(2.2px)" }}><Ico.Store s={72} c="#475569" muted /></div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.muted, letterSpacing: "0.18em" }}>SIN OPTIMIZAR</div>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 22, color: J.muted }}>Pasan y no entran</div>
        </div>
        <div style={{ background: "rgba(14,165,233,.08)", border: `1px solid ${J.blue}`, borderRadius: 14, padding: 28, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: 16 }}>
          <Ico.Store s={72} c={J.blue} />
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.blueLite, letterSpacing: "0.18em" }}>CON OLA DIGITAL</div>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 22, color: J.white }}>Entran y compran</div>
        </div>
      </div>

      <JCTA label="Escribinos" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// POST F — "87%"
function PostF() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>DATO · INTENCIÓN DE COMPRA</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 160, left: 0, right: 0, bottom: 320, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 580, color: J.blue,
          lineHeight: 0.8, letterSpacing: "-0.08em", textShadow: `0 0 100px ${J.blue}66, 0 0 30px ${J.blue}33`,
        }}>87%</div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200 }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 30, color: J.white, lineHeight: 1.3, letterSpacing: "-0.015em" }}>
          de búsquedas locales terminan en compra en menos de <span style={{ color: J.orange, borderBottom: `3px solid ${J.orange}`, paddingBottom: 2 }}>7 días</span>.
        </div>
        <div style={{ marginTop: 16, fontFamily: "'Inter', sans-serif", fontSize: 18, color: J.muted, fontStyle: "italic" }}>
          ¿Aparecés cuando te buscan?
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// POST G — De cero a agenda llena
function PostG() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>CASO REAL · AGENDA</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          De cero presencia<br />a llenar la agenda<br />de <span style={{ color: J.blue }}>consultas.</span>
        </h1>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 220, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
        <div style={{ border: `1px solid ${J.faint}`, borderRadius: 16, padding: "24px 28px", flex: 1 }}>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.muted, letterSpacing: "0.18em" }}>ANTES</div>
          <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 14 }}>
            <Ico.Cal s={56} c="#475569" />
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 24, color: J.muted, lineHeight: 1.1 }}>Calendario<br />vacío</div>
          </div>
        </div>

        <svg width="80" height="40" viewBox="0 0 80 40" fill="none">
          <path d="M4 20 L66 20" stroke={J.orange} strokeWidth="4" strokeLinecap="round" />
          <path d="M54 8 L72 20 L54 32" stroke={J.orange} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>

        <div style={{ background: "rgba(14,165,233,.10)", border: `1px solid ${J.blue}`, borderRadius: 16, padding: "24px 28px", flex: 1 }}>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.blueLite, letterSpacing: "0.18em" }}>DESPUÉS</div>
          <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 14 }}>
            <Ico.Cal s={56} c={J.blue} full />
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 24, color: J.white, lineHeight: 1.1 }}>Agenda<br />llena</div>
          </div>
        </div>
      </div>

      <JCTA />
      <JLogo caso="Caso real" location="Olavarría" />
    </JFrame>
  );
}

// POST H — Consistencia tip
function PostH() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>INSTAGRAM · ESTRATEGIA</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          ¿No ves resultados<br />en <span style={{ color: J.blue }}>Instagram?</span>
        </h1>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 470, display: "flex", flexDirection: "column", gap: 22 }}>
        {[
          { n: "01", t: "Publicá 3-4 veces por semana", s: "La consistencia le gana al algoritmo." },
          { n: "02", t: "En los horarios en que tu cliente está online", s: "Mediodía o después de las 20hs en Olavarría." },
          { n: "03", t: "Hablale a UNA persona, no a todos", s: "Hablar para todos = nadie te escucha." },
        ].map(r => (
          <div key={r.n} style={{ display: "flex", alignItems: "flex-start", gap: 20, paddingBottom: 18, borderBottom: `1px solid ${J.faint}` }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 44, color: J.blue, letterSpacing: "-0.03em", minWidth: 70 }}>{r.n}</div>
            <div>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 28, color: J.white, lineHeight: 1.15, letterSpacing: "-0.01em" }}>{r.t}</div>
              <div style={{ marginTop: 6, fontSize: 17, color: J.muted }}>{r.s}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ position: "absolute", bottom: 110, left: 80, right: 80, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 22, color: J.orange, letterSpacing: "-0.01em" }}>
        Así se construye. Así se vende.
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// POST I — Cierre dramático
function PostI() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>DATO FINAL</JEyebrow>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "200px 80px 200px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 36 }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 320, color: J.blue, lineHeight: 0.7, letterSpacing: "-0.06em", marginLeft: -20, opacity: 0.7 }}>“</div>

        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, color: J.white, lineHeight: 1.05, letterSpacing: "-0.025em", marginTop: -120 }}>
          Cada cliente que no te encuentra online…
        </div>

        <div style={{ width: 80, height: 3, background: J.blue }}></div>

        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, color: J.white, lineHeight: 1.05, letterSpacing: "-0.025em" }}>
          …<span style={{ color: J.orange }}>tu competencia</span> se lo lleva.
        </div>

        <div style={{ marginTop: 24, fontFamily: "'Inter', sans-serif", fontSize: 20, color: J.muted, fontStyle: "italic" }}>
          Pasa todos los días. En silencio.
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// CAROUSELS — shared interior + CTA templates
// ════════════════════════════════════════════════════════════════════════

// Generic interior slide for numbered carousels
function JInterior({ num, numColor = J.blue, title, body, slideNum }) {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 240, lineHeight: 0.85, letterSpacing: "-0.06em", color: numColor }}>{num}</div>
        </div>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>
          {String(slideNum).padStart(2,"0")} / 04
        </div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 460 }}>
        <div style={{ width: 80, height: 3, background: numColor, marginBottom: 24 }}></div>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 74, lineHeight: 1.02, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          {title}
        </h2>
        <div style={{ marginTop: 28, fontSize: 30, color: J.muted, lineHeight: 1.4, maxWidth: 860 }}>
          {body}
        </div>
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// Generic CTA slide
function JCTASlide({ headline, subline, badge = "Diagnóstico gratis", slideNum = 4, showWA = true, accent = J.blue }) {
  return (
    <JFrame accent={accent}>
      {/* center glow */}
      <div style={{ position: "absolute", inset: 32, background: `radial-gradient(ellipse 60% 50% at 50% 55%, ${accent}22 0%, transparent 60%)` }}></div>

      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <JEyebrow color={accent === J.blue ? J.blue : J.orange}>PASO SIGUIENTE</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>{String(slideNum).padStart(2,"0")} / 04</div>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "200px 80px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center", gap: 36 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white, maxWidth: 880 }}>
          {headline}
        </h1>
        <div style={{ width: 120, height: 3, background: accent }}></div>
        <div style={{ fontSize: 26, color: J.muted, lineHeight: 1.4, maxWidth: 760 }}>{subline}</div>

        {showWA && (
          <div style={{ display: "inline-flex", alignItems: "center", gap: 12, background: J.orange, color: J.white, padding: "20px 32px", borderRadius: 999, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 24, marginTop: 16, boxShadow: `0 20px 50px -12px rgba(249,115,22,.6)`, letterSpacing: "-0.01em" }}>
            <svg width="26" height="26" viewBox="0 0 32 32" fill={J.white}>
              <path d="M16 3C9 3 3.4 8.6 3.4 15.6c0 2.3.6 4.5 1.7 6.4L3 29l7.2-2c1.8 1 3.8 1.5 5.9 1.5 7 0 12.6-5.6 12.6-12.6S23 3 16 3z" />
            </svg>
            Escribinos por WhatsApp
          </div>
        )}

        {badge && (
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.blueLite, letterSpacing: "0.18em", textTransform: "uppercase" }}>
            → {badge}
          </div>
        )}
      </div>

      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ────────────────────────────────────────────────────────────────────────
// CAROUSEL 1 · "5 pasos para vender en redes"
function C1S1() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>GUÍA · INSTAGRAM</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>01 / 04</div>
      </div>

      {/* watermark 5 */}
      <div style={{ position: "absolute", right: -40, top: 100, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 1100, color: J.blue, opacity: 0.12, lineHeight: 0.8, letterSpacing: "-0.08em" }}>5</div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 92, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0, color: J.white }}>
          5 pasos para que<br />tu negocio venda<br />en <span style={{ color: J.blue }}>redes</span>.
        </h1>
        <div style={{ marginTop: 24, fontSize: 22, color: J.muted }}>Guardalo — lo vas a necesitar.</div>
      </div>

      <div style={{ position: "absolute", bottom: 36, right: 220, display: "inline-flex", alignItems: "center", gap: 10, color: J.orange, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 18 }}>
        deslizá <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 28, height: 28, borderRadius: 999, background: J.orange, color: J.white }}>→</span>
      </div>
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
const C1S2 = () => <JInterior num="01" numColor={J.blue}   slideNum={2} title={<>Elegí la <span style={{ color: J.blue }}>plataforma</span> correcta.</>} body="No estés en todas. Estás donde está tu cliente." />;
const C1S3 = () => <JInterior num="02" numColor={J.orange} slideNum={3} title={<>Definí a <span style={{ color: J.orange }}>quién le hablás</span>.</>} body="Un mensaje para todos no le llega a nadie." />;
const C1S4 = () => <JCTASlide headline={<>¿Querés que lo hagamos <span style={{ color: J.blue }}>por vos</span>?</>} subline="Escribinos por WhatsApp y armamos tu plan." badge="Diagnóstico gratis" />;

// ────────────────────────────────────────────────────────────────────────
// CAROUSEL 2 · "Tu competencia ya está en redes"
function C2S1() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow color={J.orange}>MIRÁ DÓNDE ESTÁS</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>01 / 04</div>
      </div>

      {/* faded competitor avatars */}
      <div style={{ position: "absolute", top: 220, left: 80, right: 80, display: "flex", gap: 14, opacity: 0.35 }}>
        {[J.blue, J.orange, J.blueLite, J.blue, J.orange, J.blueLite, J.blue].map((c, i) => (
          <div key={i} style={{ width: 70, height: 70, borderRadius: 999, background: c, opacity: 0.5 + (i % 3) * 0.18 }}></div>
        ))}
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 220 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 92, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0, color: J.white }}>
          Tu competencia<br />ya está en redes<span style={{ color: J.orange }}>.</span>
        </h1>
        <div style={{ marginTop: 24, fontSize: 26, color: J.muted }}>¿Y vos qué estás esperando?</div>
      </div>

      <JLogo location="Olavarría" />
    </JFrame>
  );
}

function C2S2() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>COMPARACIÓN</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>02 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 160, left: 80, right: 80 }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 60, lineHeight: 1, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          La diferencia no es el <span style={{ color: J.blue }}>presupuesto</span>.
        </h2>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 360, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ border: `1px solid ${J.faint}`, borderRadius: 16, padding: 28, opacity: 0.75 }}>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.muted, letterSpacing: "0.18em" }}>SIN ESTRATEGIA DIGITAL</div>
          <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 16 }}>
            {["Perfil fantasma", "Calendario vacío", "Cero consultas"].map(t => (
              <div key={t} style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <Ico.X s={22} c="#EF4444" />
                <div style={{ fontSize: 22, color: J.muted }}>{t}</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ background: "rgba(14,165,233,.10)", border: `1px solid ${J.blue}`, borderRadius: 16, padding: 28 }}>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.blueLite, letterSpacing: "0.18em" }}>CON OLA DIGITAL</div>
          <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 16 }}>
            {["Perfil que vende", "Agenda activa", "Consultas todos los días"].map(t => (
              <div key={t} style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <Ico.Check s={22} />
                <div style={{ fontSize: 22, color: J.white, fontWeight: 600 }}>{t}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

function C2S3() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>RUBROS</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>03 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 200, left: 80, right: 80 }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 68, lineHeight: 1.05, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Gastronomía. Comercios.<br />Clínicas. Servicios.
        </h2>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 460, display: "flex", gap: 14, flexWrap: "wrap" }}>
        {["Gestión de redes", "Google Ads", "SEO Local", "WhatsApp Business", "Email marketing"].map(p => (
          <div key={p} style={{ padding: "14px 22px", borderRadius: 999, border: `1.5px solid ${J.blue}`, background: "rgba(14,165,233,.08)", color: J.blueLite, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 20 }}>{p}</div>
        ))}
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200, paddingTop: 20, borderTop: `1px solid ${J.faint}` }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
          <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, color: J.orange, lineHeight: 1, letterSpacing: "-0.04em" }}>12+</span>
          <span style={{ fontSize: 22, color: J.muted }}>rubros en Olavarría ya crecen con nosotros.</span>
        </div>
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
const C2S4 = () => <JCTASlide headline={<>Primera consulta sin <span style={{ color: J.blue }}>costo</span>.</>} subline="Sin compromiso. Sin vueltas. Hablemos por WhatsApp." badge="Consulta sin costo" />;

// ────────────────────────────────────────────────────────────────────────
// CAROUSEL 3 · "3 errores"
function C3S1() {
  return (
    <JFrame accent={J.orange}>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow color={J.orange}>ATENCIÓN</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>01 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 200, right: 80 }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 300, color: J.orange, lineHeight: 0.85, letterSpacing: "-0.06em", textShadow: `0 0 80px ${J.orange}55` }}>×3</div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 80, lineHeight: 0.98, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          3 errores que hacen<br />que tu pyme <span style={{ color: J.orange }}>no venda</span> en redes.
        </h1>
        <div style={{ marginTop: 22, fontSize: 24, color: J.muted }}>¿Cuántos estás cometiendo?</div>
      </div>

      <div style={{ position: "absolute", bottom: 36, right: 220, display: "inline-flex", alignItems: "center", gap: 10, color: J.blue, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 18 }}>
        seguí <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 28, height: 28, borderRadius: 999, background: J.blue, color: J.white }}>→</span>
      </div>
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
function C3Interior({ num, title, body, slideNum }) {
  return (
    <JFrame accent={J.orange}>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 14 }}>
          <Ico.X s={28} c={J.orange} />
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 26, color: J.orange, letterSpacing: "0.04em" }}>ERROR {num}</div>
        </div>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>{String(slideNum).padStart(2,"0")} / 04</div>
      </div>

      <div style={{ position: "absolute", top: 200, left: 80, right: 80 }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 280, color: J.orange, lineHeight: 0.85, letterSpacing: "-0.06em", opacity: 0.2 }}>{num}</div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 480 }}>
        <div style={{ width: 80, height: 3, background: J.orange, marginBottom: 24 }}></div>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, lineHeight: 1.02, letterSpacing: "-0.03em", margin: 0, color: J.white }}>{title}</h2>
        <div style={{ marginTop: 28, fontSize: 28, color: J.muted, lineHeight: 1.4, maxWidth: 860 }}>{body}</div>
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
const C3S2 = () => <C3Interior num="01" slideNum={2} title={<>Publicar sin <span style={{ color: J.orange }}>estrategia</span>.</>} body="Postear porque sí no atrae clientes. Definí a quién le hablás primero." />;
const C3S3 = () => <C3Interior num="02" slideNum={3} title={<>No responder <span style={{ color: J.orange }}>rápido</span>.</>} body="Un mensaje sin respuesta es una venta que se va. En minutos, no en horas." />;
const C3S4 = () => <JCTASlide accent={J.orange} headline={<>¿Los estás <span style={{ color: J.orange }}>cometiendo</span>?</>} subline="Nosotros los arreglamos. Empezamos esta semana." badge="Sin compromiso" />;

// ────────────────────────────────────────────────────────────────────────
// CAROUSEL 4 · "Crece o se estanca"
function C4S1() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>HAY 2 CAMINOS</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>01 / 04</div>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "240px 80px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 28 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 132, lineHeight: 0.92, letterSpacing: "-0.04em", margin: 0 }}>
          <span style={{ color: J.blue }}>Tu negocio crece.</span>
        </h1>
        <div style={{ width: 200, height: 2, background: J.faint }}></div>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 132, lineHeight: 0.92, letterSpacing: "-0.04em", margin: 0 }}>
          <span style={{ color: J.orange }}>O se estanca.</span>
        </h1>
        <div style={{ marginTop: 24, fontSize: 22, color: J.muted }}>No hay tercer camino.</div>
      </div>

      <JLogo location="Olavarría" />
    </JFrame>
  );
}

function C4S2() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>DIAGNÓSTICO</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>02 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 62, lineHeight: 1, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Lo que duele.<br />Lo que lo <span style={{ color: J.blue }}>causa</span>.
        </h2>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 380, display: "grid", gridTemplateColumns: "1.1fr 1px 1fr", gap: 30, alignItems: "stretch" }}>
        <div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.muted, letterSpacing: "0.18em" }}>SÍNTOMAS</div>
          <div style={{ marginTop: 18, display: "flex", flexDirection: "column", gap: 14 }}>
            {["Gastás en redes y no ves clientes", "Copiás lo que hace la competencia", "Postear se siente como tirar al vacío"].map(t => (
              <div key={t} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                <span style={{ marginTop: 6, width: 8, height: 8, borderRadius: 999, background: "#EF4444", flexShrink: 0 }}></span>
                <div style={{ fontSize: 21, color: "#CBD5E1", lineHeight: 1.3 }}>{t}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: J.faint }}></div>

        <div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.blueLite, letterSpacing: "0.18em" }}>LA CAUSA</div>
          <div style={{ marginTop: 18, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 44, color: J.blue, lineHeight: 1.05, letterSpacing: "-0.03em" }}>
            No hay estrategia clara.
          </div>
        </div>
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

function C4S3() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>LO QUE TIENEN EN COMÚN</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>03 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 200, left: 80, right: 80, fontSize: 26, color: J.muted, lineHeight: 1.4, maxWidth: 820 }}>
        Las pymes de Olavarría que crecen en 3 meses tienen una cosa en común:
      </div>

      <div style={{ position: "absolute", inset: "380px 80px 200px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "relative", padding: "40px 60px", border: `1px solid ${J.blue}`, background: "rgba(14,165,233,.08)", borderRadius: 24 }}>
          {/* corner quotes */}
          <div style={{ position: "absolute", top: -18, left: 24, background: J.bg, padding: "0 12px", color: J.blue, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 40, lineHeight: 1 }}>“</div>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.blue, maxWidth: 780 }}>
            Saben exactamente<br />a quién le hablan.
          </h2>
        </div>
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
const C4S4 = () => <JCTASlide headline={<>Diagnóstico <span style={{ color: J.blue }}>gratuito</span> de tu presencia digital.</>} subline="Te decimos exactamente qué arreglar primero." badge="Sin costo · sin compromiso" />;

// ────────────────────────────────────────────────────────────────────────
// CAROUSEL 5 · "3 pasos para ganar clientes en Instagram"
function C5S1() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>GUÍA · INSTAGRAM</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>01 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 220, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 96, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0, color: J.white }}>
          3 pasos para<br />ganar clientes<br />en <span style={{ color: J.blue }}>Instagram</span>.
        </h1>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 740, display: "flex", alignItems: "center", gap: 28 }}>
        {["01", "02", "03"].map((n, i) => (
          <React.Fragment key={n}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 56, color: i === 1 ? J.orange : J.blue, letterSpacing: "-0.03em", lineHeight: 1 }}>{n}</div>
            {i < 2 && <div style={{ width: 40, height: 1, background: J.faint }}></div>}
          </React.Fragment>
        ))}
        <div style={{ marginLeft: "auto", fontSize: 18, color: J.muted, fontStyle: "italic" }}>Guardalo y aplicalo esta semana.</div>
      </div>

      <div style={{ position: "absolute", bottom: 36, right: 220, display: "inline-flex", alignItems: "center", gap: 10, color: J.orange, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 18 }}>
        deslizá <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 28, height: 28, borderRadius: 999, background: J.orange, color: J.white }}>→</span>
      </div>
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
const C5S2 = () => <JInterior num="01" numColor={J.blue}   slideNum={2} title={<>Definí a quién le <span style={{ color: J.blue }}>vendés</span>.</>} body="No postees para todos. Elegí UN tipo de cliente ideal y hablale solo a él." />;
const C5S3 = () => <JInterior num="02" numColor={J.orange} slideNum={3} title={<>Publicá <span style={{ color: J.orange }}>2-3 veces</span> por semana.</>} body="La consistencia le gana al algoritmo. Siempre." />;
const C5S4 = () => <JCTASlide headline={<>Estrategia <span style={{ color: J.blue }}>personalizada</span>.</>} subline="Armamos tu plan en 30 minutos. Sin costo." badge="Plan en 30 min" />;

// ────────────────────────────────────────────────────────────────────────
// CAROUSEL 6 · "Tu mejor cliente no te conocía"
function C6S1() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>PENSALO 5 SEGUNDOS</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>01 / 04</div>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "220px 80px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 30 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 84, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Tu mejor cliente<br />no sabía que existías<br />hace <span style={{ borderBottom: `4px solid ${J.blue}`, paddingBottom: 4, color: J.blue }}>6 meses</span>.
        </h1>
        <div style={{ marginTop: 16, fontSize: 26, color: J.muted, fontStyle: "italic" }}>¿Cómo lo encontraste?</div>
      </div>

      <div style={{ position: "absolute", bottom: 36, right: 220, display: "inline-flex", alignItems: "center", gap: 10, color: J.orange, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 18 }}>
        seguí <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 28, height: 28, borderRadius: 999, background: J.orange, color: J.white }}>→</span>
      </div>
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

function C6S2() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>JOURNEY DEL CLIENTE</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>02 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, lineHeight: 1, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Así toma decisiones tu cliente <span style={{ color: J.blue }}>hoy</span>.
        </h2>
      </div>

      {/* journey path */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 420 }}>
        <svg width="100%" height="60" viewBox="0 0 920 60" fill="none">
          <line x1="40" y1="30" x2="880" y2="30" stroke={J.faint} strokeWidth="2" />
          {[80, 320, 560, 800].map((x, i) => (
            <circle key={i} cx={x} cy="30" r="14" fill={J.blue} stroke={J.bg} strokeWidth="4" />
          ))}
        </svg>

        <div style={{ marginTop: 24, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
          {[
            { t: "Busca en Google", s: '"plomero Olavarría"' },
            { t: "Mira tu Instagram", s: "Revisa tu vidriera digital" },
            { t: "Escribe por WhatsApp", s: "Espera respuesta rápida" },
            { t: "Compra", s: "Si todo el camino cierra" },
          ].map((step, i) => (
            <div key={i}>
              <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.blueLite, letterSpacing: "0.16em" }}>0{i+1}</div>
              <div style={{ marginTop: 6, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 22, color: J.white, lineHeight: 1.2, letterSpacing: "-0.01em" }}>{step.t}</div>
              <div style={{ marginTop: 4, fontSize: 15, color: J.muted, lineHeight: 1.3 }}>{step.s}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200, paddingTop: 20, borderTop: `1px solid ${J.faint}`, fontSize: 22, color: J.muted, fontStyle: "italic" }}>
        Si fallás en cualquier paso, perdés la venta.
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

function C6S3() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>RESULTADOS REALES</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.2em" }}>03 / 04</div>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Clientes reales.<br />Sin <span style={{ color: J.orange }}>tirar guita</span> al boleo.
        </h2>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 480, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18 }}>
        {[
          { v: "+38", l: "consultas / mes" },
          { v: "×3",  l: "más reservas" },
          { v: "+300%", l: "alcance orgánico" },
        ].map(s => (
          <div key={s.l} style={{ background: "rgba(14,165,233,.08)", border: `1px solid ${J.blue}`, borderRadius: 16, padding: 24, textAlign: "center" }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, color: J.blue, letterSpacing: "-0.04em", lineHeight: 1 }}>{s.v}</div>
            <div style={{ marginTop: 8, fontSize: 16, color: J.blueLite, letterSpacing: "0.12em", textTransform: "uppercase", fontWeight: 600 }}>{s.l}</div>
          </div>
        ))}
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200, fontSize: 20, color: J.muted }}>
        Promedio de pymes en Olavarría · primeros 90 días.
      </div>

      <JCTA variant="ghost" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}
const C6S4 = () => <JCTASlide headline={<>DM para resultados <span style={{ color: J.blue }}>reales</span>.</>} subline="Primera consulta sin costo. Hablamos por WhatsApp." badge="Casos comprobables" />;

Object.assign(window, {
  // shared building blocks (used by other series files like july-series.jsx)
  J, JFrame, JLogo, JCTA, JEyebrow, Ico, Dot, JInterior, JCTASlide,
  // June pieces
  PostA, PostB, PostC, PostD, PostE, PostF, PostG, PostH, PostI,
  C1S1, C1S2, C1S3, C1S4,
  C2S1, C2S2, C2S3, C2S4,
  C3S1, C3S2, C3S3, C3S4,
  C4S1, C4S2, C4S3, C4S4,
  C5S1, C5S2, C5S3, C5S4,
  C6S1, C6S2, C6S3, C6S4,
});
