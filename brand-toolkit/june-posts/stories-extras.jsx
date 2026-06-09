/* OLA Digital — Stories (1080×1920), more logos, email headers */

// ════════════════════════════════════════════════════════════════════════
// STORIES (5 vertical 1080×1920)
// ════════════════════════════════════════════════════════════════════════

function StoryFrame({ children, dark = true }) {
  return (
    <div style={{
      width: 1080, height: 1920,
      background: dark ? COL.navyBg : COL.ice,
      color: dark ? "#FFFFFF" : COL.navy,
      fontFamily: "'Inter', sans-serif",
      position: "relative", overflow: "hidden",
    }}>
      {children}
    </div>
  );
}

// Story header — small profile chip at top mimics IG story header (informational, not interactive)
function StoryHeader({ dark = true, label }) {
  return (
    <div style={{ position: "absolute", top: 56, left: 56, right: 56, display: "flex", alignItems: "center", gap: 14 }}>
      {/* progress segments */}
      <div style={{ position: "absolute", top: -28, left: 0, right: 0, display: "flex", gap: 6 }}>
        {[1,1,0.4,0,0].map((p, i) => (
          <div key={i} style={{ flex: 1, height: 4, background: "rgba(255,255,255,.2)", borderRadius: 2, overflow: "hidden" }}>
            <div style={{ width: `${p*100}%`, height: "100%", background: "#FFFFFF" }}></div>
          </div>
        ))}
      </div>
      <div style={{ width: 56, height: 56, borderRadius: 999, background: GRAD, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 50, height: 50, borderRadius: 999, background: dark ? COL.navyBg : "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg width="34" height="34" viewBox="0 0 100 100">
            <g stroke={dark ? "#FFFFFF" : COL.primary} strokeWidth="14" strokeLinecap="round" fill="none">
              <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
              <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
              <path d="M8 48 Q 30 16, 50 26 T 92 14" />
            </g>
          </svg>
        </div>
      </div>
      <div>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 24, color: dark ? "#FFFFFF" : COL.navy, letterSpacing: "-0.01em" }}>oladigital</div>
        <div style={{ fontSize: 16, color: dark ? COL.cool : COL.slate, marginTop: 2 }}>{label || "Olavarría · ahora"}</div>
      </div>
    </div>
  );
}

// Story 1 — Countdown / urgency
function Story1() {
  return (
    <StoryFrame>
      <div className="ola-anim" style={{ position: "absolute", inset: 0 }}>
        <div className="ola-grad" style={{ position: "absolute", inset: 0, background: GRAD }}></div>
        <WaveField color="rgba(255,255,255,0.10)" />
        <StoryHeader />
        <div style={{ position: "absolute", inset: 0, padding: "200px 80px 140px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
          <div>
            <div className="ola-headline" style={{ display: "inline-flex", alignItems: "center", gap: 12, padding: "12px 22px", borderRadius: 999, background: "rgba(255,255,255,.16)", border: "1.5px solid rgba(255,255,255,.35)", fontSize: 22, fontWeight: 600, letterSpacing: "0.16em", textTransform: "uppercase" }}>
              <span style={{ width: 10, height: 10, borderRadius: 999, background: "#FDE68A", boxShadow: "0 0 14px #FDE68A" }}></span>
              ÚLTIMOS lugares
            </div>
            <h1 className="ola-headline delay-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 140, lineHeight: 0.92, letterSpacing: "-0.04em", margin: 0, marginTop: 36 }}>
              Quedan<br /><span style={{ fontSize: 320, color: "#FDE68A", letterSpacing: "-0.07em" }}>2</span><br />lugares este<br />mes.
            </h1>
          </div>

          {/* "swipe up" lookalike */}
          <div className="ola-cta" style={{ background: COL.accent, color: "#FFFFFF", padding: "26px 36px", borderRadius: 22, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 18, boxShadow: "0 20px 50px -10px rgba(249,115,22,.65)" }}>
            <div>
              <div style={{ fontSize: 16, color: "#FFEDD5", fontWeight: 600, letterSpacing: "0.18em", textTransform: "uppercase" }}>Reservá el tuyo</div>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 38, lineHeight: 1.1, marginTop: 4 }}>Escribinos por<br />WhatsApp →</div>
            </div>
            <svg width="80" height="80" viewBox="0 0 32 32" fill="#FFFFFF">
              <path d="M16 3C9 3 3.4 8.6 3.4 15.6c0 2.3.6 4.5 1.7 6.4L3 29l7.2-2c1.8 1 3.8 1.5 5.9 1.5 7 0 12.6-5.6 12.6-12.6S23 3 16 3z" />
            </svg>
          </div>
        </div>
      </div>
    </StoryFrame>
  );
}

