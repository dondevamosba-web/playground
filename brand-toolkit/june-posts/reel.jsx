/* OLA Digital — 15s Reel storyboard
   4 keyframes at 1080×1920 representing scenes 0-3s, 3-8s, 8-13s, 13-15s.
   Each artboard renders the FRAME content + a timeline footer with timing & motion notes. */

const REEL_GRAD = "linear-gradient(160deg, #0C4A6E 0%, #0369A1 30%, #0EA5E9 65%, #06B6D4 100%)";

function ReelFrame({ children, segment, label, motion, ease, palette = ["#0EA5E9", "#F97316"], sceneIdx, total = 4 }) {
  // Bottom 220px is timeline / scene metadata (designer chrome, not part of the actual reel)
  const REEL_H = 1920;
  const CHROME = 240;
  const SAFE_H = REEL_H - CHROME;
  return (
    <div style={{ width: 1080, height: REEL_H, background: "#05080F", color: "#FFFFFF", fontFamily: "'Inter', sans-serif", position: "relative", overflow: "hidden" }}>
      {/* live frame */}
      <div style={{ position: "absolute", top: 0, left: 0, width: 1080, height: SAFE_H, overflow: "hidden" }}>
        {children}
        {/* scene label badge */}
        <div style={{ position: "absolute", top: 32, left: 32, display: "flex", alignItems: "center", gap: 10, padding: "10px 18px", borderRadius: 999, background: "rgba(5,8,15,.55)", border: "1px solid rgba(255,255,255,.18)", backdropFilter: "blur(8px)" }}>
          <span style={{ width: 8, height: 8, borderRadius: 999, background: "#22D3EE", boxShadow: "0 0 10px #22D3EE" }}></span>
          <span style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 18, color: "#E0F2FE", letterSpacing: "0.12em" }}>SCENE {String(sceneIdx).padStart(2, "0")} · {segment}</span>
        </div>
      </div>

      {/* designer chrome: timeline + motion notes */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: CHROME, background: "#0A0F1E", borderTop: "1px solid #1E293B", padding: "24px 36px", display: "flex", flexDirection: "column", gap: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 26, color: "#FFFFFF", letterSpacing: "-0.01em" }}>{label}</div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 16, color: "#7DD3FC" }}>{segment}</div>
        </div>

        {/* timeline bar (0-15s) */}
        <div style={{ position: "relative", height: 28, background: "#111827", borderRadius: 8, overflow: "hidden", border: "1px solid #1E293B" }}>
          {/* segment fills */}
          {[
            { from: 0,  to: 3,  c: "#0EA5E9" },
            { from: 3,  to: 8,  c: "#06B6D4" },
            { from: 8,  to: 13, c: "#38BDF8" },
            { from: 13, to: 15, c: "#F97316" },
          ].map((s, i) => (
            <div key={i} style={{
              position: "absolute", top: 0, bottom: 0,
              left: `${(s.from / 15) * 100}%`,
              width: `${((s.to - s.from) / 15) * 100}%`,
              background: i + 1 === sceneIdx ? s.c : "transparent",
              borderRight: i < 3 ? "1px dashed #1E293B" : "none",
              opacity: i + 1 === sceneIdx ? 1 : 0.18,
            }} />
          ))}
          {[1,2,3,4,5,6,7,8,9,10,11,12,13,14].map(t => (
            <div key={t} style={{ position: "absolute", left: `${(t/15)*100}%`, top: 16, bottom: 0, width: 1, background: "#1E293B" }} />
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: "#475569" }}>
          <span>0s</span><span>5s</span><span>10s</span><span>15s</span>
        </div>

        <div style={{ display: "flex", gap: 24, fontSize: 15, color: "#94A3B8", marginTop: 2 }}>
          <div><span style={{ color: "#64748B", letterSpacing: "0.16em", textTransform: "uppercase", fontSize: 12, fontWeight: 600 }}>Motion</span><div style={{ color: "#E0F2FE", fontSize: 16, marginTop: 2 }}>{motion}</div></div>
          <div><span style={{ color: "#64748B", letterSpacing: "0.16em", textTransform: "uppercase", fontSize: 12, fontWeight: 600 }}>Ease</span><div style={{ color: "#E0F2FE", fontSize: 16, marginTop: 2, fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>{ease}</div></div>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
            {palette.map(c => <span key={c} style={{ width: 22, height: 22, borderRadius: 6, background: c, border: "1px solid rgba(255,255,255,.15)" }}></span>)}
          </div>
        </div>
      </div>
    </div>
  );
}

// 0–3s: hook text on dark
function Reel1() {
  return (
    <ReelFrame
      sceneIdx={1}
      segment="0:00 – 0:03"
      label="Hook · pregunta directa"
      motion="Texto entra word-by-word desde abajo, blur 8→0. Cursor parpadea al final."
      ease="cubic-bezier(.22,1,.36,1)"
      palette={["#0EA5E9", "#0F172A"]}
    >
      <div style={{ width: "100%", height: "100%", background: "#0A0F1E", position: "relative", overflow: "hidden" }}>
        {/* subtle radial */}
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 50% at 50% 60%, rgba(14,165,233,.35) 0%, rgba(10,15,30,0) 65%)" }}></div>
        {/* grain dots */}
        <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.4 }}>
          {Array.from({ length: 50 }).map((_, i) => {
            const x = (i * 137) % 1080;
            const y = (i * 211) % 1680;
            return <circle key={i} cx={x} cy={y} r={1.2} fill="#38BDF8" opacity={(i % 4) / 8 + 0.1} />;
          })}
        </svg>

        <div style={{ position: "absolute", inset: 0, padding: "200px 80px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 24, color: "#22D3EE", letterSpacing: "0.16em", marginBottom: 40 }}>
            ▍ 00:01
          </div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 116, lineHeight: 0.98, letterSpacing: "-0.04em", margin: 0 }}>
            ¿Por qué tu<br /><span style={{ color: "#94A3B8" }}>competencia</span><br />aparece <span style={{ color: "#38BDF8" }}>antes</span><br />que vos en<br /><span style={{ display: "inline-block", background: "#FFFFFF", color: "#0F172A", padding: "8px 20px", borderRadius: 12, transform: "rotate(-2deg)" }}>Google?</span>
          </h1>
          <div style={{ marginTop: 40, width: 12, height: 60, background: "#22D3EE", boxShadow: "0 0 24px #22D3EE" }}></div>
        </div>
      </div>
    </ReelFrame>
  );
}

