const { useCurrentFrame, useVideoConfig, interpolate, spring, Sequence, AbsoluteFill, Img, staticFile } = require("remotion");

const BRAND = {
  bg: "#0C4A6E",
  accent: "#0EA5E9",
  cyan: "#06B6D4",
  orange: "#F97316",
  white: "#FFFFFF",
  dark: "#071E2E",
};

function Slide({ headline, subtext, eyebrow, color = BRAND.cyan, imgSrc }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const slideUp = interpolate(frame, [0, 18], [40, 0], { extrapolateRight: "clamp" });
  const subtextFade = interpolate(frame, [8, 22], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.bg, fontFamily: "sans-serif" }}>
      {/* Background image with overlay */}
      {imgSrc && (
        <AbsoluteFill>
          <img src={imgSrc} style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.35 }} />
          <AbsoluteFill style={{ background: `linear-gradient(to bottom, ${BRAND.bg}88 0%, ${BRAND.dark}EE 100%)` }} />
        </AbsoluteFill>
      )}

      {/* Top logo bar */}
      <div style={{
        position: "absolute", top: 72, left: 72, right: 72,
        display: "flex", alignItems: "center", gap: 16,
        opacity: fadeIn,
      }}>
        <div style={{
          width: 48, height: 48, borderRadius: 12,
          background: `linear-gradient(135deg, ${BRAND.accent}, ${BRAND.cyan})`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 22, fontWeight: 900, color: BRAND.white,
        }}>O</div>
        <span style={{ fontSize: 28, fontWeight: 700, color: BRAND.white, letterSpacing: 1 }}>
          OLA <span style={{ color: BRAND.cyan }}>Digital</span>
        </span>
      </div>

      {/* Content block — bottom third */}
      <div style={{
        position: "absolute", bottom: 180, left: 72, right: 72,
        opacity: fadeIn,
        transform: `translateY(${slideUp}px)`,
      }}>
        {eyebrow && (
          <div style={{
            fontSize: 28, fontWeight: 700, color: color,
            letterSpacing: 3, textTransform: "uppercase",
            marginBottom: 20,
          }}>{eyebrow}</div>
        )}
        <div style={{
          fontSize: 88, fontWeight: 900, color: BRAND.white,
          lineHeight: 1.05, marginBottom: 28,
          textShadow: "0 4px 24px rgba(0,0,0,0.5)",
        }}>{headline}</div>
        <div style={{
          fontSize: 46, fontWeight: 400, color: BRAND.cyan,
          lineHeight: 1.4, opacity: subtextFade,
        }}>{subtext}</div>
      </div>

      {/* Accent line */}
      <div style={{
        position: "absolute", bottom: 148, left: 72,
        width: interpolate(frame, [5, 25], [0, 200], { extrapolateRight: "clamp" }),
        height: 4, borderRadius: 2,
        background: `linear-gradient(to right, ${BRAND.orange}, ${BRAND.cyan})`,
      }} />
    </AbsoluteFill>
  );
}

function CounterSlide({ number, total, headline, detail }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 12, stiffness: 200 } });
  const textFade = interpolate(frame, [10, 24], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: BRAND.dark, fontFamily: "sans-serif" }}>
      {/* Big number */}
      <div style={{
        position: "absolute", top: "50%", left: 72,
        transform: `translateY(-50%) scale(${scale})`,
        transformOrigin: "left center",
        fontSize: 320, fontWeight: 900, lineHeight: 1,
        color: BRAND.accent, opacity: 0.12,
        userSelect: "none",
      }}>{number}</div>

      <div style={{
        position: "absolute", top: "50%", left: 72, right: 72,
        transform: "translateY(-50%)",
        opacity: textFade,
      }}>
        <div style={{
          fontSize: 44, fontWeight: 700, color: BRAND.orange,
          letterSpacing: 3, marginBottom: 24,
        }}>ERROR {number}/{total}</div>
        <div style={{
          fontSize: 86, fontWeight: 900, color: BRAND.white,
          lineHeight: 1.1, marginBottom: 28,
        }}>{headline}</div>
        <div style={{
          fontSize: 44, color: BRAND.cyan, lineHeight: 1.5,
        }}>{detail}</div>
      </div>
    </AbsoluteFill>
  );
}

function CtaSlide() {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const scale = spring({ frame, fps: 30, config: { damping: 14, stiffness: 180 } });

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(160deg, ${BRAND.bg} 0%, #071E2E 100%)`,
      fontFamily: "sans-serif",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
    }}>
      <div style={{ textAlign: "center", opacity: fadeIn, transform: `scale(${scale})` }}>
        <div style={{ fontSize: 44, color: BRAND.cyan, fontWeight: 700, letterSpacing: 2, marginBottom: 32 }}>
          ¿Te identificás?
        </div>
        <div style={{ fontSize: 90, fontWeight: 900, color: BRAND.white, lineHeight: 1.1, marginBottom: 40 }}>
          Nosotros{"\n"}
          <span style={{ color: BRAND.orange }}>lo arreglamos.</span>
        </div>
        <div style={{ fontSize: 46, color: BRAND.cyan, marginBottom: 64 }}>
          Escribinos por WhatsApp
        </div>
        {/* Logo */}
        <div style={{
          display: "flex", alignItems: "center", gap: 20,
          justifyContent: "center",
        }}>
          <div style={{
            width: 72, height: 72, borderRadius: 18,
            background: `linear-gradient(135deg, ${BRAND.accent}, ${BRAND.cyan})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 34, fontWeight: 900, color: BRAND.white,
          }}>O</div>
          <span style={{ fontSize: 42, fontWeight: 800, color: BRAND.white }}>
            OLA <span style={{ color: BRAND.cyan }}>Digital</span>
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
}

const SLIDES_DATA = [
  {
    type: "intro",
    eyebrow: "Olavarría · Buenos Aires",
    headline: "5 errores que te cuestan clientes",
    subtext: "¿Cuántos estás cometiendo vos?",
  },
  { type: "counter", number: 1, total: 5, headline: "Foto de producto borrosa", detail: "Primera impresión = perdida." },
  { type: "counter", number: 2, total: 5, headline: "Sin precio en el post", detail: "El cliente no pregunta. Se va." },
  { type: "counter", number: 3, total: 5, headline: "Cero llamada a la acción", detail: "¿Qué querés que haga el que lo ve?" },
  { type: "counter", number: 4, total: 5, headline: "Publicás y desaparecés", detail: "El algoritmo castiga la irregularidad." },
  { type: "counter", number: 5, total: 5, headline: "No respondés rápido", detail: "Tardás 4 horas. El competidor, 4 minutos." },
  { type: "cta" },
];

const SLIDE_FRAMES = 90; // 3 seconds at 30fps

function OlaReel() {
  return (
    <>
      {SLIDES_DATA.map((slide, i) => (
        <Sequence key={i} from={i * SLIDE_FRAMES} durationInFrames={SLIDE_FRAMES}>
          {slide.type === "intro" && (
            <Slide
              eyebrow={slide.eyebrow}
              headline={slide.headline}
              subtext={slide.subtext}
            />
          )}
          {slide.type === "counter" && (
            <CounterSlide
              number={slide.number}
              total={slide.total}
              headline={slide.headline}
              detail={slide.detail}
            />
          )}
          {slide.type === "cta" && <CtaSlide />}
        </Sequence>
      ))}
    </>
  );
}

module.exports = { OlaReel, SLIDES_DATA, SLIDE_FRAMES };