// Story 2 — Poll
function Story2() {
  return (
    <StoryFrame>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 80% 50% at 50% 30%, rgba(14,165,233,.45) 0%, rgba(10,15,30,0) 65%)" }}></div>
      <WaveField color="rgba(56,189,248,0.07)" />
      <StoryHeader />

      <div style={{ position: "absolute", inset: 0, padding: "200px 80px 140px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
        <div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 130, lineHeight: 0.92, letterSpacing: "-0.04em", margin: 0 }}>
            ¿Tu negocio<br />tiene <span style={{ color: COL.tint }}>web</span>?
          </h1>
          <div style={{ marginTop: 24, fontSize: 28, color: COL.cool }}>Tocá una opción 👇</div>
        </div>

        {/* poll buttons */}
        <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
          <button style={{
            background: "linear-gradient(135deg, #0369A1, #0EA5E9)",
            color: "#FFFFFF", border: "none",
            padding: "44px 36px", borderRadius: 28,
            fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 60,
            display: "flex", alignItems: "center", justifyContent: "space-between",
            boxShadow: "0 28px 60px -20px rgba(3,105,161,.6)",
            letterSpacing: "-0.02em",
            cursor: "pointer",
          }}>
            <span>✓ Sí, tengo</span>
            <span style={{ fontSize: 36, color: "#BAE6FD" }}>34%</span>
          </button>
          <button style={{
            background: "#F97316",
            color: "#FFFFFF", border: "none",
            padding: "44px 36px", borderRadius: 28,
            fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 60,
            display: "flex", alignItems: "center", justifyContent: "space-between",
            boxShadow: "0 28px 60px -20px rgba(249,115,22,.6)",
            letterSpacing: "-0.02em",
            cursor: "pointer",
          }}>
            <span>✗ Todavía no</span>
            <span style={{ fontSize: 36, color: "#FFEDD5" }}>66%</span>
          </button>
          <div style={{ textAlign: "center", marginTop: 8, fontSize: 22, color: COL.cool, fontFamily: "'JetBrains Mono', ui-monospace, monospace", letterSpacing: "0.12em" }}>
            247 RESPUESTAS · OLAVARRÍA
          </div>
        </div>
      </div>
    </StoryFrame>
  );
}

