/* OLA Digital — July Series
   10 single posts (J–S) · 1080×1080 · same flat dark-navy system as June
   Reuses J / JFrame / JLogo / JCTA / JEyebrow / Ico from june-series.jsx
   (must be loaded AFTER june-series.jsx in the host html)
*/

// Pull shared building blocks off window (june-series.jsx exports them there).
const { J, JFrame, JLogo, JCTA, JEyebrow, Ico } = window;

// ════════════════════════════════════════════════════════════════════════
// POST J — Sin Google Maps no existís
// ════════════════════════════════════════════════════════════════════════
function PostJ() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", alignItems: "center", gap: 16 }}>
        <Ico.Pin s={42} />
        <JEyebrow>SEO LOCAL · OLAVARRÍA</JEyebrow>
      </div>

      {/* subtle map grid */}
      <svg style={{ position: "absolute", left: 32, right: 32, top: 32, bottom: 32, width: "calc(100% - 64px)", height: "calc(100% - 64px)", opacity: 0.18 }} viewBox="0 0 1016 1016">
        <defs>
          <pattern id="mapGrid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M80 0 L0 0 L0 80" fill="none" stroke={J.blue} strokeWidth="0.6"/>
          </pattern>
        </defs>
        <rect width="1016" height="1016" fill="url(#mapGrid)"/>
        <path d="M0 600 Q 200 580 360 620 T 700 600 T 1016 640" stroke={J.blue} strokeWidth="2" fill="none" opacity="0.5"/>
        <path d="M120 0 L120 1016 M520 0 L520 1016 M860 0 L860 1016" stroke={J.blue} strokeWidth="1" opacity="0.3"/>
      </svg>

      {/* faded competitor pins */}
      {[{ x: 200, y: 380 }, { x: 760, y: 320 }, { x: 880, y: 720 }, { x: 240, y: 760 }].map((p, i) => (
        <div key={i} style={{ position: "absolute", left: p.x, top: p.y, opacity: 0.45 }}>
          <Ico.Pin s={56} c={J.muted} />
        </div>
      ))}

      {/* big bright pin — you */}
      <div style={{ position: "absolute", left: 480, top: 460, filter: `drop-shadow(0 0 32px ${J.orange})` }}>
        <Ico.Pin s={120} c={J.orange} />
      </div>

      {/* dashed locator ring */}
      <svg style={{ position: "absolute", left: 420, top: 480, pointerEvents: "none" }} width="240" height="240" viewBox="0 0 240 240">
        <circle cx="120" cy="120" r="100" stroke={J.orange} strokeWidth="1.5" strokeDasharray="4 8" fill="none" opacity="0.6"/>
        <circle cx="120" cy="120" r="60" stroke={J.orange} strokeWidth="1" strokeDasharray="3 6" fill="none" opacity="0.4"/>
      </svg>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 88, lineHeight: 0.96, letterSpacing: "-0.035em", margin: 0, color: J.white }}>
          Si no estás en<br />Google Maps,<br />para tu cliente <span style={{ color: J.orange }}>no existís</span>.
        </h1>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST K — 73% lee reviews antes de comprar