// 3–8s: stat cards
function StatCard({ value, label, delay, color = "#0EA5E9", rotate = 0 }) {
  return (
    <div style={{
      background: "#111827",
      borderRadius: 28,
      padding: "32px 36px",
      border: `2px solid ${color}`,
      transform: `rotate(${rotate}deg)`,
      boxShadow: `0 24px 60px -20px ${color}55, 0 0 0 6px rgba(14,165,233,.06)`,
      position: "relative",
      overflow: "hidden",
    }}>
      <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: "#64748B", letterSpacing: "0.16em" }}>{delay}</div>
      <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, color: "#FFFFFF", lineHeight: 1, letterSpacing: "-0.04em", marginTop: 4 }}>{value}</div>
      <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 24, color, fontWeight: 600, marginTop: 6 }}>{label}</div>
    </div>
  );
}

function Reel2() {
  return (
    <ReelFrame
      sceneIdx={2}
      segment="0:03 – 0:08"
      label="Stat cards · counter animations"
      motion="3 tarjetas entran de a una (300ms stagger). Números cuentan 0→target en 600ms."
      ease="easeOutExpo"
      palette={["#0EA5E9", "#06B6D4", "#F97316"]}
    >
      <div style={{ width: "100%", height: "100%", background: "#05080F", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 40% at 50% 50%, rgba(6,182,212,.20) 0%, rgba(5,8,15,0) 70%)" }}></div>

        <div style={{ position: "absolute", inset: 0, padding: "160px 80px 100px", display: "flex", flexDirection: "column", gap: 36, justifyContent: "center" }}>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 48, color: "#FFFFFF", letterSpacing: "-0.02em", lineHeight: 1.05 }}>
            Lo que pasa cuando<br />arreglamos eso:
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
            <StatCard value="+300%" label="visitas al sitio" delay="t=3.4s" color="#0EA5E9" rotate={-1.2} />
            <StatCard value="×3" label="consultas por WhatsApp" delay="t=4.6s" color="#06B6D4" rotate={1.5} />
            <StatCard value="#1" label="en búsquedas locales" delay="t=5.8s" color="#F97316" rotate={-0.8} />
          </div>
        </div>
      </div>
    </ReelFrame>
  );
}