// Story 3 — Testimonial quote
function Story3() {
  return (
    <StoryFrame dark={false}>
      <div style={{ position: "absolute", top: -200, left: -200, width: 700, height: 700, borderRadius: 999, background: "linear-gradient(135deg, #0EA5E9, #06B6D4)", filter: "blur(50px)", opacity: 0.30 }}></div>
      <div style={{ position: "absolute", bottom: -250, right: -150, width: 600, height: 600, borderRadius: 999, background: "linear-gradient(135deg, #F97316, #FBBF24)", filter: "blur(60px)", opacity: 0.20 }}></div>

      <div style={{ position: "absolute", top: 56, left: 56, right: 56 }}>
        <StoryHeader dark={false} label="Testimonio · Olavarría" />
      </div>

      <div style={{ position: "absolute", inset: 0, padding: "240px 80px 160px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 48 }}>
        <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 320, lineHeight: 0.7, color: COL.primary, letterSpacing: "-0.06em", marginLeft: -20 }}>
          “
        </div>
        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, lineHeight: 1.1, letterSpacing: "-0.025em", color: COL.navy, margin: 0, marginTop: -100 }}>
          En 4 meses pasamos de no aparecer en Google a ser <span style={{ color: COL.primary }}>los primeros</span> de Olavarría.
        </h1>

        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {[1,2,3,4,5].map(i => (
            <svg key={i} width="32" height="32" viewBox="0 0 24 24" fill={COL.accentAlt}>
              <path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z" />
            </svg>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 20, paddingTop: 28, borderTop: "1px solid #CBD5E1" }}>
          <div style={{ width: 80, height: 80, borderRadius: 999, background: "linear-gradient(135deg, #F97316, #FBBF24)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 32, color: "#FFFFFF" }}>MR</div>
          <div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 28, color: COL.navy, letterSpacing: "-0.01em" }}>Martín Ríos</div>
            <div style={{ fontSize: 20, color: COL.slate, marginTop: 4 }}>Dueño · Estudio Contable Ríos</div>
          </div>
        </div>
      </div>

      {/* footer logo */}
      <div style={{ position: "absolute", bottom: 56, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <FooterLogo light={false} />
      </div>
    </StoryFrame>
  );
}

// Story 4 — Quick tip
function Story4() {
  return (
    <StoryFrame>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 50% at 50% 70%, rgba(249,115,22,.22) 0%, rgba(10,15,30,0) 65%), radial-gradient(ellipse 60% 40% at 50% 20%, rgba(14,165,233,.30) 0%, rgba(10,15,30,0) 65%)" }}></div>
      <StoryHeader />

      <div style={{ position: "absolute", inset: 0, padding: "200px 80px 140px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
        <div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 14, padding: "14px 24px", borderRadius: 999, background: COL.accent, color: "#FFFFFF", fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 26, letterSpacing: "-0.01em" }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="#FFFFFF"><path d="M9 21h6M12 3a7 7 0 0 0-4 12.7V18h8v-2.3A7 7 0 0 0 12 3z" stroke="#FFFFFF" strokeWidth="1.5" fill="#FFFFFF" /></svg>
            TIP DEL DÍA
          </div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0, marginTop: 36 }}>
            Respondé los<br />comentarios en<br /><span style={{ color: COL.tint }}>menos de</span><br /><span style={{ color: "#FDE68A" }}>1 hora.</span>
          </h1>
        </div>

        {/* mini chart */}
        <div style={{ background: "rgba(15,23,42,.55)", border: "1px solid #1E293B", borderRadius: 24, padding: 32, backdropFilter: "blur(8px)" }}>
          <div style={{ fontSize: 18, color: COL.cool, letterSpacing: "0.16em", textTransform: "uppercase", fontWeight: 600 }}>Conversión vs. tiempo de respuesta</div>
          <div style={{ marginTop: 20, display: "flex", alignItems: "flex-end", gap: 14, height: 220 }}>
            {[
              { l: "0-1h",   h: "92%", color: "#22C55E" },
              { l: "1-4h",   h: "60%", color: "#0EA5E9" },
              { l: "4-24h",  h: "30%", color: "#F59E0B" },
              { l: "+24h",   h: "8%",  color: "#EF4444" },
            ].map(b => (
              <div key={b.l} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end" }}>
                <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 28, color: "#FFFFFF", marginBottom: 8 }}>{b.h}</div>
                <div style={{ width: "100%", height: b.h, background: b.color, borderRadius: 10, boxShadow: `0 0 30px ${b.color}55` }}></div>
                <div style={{ marginTop: 12, fontSize: 18, color: COL.cool, fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>{b.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </StoryFrame>
  );
}

// Story 5 — Behind the scenes
function Story5() {
  return (
    <StoryFrame>
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, #0A0F1E 0%, #0C4A6E 100%)" }}></div>
      {/* desk grid */}
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.5 }}>
        {Array.from({ length: 14 }).map((_, i) => (
          <line key={`v${i}`} x1={i * 80} y1="0" x2={i * 80} y2="1920" stroke="#1E293B" strokeWidth="1" />
        ))}
        {Array.from({ length: 24 }).map((_, i) => (
          <line key={`h${i}`} x1="0" y1={i * 80} x2="1080" y2={i * 80} stroke="#1E293B" strokeWidth="1" />
        ))}
      </svg>
      <StoryHeader />

      <div style={{ position: "absolute", inset: 0, padding: "200px 80px 140px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
        <div>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 22, color: COL.tint, letterSpacing: "0.18em", marginBottom: 24 }}>BEHIND_THE_SCENES.MOV</div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            Así<br />trabajamos<br />en <span style={{ color: COL.tint }}>OLA</span>.
          </h1>
        </div>

        {/* placeholder photo slot — striped */}
        <div style={{
          background: "repeating-linear-gradient(135deg, #1E293B 0 20px, #0F172A 20px 40px)",
          borderRadius: 28,
          height: 580,
          border: "2px dashed rgba(56,189,248,.4)",
          display: "flex", alignItems: "center", justifyContent: "center",
          position: "relative", overflow: "hidden",
        }}>
          <div style={{ position: "absolute", inset: 0, background: "radial-gradient(circle at center, rgba(14,165,233,.25) 0%, transparent 60%)" }}></div>
          <div style={{ textAlign: "center", color: COL.cool, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 22, letterSpacing: "0.1em" }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>▶</div>
            FOTO/VIDEO DEL EQUIPO<br />trabajando en la oficina
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            ["Lunes 8:30", "Reunión semanal con vos"],
            ["Martes a jueves", "Producimos tu contenido"],
            ["Viernes", "Te mandamos el reporte"],
          ].map(([d, t]) => (
            <div key={d} style={{ display: "flex", gap: 18, alignItems: "center", color: "#FFFFFF" }}>
              <div style={{ width: 14, height: 14, borderRadius: 999, background: COL.tint, boxShadow: `0 0 14px ${COL.tint}` }}></div>
              <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 20, color: COL.tint, minWidth: 220 }}>{d}</div>
              <div style={{ fontSize: 24, fontWeight: 600 }}>{t}</div>
            </div>
          ))}
        </div>
      </div>
    </StoryFrame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// LOGO VARIATIONS (4 new)
