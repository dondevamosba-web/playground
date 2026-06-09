/* OLA Digital — Instagram feed posts (3 standalone 1080×1080) + 5-slide carousel
   All rendered as 1080×1080 inside design canvas artboards. */

const COL = {
  primaryDark: "#0369A1",
  primary: "#0EA5E9",
  primaryLight: "#06B6D4",
  tint: "#38BDF8",
  accent: "#F97316",
  accentAlt: "#F59E0B",
  navy: "#0F172A",
  navyBg: "#0A0F1E",
  surface: "#111827",
  slate: "#334155",
  cool: "#94A3B8",
  ice: "#F0F9FF",
};
const GRAD = "linear-gradient(135deg, #0C4A6E 0%, #0369A1 28%, #0EA5E9 60%, #06B6D4 85%, #38BDF8 100%)";

// Decorative wave field — concentric arcs evoking signal/ocean.
function WaveField({ color = "rgba(255,255,255,0.10)", offset = 0, count = 9, strokeWidth = 2 }) {
  const arcs = [];
  for (let i = 0; i < count; i++) {
    const r = 180 + i * 110;
    arcs.push(
      <circle
        key={i}
        cx={1080 + offset}
        cy={1080 + offset}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        opacity={1 - i / (count + 2)}
      />
    );
  }
  return (
    <svg width="1080" height="1080" viewBox="0 0 1080 1080" style={{ position: "absolute", inset: 0 }}>
      {arcs}
    </svg>
  );
}

function CTAButton({ label = "Escribinos por WhatsApp", size = 1 }) {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 16 * size,
        background: COL.accent,
        color: "#FFFFFF",
        padding: `${22 * size}px ${36 * size}px`,
        borderRadius: 999,
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        fontWeight: 800,
        fontSize: 28 * size,
        letterSpacing: "-0.01em",
        boxShadow: "0 14px 40px -12px rgba(249,115,22,.55)",
      }}
    >
      <svg width={32 * size} height={32 * size} viewBox="0 0 32 32" fill="#FFFFFF">
        <path d="M16 3C9 3 3.4 8.6 3.4 15.6c0 2.3.6 4.5 1.7 6.4L3 29l7.2-2c1.8 1 3.8 1.5 5.9 1.5 7 0 12.6-5.6 12.6-12.6S23 3 16 3zm0 22.9c-1.8 0-3.5-.5-5-1.4l-.4-.2-4.3 1.2 1.2-4.2-.3-.4a10.4 10.4 0 1118.7-6.3c0 5.7-4.6 10.3-10.3 10.3zm5.7-7.7c-.3-.2-1.8-.9-2.1-1s-.5-.2-.7.2-.8 1-.9 1.2-.3.2-.6 0c-1.7-.8-2.8-1.5-3.9-3.5-.3-.5.3-.5.8-1.5.1-.2 0-.4 0-.5l-1-2.3c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.8.4-.3.4-1.1 1.1-1.1 2.7s1.1 3.1 1.3 3.3c.2.2 2.2 3.4 5.3 4.8 2 .8 2.6 1 3.5 1 .6 0 1.7-.5 2-1.1.3-.5.3-1.1.2-1.2-.1-.1-.3-.2-.6-.3z" />
      </svg>
      {label}
    </div>
  );
}

// Small "OLA Digital" footer logo
function FooterLogo({ light = true }) {
  const fg = light ? "#FFFFFF" : COL.navy;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <svg width="44" height="44" viewBox="0 0 100 100">
        <g stroke={fg} strokeWidth="14" strokeLinecap="round" fill="none">
          <path d="M8 72 Q 30 40, 50 50 T 92 38" opacity="0.45" />
          <path d="M8 60 Q 30 28, 50 38 T 92 26" opacity="0.75" />
          <path d="M8 48 Q 30 16, 50 26 T 92 14" />
        </g>
      </svg>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 28, color: fg, letterSpacing: "-0.02em" }}>OLA</span>
        <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 13, color: light ? "#BAE6FD" : COL.primary, letterSpacing: "0.32em" }}>DIGITAL</span>
      </div>
    </div>
  );
}