// ════════════════════════════════════════════════════════════════════════
function PostK() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>DATO · REPUTACIÓN ONLINE</JEyebrow>
      </div>

      {/* huge percent on the right */}
      <div style={{ position: "absolute", right: -30, top: 110, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 760, color: J.blue, lineHeight: 0.8, letterSpacing: "-0.08em", textShadow: `0 0 100px ${J.blue}55` }}>73</div>
      <div style={{ position: "absolute", right: 60, top: 160, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 120, color: J.blueLite, lineHeight: 1, letterSpacing: "-0.04em" }}>%</div>

      {/* star row */}
      <div style={{ position: "absolute", left: 80, top: 540, display: "flex", gap: 8 }}>
        {[1, 2, 3, 4, 5].map(i => (
          <svg key={i} width="36" height="36" viewBox="0 0 24 24" fill={J.orange}>
            <polygon points="12,2 15,9 22,9.5 17,14.5 18.5,22 12,18 5.5,22 7,14.5 2,9.5 9,9" />
          </svg>
        ))}
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200 }}>
        <div style={{ width: 80, height: 4, background: J.orange, marginBottom: 22 }}></div>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 34, color: J.white, lineHeight: 1.2, letterSpacing: "-0.015em", maxWidth: 880 }}>
          de tus clientes lee las <span style={{ color: J.orange }}>reseñas</span> antes de comprar.
        </div>
        <div style={{ marginTop: 16, fontSize: 20, color: J.muted, fontStyle: "italic" }}>
          ¿Qué dicen las tuyas?
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST L — Cada 30 segundos perdés un cliente
// ════════════════════════════════════════════════════════════════════════
function PostL() {
  return (
    <JFrame accent={J.orange}>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow color={J.orange}>TIEMPO DE RESPUESTA</JEyebrow>
      </div>

      {/* central clock */}
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", paddingTop: 40 }}>
        <div style={{ position: "relative", width: 420, height: 420 }}>
          {/* ring */}
          <svg width="420" height="420" viewBox="0 0 420 420" style={{ position: "absolute", inset: 0 }}>
            <circle cx="210" cy="210" r="190" stroke={J.faint} strokeWidth="2" fill="none" />
            <circle cx="210" cy="210" r="190" stroke={J.orange} strokeWidth="6" fill="none"
              strokeDasharray={2 * Math.PI * 190} strokeDashoffset={2 * Math.PI * 190 * 0.5}
              strokeLinecap="round" transform="rotate(-90 210 210)" />
            {/* tick marks */}
            {[...Array(12)].map((_, i) => {
              const a = (i * 30 - 90) * Math.PI / 180;
              const x1 = 210 + Math.cos(a) * 168, y1 = 210 + Math.sin(a) * 168;
              const x2 = 210 + Math.cos(a) * 180, y2 = 210 + Math.sin(a) * 180;
              return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={J.muted} strokeWidth="2" opacity="0.4" />;
            })}
          </svg>
          {/* number */}
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.22em" }}>CADA</div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 240, color: J.orange, lineHeight: 0.9, letterSpacing: "-0.05em", textShadow: `0 0 60px ${J.orange}55` }}>30''</div>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.22em" }}>SEGUNDOS</div>
          </div>
        </div>

        <div style={{ marginTop: 56, textAlign: "center", maxWidth: 820 }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 48, lineHeight: 1.05, letterSpacing: "-0.025em", margin: 0, color: J.white }}>
            que tardás en responder<br />es un cliente que <span style={{ color: J.orange }}>se va</span>.
          </h2>
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST M — Local cerrado vs Instagram abierto (always-on)
// ════════════════════════════════════════════════════════════════════════
function PostM() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>TU NEGOCIO · 24/7</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 70, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Tu local cierra a las 20hs.<br /><span style={{ color: J.blue }}>Tu Instagram, no.</span>
        </h1>
      </div>

      {/* time strip 00 → 24 */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 460 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.muted, letterSpacing: "0.18em", marginBottom: 12 }}>
          <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span>
        </div>

        {/* LOCAL bar */}
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 18 }}>
          <div style={{ width: 110, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.muted, letterSpacing: "0.18em" }}>LOCAL</div>
          <div style={{ flex: 1, height: 40, position: "relative", background: J.faint, borderRadius: 6, overflow: "hidden" }}>
            <div style={{ position: "absolute", left: "37.5%", width: "33%", top: 0, bottom: 0, background: `repeating-linear-gradient(45deg, ${J.muted}33, ${J.muted}33 6px, transparent 6px, transparent 12px)`, border: `1px solid ${J.muted}66` }}></div>
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.muted, letterSpacing: "0.18em" }}>9:00 — 20:00 · 11h</div>
          </div>
        </div>

        {/* INSTAGRAM bar */}
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ width: 110, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: J.blueLite, letterSpacing: "0.18em" }}>INSTAGRAM</div>
          <div style={{ flex: 1, height: 40, position: "relative", background: `linear-gradient(90deg, ${J.blue} 0%, ${J.blueLite} 100%)`, borderRadius: 6, boxShadow: `0 0 30px ${J.blue}55` }}>
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.bg, letterSpacing: "0.18em", fontWeight: 700 }}>SIEMPRE ABIERTO · 24h</div>
          </div>
        </div>

        <div style={{ marginTop: 60, padding: 28, border: `1px solid ${J.blue}`, background: "rgba(14,165,233,.08)", borderRadius: 16 }}>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 28, color: J.white, lineHeight: 1.25, letterSpacing: "-0.015em" }}>
            Mientras dormís, alguien busca lo que vendés. <span style={{ color: J.blue }}>Que te encuentre.</span>
          </div>
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST N — Caso real: estudio contable
// ════════════════════════════════════════════════════════════════════════
function PostN() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>CASO REAL · ESTUDIO CONTABLE</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, lineHeight: 1.02, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Un estudio contable<br />de Olavarría pasó a tener<br /><span style={{ color: J.blue }}>consultas todos los días</span>.
        </h1>
      </div>

      {/* stats grid */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 540, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
        {[
          { v: "+40", l: "consultas / mes",   c: J.blue },
          { v: "60", l: "días",                c: J.orange, suf: "d" },
          { v: "×4",  l: "tráfico al sitio",  c: J.blue },
        ].map((s, i) => (
          <div key={i} style={{ background: i === 1 ? "rgba(249,115,22,.08)" : "rgba(14,165,233,.08)", border: `1px solid ${i === 1 ? J.orange : J.blue}`, borderRadius: 16, padding: 28 }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 88, color: s.c, letterSpacing: "-0.04em", lineHeight: 1 }}>{s.v}</div>
            <div style={{ marginTop: 12, fontSize: 16, color: i === 1 ? J.orangeLite : J.blueLite, letterSpacing: "0.12em", textTransform: "uppercase", fontWeight: 600 }}>{s.l}</div>
          </div>
        ))}
      </div>

      {/* sparkline */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 800 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.muted, letterSpacing: "0.18em" }}>CONSULTAS · SEMANALES</div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.blueLite, letterSpacing: "0.18em" }}>+312%</div>
        </div>
        <svg width="100%" height="80" viewBox="0 0 920 80" preserveAspectRatio="none">
          <path d="M0 68 L80 62 L160 64 L240 56 L320 58 L400 46 L480 38 L560 32 L640 22 L720 14 L800 10 L880 6 L920 4"
                stroke={J.blue} strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M0 68 L80 62 L160 64 L240 56 L320 58 L400 46 L480 38 L560 32 L640 22 L720 14 L800 10 L880 6 L920 4 L920 80 L0 80 Z"
                fill={`url(#nGrad)`} opacity="0.35"/>
          <defs>
            <linearGradient id="nGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={J.blue} stopOpacity="0.8"/>
              <stop offset="100%" stopColor={J.blue} stopOpacity="0"/>
            </linearGradient>
          </defs>
        </svg>
      </div>

      <JCTA />
      <JLogo caso="Caso real" location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST O — 3 cosas en tu bio