// ════════════════════════════════════════════════════════════════════════

// 5. WhatsApp profile · dark icon-only badge (square)
function LogoWhatsAppDP() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#0A0F1E", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
      {/* phone-safe square inset */}
      <div style={{
        width: 320, height: 320, borderRadius: "50%", background: GRAD,
        boxShadow: "0 0 80px rgba(14,165,233,.45), inset 0 0 0 8px rgba(255,255,255,.10)",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <svg width="200" height="200" viewBox="0 0 100 100" style={{ overflow: "visible" }}>
          <g stroke="#FFFFFF" strokeWidth="14" strokeLinecap="round" fill="none" filter="drop-shadow(0 4px 12px rgba(0,0,0,.25))">
            <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
            <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
            <path d="M8 48 Q 30 16, 50 26 T 92 14" />
          </g>
        </svg>
      </div>
      <div style={{ position: "absolute", bottom: 30, left: 0, right: 0, textAlign: "center", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: COL.cool, letterSpacing: "0.18em" }}>
        WHATSAPP DP · 640×640 · CROP A CÍRCULO
      </div>
    </div>
  );
}

// 6. Horizontal lockup for email signature (white bg, compact)
function LogoEmailSig() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#FFFFFF", display: "flex", flexDirection: "column", alignItems: "flex-start", justifyContent: "center", padding: "0 56px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <svg width="48" height="48" viewBox="0 0 100 100">
          <g stroke={COL.primary} strokeWidth="14" strokeLinecap="round" fill="none">
            <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
            <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
            <path d="M8 48 Q 30 16, 50 26 T 92 14" />
          </g>
        </svg>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 36, color: COL.navy, letterSpacing: "-0.02em", lineHeight: 1 }}>OLA</span>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 16, color: COL.primary, letterSpacing: "0.32em" }}>DIGITAL</span>
        </div>
        <span style={{ marginLeft: 18, paddingLeft: 18, borderLeft: "1px solid #CBD5E1", fontSize: 14, color: COL.slate, fontFamily: "'Inter', sans-serif", lineHeight: 1.5 }}>
          Hacemos crecer negocios en internet.<br />
          <span style={{ color: COL.primary, fontWeight: 600 }}>oladigital.com.ar</span> · hola@oladigital.com.ar
        </span>
      </div>
      <div style={{ marginTop: 28, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 11, color: COL.cool, letterSpacing: "0.18em" }}>
        EMAIL SIGNATURE · 600PX MAX · MIN 32PX HEIGHT
      </div>
    </div>
  );
}