function Tag({ children, dark }) {
  return (
    <div style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      padding: "10px 22px",
      borderRadius: 999,
      background: dark ? "rgba(56,189,248,.15)" : "rgba(255,255,255,.18)",
      border: dark ? "1.5px solid rgba(56,189,248,.4)" : "1.5px solid rgba(255,255,255,.35)",
      color: dark ? "#7DD3FC" : "#FFFFFF",
      fontFamily: "'Inter', sans-serif",
      fontWeight: 600,
      fontSize: 18,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
    }}>
      <span style={{ width: 8, height: 8, borderRadius: 999, background: dark ? "#38BDF8" : "#FFFFFF" }}></span>
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// FEED POST 1 — SEO: "¿Tu negocio aparece en Google?"
// Background: gradient. Mock-Google-result card. Big rhetorical headline.
function Feed1() {
  return (
    <div style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: GRAD, color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      <WaveField color="rgba(255,255,255,0.08)" />
      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag>SEO local</Tag>
          <FooterLogo />
        </div>

        <div style={{ marginTop: 80 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 132, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            ¿Tu negocio<br />aparece en<br /><span style={{ color: "#FDE68A" }}>Google?</span>
          </h1>
        </div>

        {/* Fake search bar */}
        <div style={{ marginTop: 56, background: "#FFFFFF", borderRadius: 18, padding: "22px 28px", display: "flex", alignItems: "center", gap: 18, boxShadow: "0 30px 60px -20px rgba(2,8,30,.45)" }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2.4" strokeLinecap="round">
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" />
          </svg>
          <span style={{ color: COL.slate, fontSize: 26, fontWeight: 500 }}>panadería en Olavarría</span>
          <span style={{ marginLeft: "auto", width: 3, height: 28, background: COL.primary, animation: "" }}></span>
        </div>

        {/* Mock result cards */}
        <div style={{ marginTop: 28, display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ background: "rgba(255,255,255,.96)", borderRadius: 16, padding: "20px 26px", color: COL.navy }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 16, color: COL.slate, fontWeight: 500 }}>
              <span style={{ width: 24, height: 24, borderRadius: 999, background: COL.ice, display: "inline-flex", alignItems: "center", justifyContent: "center", color: COL.primary, fontWeight: 800, fontSize: 14 }}>1</span>
              tucompetencia.com.ar · Olavarría
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 26, color: COL.primaryDark, marginTop: 6 }}>La competencia — Inicio</div>
          </div>
          <div style={{ background: "rgba(255,255,255,.55)", borderRadius: 16, padding: "20px 26px", color: COL.navy, border: "2px dashed rgba(255,255,255,.6)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 16, color: COL.slate, fontWeight: 500 }}>
              <span style={{ width: 24, height: 24, borderRadius: 999, background: COL.accent, display: "inline-flex", alignItems: "center", justifyContent: "center", color: "#FFFFFF", fontWeight: 800, fontSize: 14 }}>?</span>
              tunegocio.com.ar · ¿dónde?
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 26, color: COL.slate, marginTop: 6, fontStyle: "italic" }}>Vos no estás acá.</div>
          </div>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 22, color: "#BAE6FD", lineHeight: 1.3, maxWidth: 480 }}>
            Hacemos que te encuentren primero<br />en tu zona.
          </div>
          <CTAButton />
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// FEED POST 2 — Social: "Redes sociales que venden, no solo que gustan"
// Background: dark navy, hearts vs conversions visual.
function Feed2() {
  return (
    <div style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: COL.navyBg, color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      {/* gradient blob */}
      <div style={{ position: "absolute", left: -160, bottom: -180, width: 720, height: 720, borderRadius: 999, background: GRAD, filter: "blur(80px)", opacity: 0.55 }}></div>
      <WaveField color="rgba(56,189,248,0.08)" />

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag dark>Redes sociales</Tag>
          <FooterLogo />
        </div>

        <div style={{ marginTop: 64 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            Redes que<br /><span style={{ color: COL.tint }}>venden</span>.<br />No solo que<br /><span style={{ textDecoration: "line-through", textDecorationColor: COL.accent, textDecorationThickness: 10, color: "#64748B" }}>gustan</span>.
          </h1>
        </div>

        {/* Two contrast cards */}
        <div style={{ marginTop: 56, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div style={{ background: COL.surface, borderRadius: 24, padding: 28, border: "1px solid #1E293B" }}>
            <div style={{ fontSize: 18, color: COL.cool, fontWeight: 600, letterSpacing: "0.18em", textTransform: "uppercase" }}>Antes</div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 6, marginTop: 8 }}>
              <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, color: "#FFFFFF" }}>847</span>
              <svg width="34" height="34" viewBox="0 0 24 24" fill="#EF4444"><path d="M12 21s-7-4.5-9.5-9C.9 9.4 1.9 5.7 5 4.6c2-.7 4.1.1 5.3 1.7l1.7 2 1.7-2C14.9 4.7 17 3.9 19 4.6c3.1 1.1 4.1 4.8 2.5 7.4C19 16.5 12 21 12 21z"/></svg>
            </div>
            <div style={{ fontSize: 18, color: COL.cool, marginTop: 4 }}>likes / mes</div>
            <div style={{ marginTop: 16, fontSize: 22, color: "#94A3B8", fontWeight: 500 }}>Cero clientes nuevos.</div>
          </div>
          <div style={{ background: "linear-gradient(180deg, #0369A1 0%, #0EA5E9 100%)", borderRadius: 24, padding: 28, position: "relative", overflow: "hidden" }}>
            <div style={{ fontSize: 18, color: "#BAE6FD", fontWeight: 600, letterSpacing: "0.18em", textTransform: "uppercase" }}>Con nosotros</div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 8 }}>
              <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 76, color: "#FFFFFF" }}>+38</span>
              <span style={{ fontSize: 26, color: "#FFFFFF", fontWeight: 700 }}>consultas</span>
            </div>
            <div style={{ fontSize: 18, color: "#BAE6FD", marginTop: 4 }}>por WhatsApp / mes</div>
            <div style={{ marginTop: 16, fontSize: 22, color: "#FFFFFF", fontWeight: 600 }}>Eso sí mueve la caja.</div>
          </div>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 22, color: COL.cool, lineHeight: 1.3, maxWidth: 460 }}>
            Contenido pensado para que la gente<br />de Olavarría te elija.
          </div>
          <CTAButton />
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// FEED POST 3 — Web: "Tu web, trabajando mientras dormís"
// Background: dark with browser mockup + "moon" vibe.
function Feed3() {
  return (
    <div style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: COL.navyBg, color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      {/* sky gradient at top */}
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 60% at 80% 8%, rgba(14,165,233,.55) 0%, rgba(10,15,30,0) 60%)" }}></div>
      {/* stars */}
      <svg width="1080" height="1080" style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: 60 }).map((_, i) => {
          const x = (i * 89) % 1080;
          const y = (i * 53) % 540;
          const r = (i % 3 === 0) ? 2.4 : 1.2;
          return <circle key={i} cx={x} cy={y} r={r} fill="#FFFFFF" opacity={(i % 5) / 8 + 0.2} />;
        })}
      </svg>

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag dark>Sitios web</Tag>
          <FooterLogo />
        </div>

        <div style={{ marginTop: 56 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 128, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            Tu web,<br />trabajando<br />mientras<br /><span style={{ color: COL.tint }}>dormís.</span>
          </h1>
        </div>

        {/* Browser card */}
        <div style={{ marginTop: 36, background: COL.surface, borderRadius: 22, overflow: "hidden", border: "1px solid #1E293B", boxShadow: "0 40px 80px -20px rgba(2,8,30,.7)" }}>
          <div style={{ background: "#0B1220", padding: "14px 22px", display: "flex", alignItems: "center", gap: 10, borderBottom: "1px solid #1E293B" }}>
            <span style={{ width: 12, height: 12, borderRadius: 999, background: "#475569" }}></span>
            <span style={{ width: 12, height: 12, borderRadius: 999, background: "#475569" }}></span>
            <span style={{ width: 12, height: 12, borderRadius: 999, background: "#475569" }}></span>
            <span style={{ marginLeft: 24, color: COL.cool, fontSize: 15, fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>tunegocio.com.ar</span>
            <span style={{ marginLeft: "auto", display: "inline-flex", alignItems: "center", gap: 8, color: "#22C55E", fontSize: 14, fontWeight: 600 }}>
              <span style={{ width: 8, height: 8, borderRadius: 999, background: "#22C55E", boxShadow: "0 0 12px #22C55E" }}></span>
              LIVE
            </span>
          </div>
          <div style={{ padding: "24px 26px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 14, color: COL.cool, letterSpacing: "0.16em", textTransform: "uppercase", fontWeight: 600 }}>03:47 AM · Olavarría</div>
              <div style={{ marginTop: 8, display: "flex", alignItems: "baseline", gap: 14 }}>
                <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, color: "#FFFFFF", lineHeight: 1 }}>12</span>
                <span style={{ fontSize: 22, color: COL.tint, fontWeight: 600 }}>consultas esta noche</span>
              </div>
            </div>
            {/* mini sparkline */}
            <svg width="220" height="80" viewBox="0 0 220 80" fill="none">
              <path d="M0 60 L30 50 L60 55 L90 38 L120 42 L150 22 L180 28 L220 8" stroke={COL.primary} strokeWidth="3" strokeLinecap="round" />
              <circle cx="220" cy="8" r="6" fill={COL.accent} />
            </svg>
          </div>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontFamily: "'Inter', sans-serif", fontSize: 22, color: COL.cool, lineHeight: 1.3, maxWidth: 460 }}>
            Sitios rápidos que captan clientes<br />los 7 días, las 24 horas.
          </div>
          <CTAButton />
        </div>
      </div>
    </div>
  );
}