// 8–13s: wave icon builds across screen
function Reel3() {
  return (
    <ReelFrame
      sceneIdx={3}
      segment="0:08 – 0:13"
      label="Wave mark builds · brand reveal"
      motion="Trazos de la onda dibujan de izq→der (stroke-dashoffset). Gradiente fluye. Pulso al cerrar."
      ease="cubic-bezier(.65,0,.35,1)"
      palette={["#0EA5E9", "#06B6D4", "#F97316"]}
    >
      <div style={{ width: "100%", height: "100%", background: REEL_GRAD, position: "relative", overflow: "hidden" }}>
        {/* receding waves */}
        {[0,1,2,3].map(i => (
          <div key={i} style={{ position: "absolute", inset: 0, borderRadius: "50%", border: "2px solid rgba(255,255,255,.18)", margin: `${120 + i * 140}px`, opacity: 1 - i * 0.18 }}></div>
        ))}

        <div style={{ position: "absolute", inset: 0, padding: "200px 60px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
          {/* large wave mark with gradient stroke */}
          <svg width="900" height="500" viewBox="0 0 100 56" style={{ overflow: "visible" }}>
            <defs>
              <linearGradient id="reelGrad" x1="0" y1="28" x2="100" y2="28" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#FFFFFF" />
                <stop offset="55%" stopColor="#7DD3FC" />
                <stop offset="100%" stopColor="#F97316" />
              </linearGradient>
              <filter id="glow2" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="1.4" result="b" />
                <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>
            <g stroke="url(#reelGrad)" strokeWidth="3.6" strokeLinecap="round" fill="none" filter="url(#glow2)">
              <path d="M4 44 Q 28 18, 50 28 T 96 18" opacity="0.5" />
              <path d="M4 34 Q 28 8, 50 18 T 96 8" opacity="0.85" />
              <path d="M4 24 Q 28 -2, 50 8 T 96 -2" />
            </g>
            {/* tip dot */}
            <circle cx="96" cy="-2" r="2.8" fill="#F97316" />
          </svg>

          <div style={{ marginTop: 24, fontFamily: "'Inter', sans-serif", fontSize: 28, color: "rgba(255,255,255,.85)", letterSpacing: "0.32em", textTransform: "uppercase" }}>
            la marca aparece
          </div>
        </div>

        {/* progress ticks */}
        <div style={{ position: "absolute", bottom: 60, left: 80, right: 80, display: "flex", gap: 6 }}>
          {Array.from({ length: 40 }).map((_, i) => (
            <span key={i} style={{ flex: 1, height: 4, background: i < 30 ? "#FFFFFF" : "rgba(255,255,255,.25)", borderRadius: 2 }}></span>
          ))}
        </div>
      </div>
    </ReelFrame>
  );
}

// 13–15s: logo lockup + CTA
function Reel4() {
  return (
    <ReelFrame
      sceneIdx={4}
      segment="0:13 – 0:15"
      label="Logo lockup + CTA"
      motion="Logo entra con scale 1.05→1, CTA pulsa una vez. URL underline dibuja."
      ease="cubic-bezier(.34,1.56,.64,1)"
      palette={["#0EA5E9", "#F97316"]}
    >
      <div style={{ width: "100%", height: "100%", background: "#0A0F1E", position: "relative", overflow: "hidden" }}>
        {/* soft glow */}
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 50% at 50% 45%, rgba(14,165,233,.30) 0%, rgba(10,15,30,0) 65%)" }}></div>

        <div style={{ position: "absolute", inset: 0, padding: "180px 80px 120px", display: "flex", flexDirection: "column", justifyContent: "space-between", alignItems: "center", textAlign: "center" }}>
          <div></div>

          {/* logo lockup */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 32 }}>
            <svg width="280" height="180" viewBox="0 0 100 56" style={{ overflow: "visible", filter: "drop-shadow(0 0 28px rgba(34,211,238,.5))" }}>
              <defs>
                <linearGradient id="reelLogoGrad" x1="0" y1="28" x2="100" y2="28" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#0EA5E9" />
                  <stop offset="55%" stopColor="#06B6D4" />
                  <stop offset="100%" stopColor="#F97316" />
                </linearGradient>
              </defs>
              <g stroke="url(#reelLogoGrad)" strokeWidth="4" strokeLinecap="round" fill="none">
                <path d="M4 44 Q 28 18, 50 28 T 96 18" opacity="0.5" />
                <path d="M4 34 Q 28 8, 50 18 T 96 8" opacity="0.85" />
                <path d="M4 24 Q 28 -2, 50 8 T 96 -2" />
              </g>
            </svg>
            <div style={{ display: "flex", alignItems: "baseline", gap: 22 }}>
              <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 140, color: "#FFFFFF", letterSpacing: "-0.04em", lineHeight: 1 }}>OLA</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 38, color: "#38BDF8", letterSpacing: "0.32em" }}>DIGITAL</span>
            </div>
            <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 30, color: "#E0F2FE", marginTop: 8 }}>
              <span style={{ borderBottom: "2px solid #38BDF8", paddingBottom: 4 }}>oladigital.com.ar</span>
            </div>
          </div>

          {/* CTA */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 16,
              background: "#F97316", color: "#FFFFFF",
              padding: "26px 44px", borderRadius: 999,
              fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 36,
              letterSpacing: "-0.01em",
              boxShadow: "0 20px 50px -10px rgba(249,115,22,.65), 0 0 0 8px rgba(249,115,22,.12)",
            }}>
              <svg width="38" height="38" viewBox="0 0 32 32" fill="#FFFFFF">
                <path d="M16 3C9 3 3.4 8.6 3.4 15.6c0 2.3.6 4.5 1.7 6.4L3 29l7.2-2c1.8 1 3.8 1.5 5.9 1.5 7 0 12.6-5.6 12.6-12.6S23 3 16 3z" />
              </svg>
              Escribinos hoy
            </div>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 18, color: "#7DD3FC", letterSpacing: "0.16em" }}>+54 9 2284 · WhatsApp</div>
          </div>
        </div>
      </div>
    </ReelFrame>
  );
}

Object.assign(window, { Reel1, Reel2, Reel3, Reel4, REEL_GRAD });