// 7. Favicon / app icon — wave mark only, 512×512 (shown larger here, with size guides)
function LogoFavicon() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#F0F9FF", display: "flex", alignItems: "center", justifyContent: "center", gap: 36, padding: 40 }}>
      {/* large */}
      <div style={{ width: 240, height: 240, borderRadius: 56, background: GRAD, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 30px 60px -20px rgba(3,105,161,.45)" }}>
        <svg width="160" height="160" viewBox="0 0 100 100">
          <g stroke="#FFFFFF" strokeWidth="14" strokeLinecap="round" fill="none">
            <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
            <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
            <path d="M8 48 Q 30 16, 50 26 T 92 14" />
          </g>
        </svg>
      </div>
      {/* size ladder */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14, alignItems: "flex-start" }}>
        {[
          { s: 96, label: "192" },
          { s: 64, label: "128" },
          { s: 40, label: "64" },
          { s: 24, label: "32" },
          { s: 16, label: "16" },
        ].map(({ s, label }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: s, height: s, borderRadius: Math.max(4, s/5), background: GRAD, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width={s*0.65} height={s*0.65} viewBox="0 0 100 100">
                <g stroke="#FFFFFF" strokeWidth={s < 30 ? 18 : 14} strokeLinecap="round" fill="none">
                  <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity={s < 30 ? "0" : "0.75"} />
                  <path d="M8 48 Q 30 16, 50 26 T 92 14" />
                </g>
              </svg>
            </div>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: COL.slate }}>{label}px</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// 8. Co-brand "Powered by" watermark strip
function LogoPoweredBy() {
  return (
    <div style={{ width: "100%", height: "100%", background: "#FFFFFF", display: "flex", flexDirection: "column", alignItems: "stretch", justifyContent: "center", padding: 0 }}>
      {/* mock card preview */}
      <div style={{
        margin: "20px 36px",
        background: "linear-gradient(180deg, #F0F9FF 0%, #FFFFFF 100%)",
        border: "1px solid #E0F2FE",
        borderRadius: 18,
        padding: "22px 24px",
        flex: 1,
        display: "flex", flexDirection: "column",
      }}>
        <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 11, color: COL.slate, letterSpacing: "0.18em" }}>PARTNER CONTENT</div>
        <div style={{ marginTop: 6, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 22, color: COL.navy, letterSpacing: "-0.01em", lineHeight: 1.1 }}>Tu marca acá</div>
        <div style={{ marginTop: "auto", paddingTop: 12, borderTop: "1px dashed #CBD5E1", display: "flex", alignItems: "center", gap: 10, fontSize: 11, color: COL.slate }}>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500 }}>Powered by</span>
          <svg width="20" height="20" viewBox="0 0 100 100">
            <g stroke={COL.primary} strokeWidth="14" strokeLinecap="round" fill="none">
              <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
              <path d="M8 48 Q 30 16, 50 26 T 92 14" />
            </g>
          </svg>
          <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 14, color: COL.navy, letterSpacing: "-0.01em" }}>OLA</span>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 9, color: COL.primary, letterSpacing: "0.32em" }}>DIGITAL</span>
        </div>
      </div>
      <div style={{ padding: "8px 36px 18px", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 11, color: COL.cool, letterSpacing: "0.18em" }}>
        WATERMARK STRIP · USAR EN MATERIAL CO-BRAND
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════
// EMAIL HEADERS — 600×200 (shown ~scaled, label below)
// ════════════════════════════════════════════════════════════════════════

function EmailFrame({ children }) {
  return (
    <div style={{ width: 1080, height: 540, background: "#F8FAFC", padding: 40, fontFamily: "'Inter', sans-serif", display: "flex", flexDirection: "column" }}>
      {/* sender chrome */}
      <div style={{ background: "#FFFFFF", borderRadius: 18, padding: 24, boxShadow: "0 14px 40px -20px rgba(15,23,42,.18)", flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14, paddingBottom: 16, borderBottom: "1px solid #E2E8F0" }}>
          <div style={{ width: 36, height: 36, borderRadius: 999, background: GRAD }}></div>
          <div>
            <div style={{ fontWeight: 700, color: COL.navy, fontSize: 16 }}>OLA Digital <span style={{ color: COL.slate, fontWeight: 400 }}>&lt;hola@oladigital.com.ar&gt;</span></div>
            <div style={{ fontSize: 13, color: COL.slate }}>para vos · hoy 09:14</div>
          </div>
        </div>
        {children}
      </div>
    </div>
  );
}

// Header banner — 1000×260 inside an email shell (visual fidelity > exact 600px)
function HeaderBanner({ children, height = 260 }) {
  return (
    <div style={{ marginTop: 18, width: 1000, height, borderRadius: 16, overflow: "hidden", position: "relative" }}>
      {children}
    </div>
  );
}