// ===========================================================================
// CAROUSEL — "5 errores que cometen los negocios de Olavarría en internet"
// ===========================================================================

function CarouselFrame({ children, light = false, slideNum, total = 5 }) {
  return (
    <div style={{
      width: 1080, height: 1080, position: "relative", overflow: "hidden",
      background: light ? COL.ice : COL.navyBg,
      color: light ? COL.navy : "#FFFFFF",
      fontFamily: "'Inter', sans-serif",
    }}>
      {children}
      <div style={{
        position: "absolute", bottom: 36, left: 80,
        fontFamily: "'JetBrains Mono', ui-monospace, monospace",
        fontSize: 16, color: light ? COL.cool : "#475569", letterSpacing: "0.2em",
      }}>
        {String(slideNum).padStart(2, "0")} / {String(total).padStart(2, "0")}
      </div>
      <div style={{ position: "absolute", bottom: 36, right: 80 }}>
        <FooterLogo light={!light} />
      </div>
    </div>
  );
}

// Slide 1 — Cover
function Carousel1() {
  return (
    <CarouselFrame slideNum={1}>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 80% 60% at 20% 20%, rgba(14,165,233,.45) 0%, rgba(10,15,30,0) 65%)" }}></div>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 50% at 90% 90%, rgba(249,115,22,.25) 0%, rgba(10,15,30,0) 60%)" }}></div>
      <WaveField color="rgba(56,189,248,0.07)" />

      <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ width: 56, height: 4, background: COL.accent, borderRadius: 2 }}></span>
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: 22, color: COL.tint, letterSpacing: "0.28em", textTransform: "uppercase" }}>Carrusel · Olavarría</span>
        </div>

        <div>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 320, color: COL.accent, lineHeight: 0.85, letterSpacing: "-0.06em" }}>5</div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 78, lineHeight: 0.98, letterSpacing: "-0.03em", margin: 0, marginTop: 8 }}>
            errores que cometen<br />los negocios de<br /><span style={{ color: COL.tint }}>Olavarría</span> en internet.
          </h1>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14, fontFamily: "'Inter', sans-serif", color: COL.cool, fontSize: 22 }}>
          Deslizá <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 40, height: 40, borderRadius: 999, background: "rgba(56,189,248,.15)", color: COL.tint }}>→</span>
        </div>
      </div>
    </CarouselFrame>
  );
}