// ════════════════════════════════════════════════════════════════════════
function PostO() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>BIO DE INSTAGRAM · CHECKLIST</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          3 cosas que no<br />pueden faltar en tu <span style={{ color: J.blue }}>bio</span>.
        </h1>
      </div>

      {/* mock phone bio preview */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 470, display: "grid", gridTemplateColumns: "300px 1fr", gap: 28, alignItems: "start" }}>
        {/* phone */}
        <div style={{ background: J.ink, border: `1px solid ${J.faint}`, borderRadius: 24, padding: 18 }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ width: 56, height: 56, borderRadius: 999, background: `linear-gradient(135deg, ${J.blue}, ${J.orange})` }}></div>
            <div>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 18, color: J.white }}>@tunegocio</div>
              <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 11, color: J.muted, letterSpacing: "0.12em", marginTop: 2 }}>2.4K · seguidores</div>
            </div>
          </div>
          <div style={{ marginTop: 14, fontSize: 14, color: J.white, lineHeight: 1.4 }}>
            <span style={{ color: J.blue, fontWeight: 700 }}>Lo que hacés</span><br/>
            <span style={{ color: J.muted }}>↳ para quién y dónde</span><br/>
            <span style={{ color: J.orange, fontWeight: 600 }}>→ Reservá por WhatsApp ↓</span>
          </div>
          <div style={{ marginTop: 12, padding: "8px 12px", background: J.faint, borderRadius: 8, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 11, color: J.blueLite }}>
            wa.me/549228...
          </div>
        </div>

        {/* list */}
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          {[
            { n: "01", t: "Qué hacés, en una línea", s: "Que se entienda en 3 segundos." },
            { n: "02", t: "Para quién y dónde",       s: "“Pymes de Olavarría” > “Marketing digital”." },
            { n: "03", t: "Una sola acción clara",    s: "Un link. Un botón. Un WhatsApp." },
          ].map(r => (
            <div key={r.n} style={{ display: "flex", gap: 16, paddingBottom: 14, borderBottom: `1px solid ${J.faint}` }}>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 32, color: J.blue, letterSpacing: "-0.03em", minWidth: 50 }}>{r.n}</div>
              <div>
                <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 24, color: J.white, lineHeight: 1.15, letterSpacing: "-0.01em" }}>{r.t}</div>
                <div style={{ marginTop: 4, fontSize: 16, color: J.muted }}>{r.s}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <JCTA label="Te la armamos" />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST P — "Si no estás en Google, no existís" (quote-style)