function Email1() {
  return (
    <EmailFrame>
      <div style={{ marginTop: 16, fontSize: 22, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: COL.navy }}>El boletín de OLA — Edición #14</div>
      <HeaderBanner>
        <div style={{ position: "absolute", inset: 0, background: GRAD }}></div>
        <WaveField color="rgba(255,255,255,0.10)" />
        <div style={{ position: "absolute", inset: 0, padding: "32px 40px", color: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, letterSpacing: "0.22em", color: "#BAE6FD" }}>NEWSLETTER · MARZO</div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 52, lineHeight: 1, letterSpacing: "-0.025em", marginTop: 10 }}>El boletín<br />de OLA.</div>
            <div style={{ marginTop: 12, fontSize: 18, color: "#E0F2FE" }}>5 tips, 1 caso, 0 vueltas.</div>
          </div>
          <svg width="160" height="160" viewBox="0 0 100 100">
            <g stroke="#FFFFFF" strokeWidth="12" strokeLinecap="round" fill="none">
              <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
              <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
              <path d="M8 48 Q 30 16, 50 26 T 92 14" />
            </g>
          </svg>
        </div>
      </HeaderBanner>
      <div style={{ marginTop: 14, fontSize: 14, color: COL.slate }}>Cuerpo del email…</div>
    </EmailFrame>
  );
}

function Email2() {
  return (
    <EmailFrame>
      <div style={{ marginTop: 16, fontSize: 22, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: COL.navy }}>20% off este mes · Solo 5 lugares</div>
      <HeaderBanner>
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, #F97316 0%, #FBBF24 45%, #F59E0B 100%)" }}></div>
        {/* darker overlay */}
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 80% at 90% 50%, rgba(15,23,42,.35) 0%, transparent 60%)" }}></div>
        <div style={{ position: "absolute", inset: 0, padding: "28px 40px", color: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 10, background: "rgba(15,23,42,.85)", color: "#FFFFFF", padding: "8px 18px", borderRadius: 999, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, letterSpacing: "0.18em" }}>
              ● PROMO · MARZO
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, lineHeight: 0.95, letterSpacing: "-0.04em", marginTop: 12 }}>
              <span style={{ fontSize: 100 }}>20%</span> off
            </div>
            <div style={{ marginTop: 4, fontSize: 18, color: "#FFEDD5" }}>en todos nuestros planes — solo este mes.</div>
          </div>
          <div style={{ background: "#FFFFFF", color: COL.navy, padding: "16px 24px", borderRadius: 16, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 22, boxShadow: "0 14px 30px -10px rgba(15,23,42,.35)" }}>
            QUIERO MI 20%
          </div>
        </div>
      </HeaderBanner>
      <div style={{ marginTop: 14, fontSize: 14, color: COL.slate }}>Cuerpo del email…</div>
    </EmailFrame>
  );
}

function Email3() {
  return (
    <EmailFrame>
      <div style={{ marginTop: 16, fontSize: 22, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: COL.navy }}>Tu reporte mensual · febrero 2026</div>
      <HeaderBanner>
        <div style={{ position: "absolute", inset: 0, background: "#0A0F1E" }}></div>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 60% at 80% 30%, rgba(14,165,233,.35) 0%, transparent 65%)" }}></div>
        <div style={{ position: "absolute", inset: 0, padding: "28px 40px", color: "#FFFFFF", display: "flex", alignItems: "center", gap: 32 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, letterSpacing: "0.22em", color: COL.tint }}>REPORTE · FEB 2026</div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 48, lineHeight: 1, letterSpacing: "-0.025em", marginTop: 10 }}>
              Cómo nos fue<br />este mes.
            </div>
          </div>
          {/* stat tiles */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, minWidth: 460 }}>
            {[
              { v: "+38%", l: "visitas web", c: COL.tint },
              { v: "×2.4", l: "consultas WA", c: "#FDE68A" },
              { v: "#1",   l: "en Google",   c: COL.accent },
            ].map(s => (
              <div key={s.l} style={{ background: "rgba(15,23,42,.65)", border: "1px solid #1E293B", borderRadius: 14, padding: "14px 16px" }}>
                <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 32, color: s.c, lineHeight: 1 }}>{s.v}</div>
                <div style={{ fontSize: 13, color: COL.cool, marginTop: 6 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </HeaderBanner>
      <div style={{ marginTop: 14, fontSize: 14, color: COL.slate }}>Cuerpo del email…</div>
    </EmailFrame>
  );
}

Object.assign(window, {
  Story1, Story2, Story3, Story4, Story5,
  LogoWhatsAppDP, LogoEmailSig, LogoFavicon, LogoPoweredBy,
  Email1, Email2, Email3,
});