// Slide content card used in 2/3/4
function MistakeSlide({ num, light, title, body, IconSvg, slideNum }) {
  const fg = light ? COL.navy : "#FFFFFF";
  const muted = light ? COL.slate : COL.cool;
  return (
    <CarouselFrame slideNum={slideNum} light={light}>
      <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{
            width: 96, height: 96, borderRadius: 24,
            background: light ? "#FFFFFF" : COL.surface,
            border: light ? "1px solid #E0F2FE" : "1px solid #1E293B",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: light ? "0 10px 30px -10px rgba(3,105,161,.18)" : "none",
          }}>
            <IconSvg />
          </div>
          <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 28, color: light ? COL.primary : COL.tint, letterSpacing: "0.04em" }}>
            ERROR {num}
          </div>
        </div>

        <div style={{ marginTop: 64 }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 96, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0, color: fg, textWrap: "balance" }}>
            {title}
          </h2>
        </div>

        <div style={{ marginTop: 40, maxWidth: 820, fontSize: 32, lineHeight: 1.35, color: muted, fontWeight: 400 }}>
          {body}
        </div>

        <div style={{ marginTop: "auto", display: "flex", alignItems: "center", gap: 12 }}>
          {[1, 2, 3, 4, 5].map(i => (
            <span key={i} style={{
              width: i === slideNum ? 48 : 12, height: 6, borderRadius: 999,
              background: i === slideNum ? COL.accent : (light ? "#CBD5E1" : "#1E293B"),
              transition: "all .3s",
            }}></span>
          ))}
        </div>
      </div>
    </CarouselFrame>
  );
}