// ════════════════════════════════════════════════════════════════════════
function PostP() {
  return (
    <JFrame>
      {/* faint search bar mock */}
      <div style={{ position: "absolute", top: 200, left: 120, right: 120, opacity: 0.5 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "18px 24px", borderRadius: 999, border: `1px solid ${J.faint}`, background: "rgba(255,255,255,.02)" }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={J.muted} strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 18, color: J.muted, letterSpacing: "0.04em" }}>
            panadería cerca de mí <span style={{ borderRight: `2px solid ${J.blue}`, paddingRight: 2, marginLeft: 2 }}></span>
          </div>
        </div>
      </div>

      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>VERDAD INCÓMODA</JEyebrow>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "340px 80px 240px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 260, color: J.blue, lineHeight: 0.7, letterSpacing: "-0.06em", marginLeft: -16, opacity: 0.7 }}>“</div>

        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 80, lineHeight: 1.02, letterSpacing: "-0.03em", margin: 0, marginTop: -80, color: J.white }}>
          Si no estás en<br /><span style={{ color: J.blue }}>Google</span>,<br />para tu cliente <span style={{ color: J.orange }}>no existís</span>.
        </h1>

        <div style={{ marginTop: 36, display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 40, height: 1, background: J.faint }}></div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: J.muted, letterSpacing: "0.22em", textTransform: "uppercase" }}>
            Y no es opinión. Es comportamiento.
          </div>
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST Q — 5 segundos para decidir
// ════════════════════════════════════════════════════════════════════════
function PostQ() {
  return (
    <JFrame accent={J.orange}>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow color={J.orange}>DATO · PRIMERA IMPRESIÓN</JEyebrow>
      </div>

      {/* huge 5 with countdown ticks */}
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", paddingTop: 60 }}>
        <div style={{ position: "relative" }}>
          <div style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 640,
            color: J.orange, lineHeight: 0.78, letterSpacing: "-0.08em",
            textShadow: `0 0 100px ${J.orange}55, 0 0 30px ${J.orange}33`,
          }}>5</div>
          <div style={{ position: "absolute", right: -30, top: 60, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 140, color: J.orangeLite, lineHeight: 1, letterSpacing: "-0.04em" }}>s</div>
        </div>

        {/* countdown ticks */}
        <div style={{ marginTop: 8, display: "flex", gap: 10 }}>
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} style={{ width: 60, height: 6, borderRadius: 999, background: i <= 5 ? J.orange : J.faint, boxShadow: i <= 5 ? `0 0 12px ${J.orange}88` : "none" }}></div>
          ))}
        </div>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, bottom: 200 }}>
        <div style={{ width: 80, height: 4, background: J.blue, marginBottom: 20 }}></div>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 36, color: J.white, lineHeight: 1.2, letterSpacing: "-0.02em", maxWidth: 920 }}>
          Es lo que tarda tu cliente en decidir si se queda <span style={{ color: J.blue }}>o se va</span>.
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST R — Web lenta vs Web rápida
// ════════════════════════════════════════════════════════════════════════
function PostR() {
  return (
    <JFrame>
      <div style={{ position: "absolute", top: 80, left: 80, right: 80 }}>
        <JEyebrow>VELOCIDAD · SITIOS WEB</JEyebrow>
      </div>

      <div style={{ position: "absolute", top: 170, left: 80, right: 80 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, lineHeight: 1.0, letterSpacing: "-0.03em", margin: 0, color: J.white }}>
          Una web que tarda<br />es una venta que <span style={{ color: J.orange }}>se va</span>.
        </h1>
      </div>

      {/* two browser-bar mocks */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 480, display: "flex", flexDirection: "column", gap: 24 }}>
        {/* SLOW */}
        <div style={{ border: `1px solid ${J.faint}`, borderRadius: 14, overflow: "hidden", opacity: 0.8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 16px", background: J.faint }}>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: "#475569" }}></div>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: "#475569" }}></div>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: "#475569" }}></div>
            <div style={{ marginLeft: 12, flex: 1, height: 18, borderRadius: 6, background: "#1E293B", display: "flex", alignItems: "center", paddingLeft: 10, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 10, color: J.muted }}>tunegocio.com.ar</div>
          </div>
          <div style={{ padding: 24, display: "flex", alignItems: "center", gap: 18 }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 56, color: "#EF4444", letterSpacing: "-0.03em", lineHeight: 1 }}>7.4s</div>
            <div style={{ flex: 1 }}>
              <div style={{ height: 12, background: J.faint, borderRadius: 999, overflow: "hidden" }}>
                <div style={{ width: "32%", height: "100%", background: "#EF4444", borderRadius: 999 }}></div>
              </div>
              <div style={{ marginTop: 8, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.muted, letterSpacing: "0.16em" }}>WEB LENTA · 53% SE VA</div>
            </div>
          </div>
        </div>

        {/* FAST */}
        <div style={{ background: "rgba(14,165,233,.06)", border: `1px solid ${J.blue}`, borderRadius: 14, overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 16px", background: J.faint }}>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: J.blue, boxShadow: `0 0 8px ${J.blue}` }}></div>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: "#475569" }}></div>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: "#475569" }}></div>
            <div style={{ marginLeft: 12, flex: 1, height: 18, borderRadius: 6, background: "#0A0F1E", display: "flex", alignItems: "center", paddingLeft: 10, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 10, color: J.blueLite }}>tunegocio.com.ar</div>
          </div>
          <div style={{ padding: 24, display: "flex", alignItems: "center", gap: 18 }}>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 56, color: J.blue, letterSpacing: "-0.03em", lineHeight: 1 }}>1.2s</div>
            <div style={{ flex: 1 }}>
              <div style={{ height: 12, background: J.faint, borderRadius: 999, overflow: "hidden" }}>
                <div style={{ width: "100%", height: "100%", background: `linear-gradient(90deg, ${J.blue}, ${J.blueLite})`, borderRadius: 999, boxShadow: `0 0 14px ${J.blue}88` }}></div>
              </div>
              <div style={{ marginTop: 8, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.blueLite, letterSpacing: "0.16em" }}>WEB RÁPIDA · CONVIERTE</div>
            </div>
          </div>
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// POST S — Cierre · Tu negocio es bueno. Que se vea.
// ════════════════════════════════════════════════════════════════════════
function PostS() {
  return (
    <JFrame>
      {/* radial glow */}
      <div style={{ position: "absolute", inset: 32, background: `radial-gradient(ellipse 60% 50% at 50% 55%, ${J.blue}1F 0%, transparent 65%)`, pointerEvents: "none" }}></div>

      <div style={{ position: "absolute", top: 80, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <JEyebrow>OLA DIGITAL · OLAVARRÍA</JEyebrow>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 12, color: J.muted, letterSpacing: "0.22em" }}>EST. 2024</div>
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "240px 80px 240px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center", gap: 36 }}>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 128, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0, color: J.white, maxWidth: 920 }}>
          Tu negocio<br />es <span style={{ color: J.blue, textShadow: `0 0 40px ${J.blue}66` }}>bueno</span>.
        </h1>

        {/* divider with dot */}
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 80, height: 1, background: J.faint }}></div>
          <span style={{ width: 8, height: 8, borderRadius: 999, background: J.orange, boxShadow: `0 0 14px ${J.orange}` }}></span>
          <div style={{ width: 80, height: 1, background: J.faint }}></div>
        </div>

        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 128, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0, color: J.white, maxWidth: 920 }}>
          Que se <span style={{ color: J.orange, textShadow: `0 0 40px ${J.orange}66` }}>vea</span>.
        </h1>

        <div style={{ marginTop: 16, fontFamily: "'Inter', sans-serif", fontSize: 22, color: J.muted, fontStyle: "italic", maxWidth: 720 }}>
          Hacemos que te encuentren. Y te elijan.
        </div>
      </div>

      <JCTA />
      <JLogo location="Olavarría" />
    </JFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
Object.assign(window, {
  PostJ, PostK, PostL, PostM, PostN, PostO, PostP, PostQ, PostR, PostS,
});
