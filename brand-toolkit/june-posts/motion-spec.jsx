/* OLA Digital — Motion specification card
   Single artboard explaining the CSS keyframe system used across animated feeds + covers. */

function MotionSpec() {
  return (
    <div style={{ width: 1080, height: 1400, background: "#0A0F1E", color: "#FFFFFF", fontFamily: "'Inter', sans-serif", padding: 56, position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 50% at 10% 0%, rgba(14,165,233,.30) 0%, transparent 60%), radial-gradient(ellipse 50% 40% at 100% 100%, rgba(249,115,22,.18) 0%, transparent 60%)" }}></div>

      <div style={{ position: "relative", zIndex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Tag dark>Motion system</Tag>
          <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: COL.cool, letterSpacing: "0.18em" }}>animations.css</div>
        </div>

        <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, lineHeight: 0.96, letterSpacing: "-0.03em", margin: "32px 0 12px" }}>
          4 keyframes,<br />aplicados en <span style={{ color: COL.tint }}>todo</span>.
        </h1>
        <div style={{ fontSize: 22, color: COL.cool, maxWidth: 780, lineHeight: 1.4 }}>
          Cada feed post animado y cover de carrusel usa la misma timeline. Liviano, declarativo, sin librerías.
          Para exportar a Lottie: render el SVG y la timeline con bodymovin / lottiefiles converter.
        </div>

        {/* timeline */}
        <div style={{ marginTop: 40, background: "#111827", border: "1px solid #1E293B", borderRadius: 20, padding: 28 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: COL.cool, letterSpacing: "0.16em" }}>
            <span>0s</span><span>0.5s</span><span>1.0s</span><span>1.5s</span><span>2.0s</span>
          </div>
          <div style={{ marginTop: 8, height: 4, background: "#1E293B", borderRadius: 2 }}></div>

          {[
            { name: "ola-fade-up",      cls: ".ola-headline",       from: 0.15, to: 0.55, color: COL.tint,    desc: "Headline + cards entran fade + 28px ↑" },
            { name: "ola-draw",         cls: ".ola-wave path",      from: 0.25, to: 0.85, color: "#06B6D4",   desc: "Stroke-dashoffset → 0, 3 paths stagger 100ms" },
            { name: "ola-pulse-once",   cls: ".ola-cta",            from: 1.2,  to: 2.4,  color: COL.accent,  desc: "scale 1→1.06→1 con halo naranja" },
            { name: "ola-grad-shift",   cls: ".ola-grad",           from: 0.0,  to: 2.0,  color: "#FDE68A",   desc: "background-position oscilla 0%→100%, loop 4s", loop: true },
          ].map(t => (
            <div key={t.name} style={{ marginTop: 18 }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                <span style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontWeight: 600, fontSize: 16, color: t.color }}>@{t.name}</span>
                <span style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13, color: COL.cool }}>→ {t.cls}</span>
                {t.loop && <span style={{ marginLeft: 6, padding: "2px 8px", borderRadius: 6, background: "rgba(253,230,138,.15)", color: "#FDE68A", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 11, letterSpacing: "0.12em" }}>LOOP</span>}
              </div>
              <div style={{ position: "relative", height: 18, background: "#0F172A", borderRadius: 4, marginTop: 6 }}>
                <div style={{
                  position: "absolute",
                  left: `${(t.from / 2) * 100}%`,
                  width: `${((t.to - t.from) / 2) * 100}%`,
                  top: 0, bottom: 0,
                  background: `linear-gradient(90deg, ${t.color} 0%, ${t.color}55 100%)`,
                  borderRadius: 4,
                  boxShadow: `0 0 18px ${t.color}55`,
                }}></div>
              </div>
              <div style={{ fontSize: 15, color: "#CBD5E1", marginTop: 6 }}>{t.desc}</div>
            </div>
          ))}
        </div>

        {/* easings */}
        <div style={{ marginTop: 28, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
          {[
            { name: "fade-up / cta", ease: "cubic-bezier(.22,1,.36,1)" },
            { name: "wave draw",     ease: "cubic-bezier(.65,0,.35,1)" },
            { name: "gradient",      ease: "ease-in-out (loop)" },
          ].map(e => (
            <div key={e.name} style={{ background: "#111827", border: "1px solid #1E293B", borderRadius: 14, padding: 18 }}>
              <div style={{ fontSize: 14, color: COL.cool, letterSpacing: "0.16em", textTransform: "uppercase", fontWeight: 600 }}>{e.name}</div>
              <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 15, color: COL.tint, marginTop: 8 }}>{e.ease}</div>
            </div>
          ))}
        </div>

        {/* how to use */}
        <div style={{ marginTop: 28, background: "#111827", border: "1px solid #1E293B", borderRadius: 18, padding: 24, fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 15, color: "#E0F2FE", lineHeight: 1.6 }}>
          <div style={{ color: COL.cool, marginBottom: 8 }}>// uso en cualquier artboard:</div>
          <div>&lt;div className=<span style={{ color: "#FDE68A" }}>"ola-anim"</span>&gt;</div>
          <div>&nbsp;&nbsp;&lt;div className=<span style={{ color: "#FDE68A" }}>"ola-grad"</span> style=&#123;{`{`}background: GRAD&#125;{`}`}/&gt;</div>
          <div>&nbsp;&nbsp;&lt;h1 className=<span style={{ color: "#FDE68A" }}>"ola-headline"</span>&gt;...&lt;/h1&gt;</div>
          <div>&nbsp;&nbsp;&lt;svg className=<span style={{ color: "#FDE68A" }}>"ola-wave"</span>&gt;...&lt;/svg&gt;</div>
          <div>&nbsp;&nbsp;&lt;button className=<span style={{ color: "#FDE68A" }}>"ola-cta"</span>&gt;...&lt;/button&gt;</div>
          <div>&lt;/div&gt;</div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { MotionSpec });