const IconPin = () => (
  <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={COL.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-7 8-13a8 8 0 1 0-16 0c0 6 8 13 8 13z" />
    <circle cx="12" cy="9" r="3" />
  </svg>
);
const IconPhone = () => (
  <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={COL.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="6" y="2" width="12" height="20" rx="3" />
    <line x1="11" y1="18" x2="13" y2="18" />
  </svg>
);
const IconChat = () => (
  <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={COL.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a4 4 0 0 1-4 4H8l-5 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
  </svg>
);

function Carousel2() {
  return (
    <MistakeSlide
      num="01"
      light={true}
      slideNum={2}
      title={<>No estás en <span style={{ color: COL.primary }}>Google&nbsp;Maps</span>.</>}
      body={<>Si alguien busca “tu rubro en Olavarría”, no aparecés. Esa búsqueda se la lleva un competidor que sí cargó su ficha. Es gratis, y toma 20 minutos.</>}
      IconSvg={IconPin}
    />
  );
}
function Carousel3() {
  return (
    <MistakeSlide
      num="02"
      light={false}
      slideNum={3}
      title={<>Tu web tarda <span style={{ color: COL.tint }}>10 segundos</span> en abrir.</>}
      body={<>El 53% de la gente se va antes de que cargue. Cada segundo extra son clientes que ya están comprando en otro lado mientras tu sitio pelea con una imagen pesada.</>}
      IconSvg={IconPhone}
    />
  );
}
function Carousel4() {
  return (
    <MistakeSlide
      num="03"
      light={true}
      slideNum={4}
      title={<>Contestás los <span style={{ color: COL.primary }}>DMs</span> al otro día.</>}
      body={<>La gente decide en minutos, no en días. Si tu competencia responde en 3 minutos y vos en 14 horas, la venta ya se cerró sin vos.</>}
      IconSvg={IconChat}
    />
  );
}

// Slide 5 — CTA
function Carousel5() {
  return (
    <CarouselFrame slideNum={5}>
      <div style={{ position: "absolute", inset: 0, background: GRAD, opacity: 1 }}></div>
      <WaveField color="rgba(255,255,255,0.10)" />

      <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
        <Tag>Paso siguiente</Tag>

        <div>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 132, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            ¿Listo para<br /><span style={{ color: "#FDE68A" }}>crecer?</span>
          </h1>
          <div style={{ marginTop: 36, fontSize: 30, color: "#E0F2FE", maxWidth: 760, lineHeight: 1.35 }}>
            Diagnóstico gratis de tu presencia digital en Olavarría. Te decimos qué arreglar primero — sin vueltas.
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-start" }}>
          <CTAButton label="Escribinos por WhatsApp" size={1.15} />
        </div>
      </div>
    </CarouselFrame>
  );
}

Object.assign(window, {
  Feed1, Feed2, Feed3,
  Carousel1, Carousel2, Carousel3, Carousel4, Carousel5,
  CTAButton, FooterLogo, WaveField, COL, GRAD,
});
