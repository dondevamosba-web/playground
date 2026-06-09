// Ola Digital — Main canvas app
// Uses DesignCanvas + DCSection + DCArtboard from design-canvas.jsx.
// Imports Post component, SINGLES, CAROUSELS from window.

const { useState, useEffect } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "showWa": true,
  "scale": "normal",
  "globalAccent": "auto",
  "carouselSlides": 4
}/*EDITMODE-END*/;

// ============ Style tile content ============
const Swatch = ({ name, hex, sub, dark }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
    <div style={{
      width: '100%', aspectRatio: '1.6/1', borderRadius: 16, background: hex,
      border: dark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.06)',
      boxShadow: '0 8px 28px rgba(0,0,0,0.08)',
    }}></div>
    <div>
      <div style={{ fontWeight: 800, fontSize: 18, color: '#0F172A', letterSpacing: '-0.01em' }}>{name}</div>
      <div style={{ fontWeight: 600, fontSize: 14, color: '#475569', fontFamily: 'ui-monospace, SF Mono, Menlo, monospace', marginTop: 4 }}>{hex}</div>
      {sub && <div style={{ fontSize: 13, color: '#64748b', marginTop: 6, lineHeight: 1.4 }}>{sub}</div>}
    </div>
  </div>
);

const StyleTile = () => (
  <div style={{
    width: '100%', height: '100%', padding: 56, background: '#fafaf7', overflow: 'hidden',
    fontFamily: 'Inter, system-ui, sans-serif', color: '#0F172A',
    display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: 'auto 1fr', gap: 36,
  }}>
    <div style={{ gridColumn: '1 / -1' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16 }}>
        <div style={{ fontWeight: 900, fontSize: 36, letterSpacing: '-0.02em' }}>OLA DIGITAL</div>
        <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: '0.18em', color: '#64748b', textTransform: 'uppercase' }}>Master Style Tile · v1</div>
      </div>
      <div style={{ marginTop: 8, fontSize: 16, color: '#64748b', maxWidth: 720 }}>
        Sistema visual para los 40 posts. Dark-first, geométrico, tipografía agresiva. Construido para que un diseñador (o IA) replique todo sin desviarse.
      </div>
    </div>

    <div>
      <div style={{ fontSize: 13, fontWeight: 800, letterSpacing: '0.2em', color: '#64748b', textTransform: 'uppercase', marginBottom: 16 }}>Paleta</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Swatch name="Navy / Fondo" hex="#0F172A" sub="Base de todos los posts. Nunca fondo claro." dark />
        <Swatch name="Electric Blue" hex="#0EA5E9" sub="Titulares, números de stat, íconos." />
        <Swatch name="Orange Pop" hex="#F97316" sub="UN solo dato hero o CTA por post. Nunca dos." />
        <Swatch name="White" hex="#FFFFFF" sub="Cuerpo principal. Apoyos al 62% / 42% de opacidad." />
      </div>
    </div>

    <div>
      <div style={{ fontSize: 13, fontWeight: 800, letterSpacing: '0.2em', color: '#64748b', textTransform: 'uppercase', marginBottom: 16 }}>Tipografía</div>
      <div style={{ background: '#0F172A', color: '#fff', borderRadius: 16, padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.2em', color: '#94a3b8', textTransform: 'uppercase', marginBottom: 4 }}>Inter · 900 / Stat</div>
          <div style={{ fontSize: 72, fontWeight: 900, lineHeight: 0.9, letterSpacing: '-0.05em', color: '#0EA5E9' }}>89%</div>
        </div>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.2em', color: '#94a3b8', textTransform: 'uppercase', marginBottom: 4 }}>Inter · 800 / H1</div>
          <div style={{ fontSize: 32, fontWeight: 800, lineHeight: 1, letterSpacing: '-0.025em' }}>Si no aparecés en Google, no existís.</div>
        </div>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.2em', color: '#94a3b8', textTransform: 'uppercase', marginBottom: 4 }}>Inter · 500 / Lede</div>
          <div style={{ fontSize: 16, fontWeight: 500, lineHeight: 1.3, color: 'rgba(255,255,255,0.62)' }}>Sin tu marca en Google Maps ya estás perdiendo clientes hoy mismo.</div>
        </div>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.2em', color: '#94a3b8', textTransform: 'uppercase', marginBottom: 4 }}>Inter · 700 / Eyebrow</div>
          <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: '0.22em', textTransform: 'uppercase', color: '#0EA5E9' }}>SEO LOCAL · BÚSQUEDAS</div>
        </div>
      </div>
    </div>

    <div style={{ gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 24 }}>
      <div>
        <div style={{ fontSize: 13, fontWeight: 800, letterSpacing: '0.2em', color: '#64748b', textTransform: 'uppercase', marginBottom: 12 }}>Espaciado · Grid</div>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, fontFamily: 'ui-monospace, SF Mono, monospace', fontSize: 13, lineHeight: 1.7, color: '#334155' }}>
          <div><b>Padding</b>: 56 / 64 px</div>
          <div><b>Cuerpo gap</b>: 28–40 px</div>
          <div><b>Border-radius</b>: 24 / 36 px</div>
          <div><b>Border-line</b>: rgba(255,255,255,0.10)</div>
        </div>
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 800, letterSpacing: '0.2em', color: '#64748b', textTransform: 'uppercase', marginBottom: 12 }}>Reglas de uso</div>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, fontSize: 14, lineHeight: 1.55, color: '#334155' }}>
          <div>• Naranja: <b>solo</b> en el dato hero o CTA. Nunca en cuerpo.</div>
          <div>• Wordmark “OLA DIGITAL” siempre top-left con dot azul.</div>
          <div>• Cada post tiene <b>una</b> idea fuerte. Si hay dos, son dos posts.</div>
          <div>• Stats con `tabular-nums`. Sin decimales innecesarios.</div>
        </div>
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 800, letterSpacing: '0.2em', color: '#64748b', textTransform: 'uppercase', marginBottom: 12 }}>7 layouts del sistema</div>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, fontSize: 14, lineHeight: 1.65, color: '#334155' }}>
          <div>1. <b>Stat</b> — número gigante</div>
          <div>2. <b>Hook</b> — ¿Sabías que…?</div>
          <div>3. <b>Bold</b> — manifesto tipográfico</div>
          <div>4. <b>List</b> — numerada 3–5 ítems</div>
          <div>5. <b>Before/After</b> — comparativa</div>
          <div>6. <b>Versus</b> — vos vs competencia</div>
          <div>7. <b>CTA</b> — cierre WhatsApp</div>
        </div>
      </div>
    </div>
  </div>
);

// ============ App ============
const App = () => {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // global accent override
  const accentFor = (post) => {
    if (t.globalAccent === 'blue') return 'blue';
    if (t.globalAccent === 'orange') return 'orange';
    return post.accent || 'blue';
  };

  // helper: render a single post into a fixed-size board
  const renderPost = (post, w, h, opts = {}) => (
    <div style={{ width: w, height: h, position: 'relative', background: '#0F172A' }}>
      <Post post={post} accent={accentFor(post)} scale={t.scale} showWa={t.showWa} />
    </div>
  );

  return (
    <>
      <DesignCanvas
        title="OLA DIGITAL — 40 posts para Instagram"
        subtitle="Olavarría · agencia de marketing digital · v1 · 16 single feed + 6 carousels × 4 slides"
      >
        <DCSection id="style-tile" title="Master Style Tile" subtitle="Colores, tipografía, reglas. Para replicar el sistema en cualquier post nuevo.">
          <DCArtboard id="tile" label="Sistema visual" width={1280} height={900}>
            <StyleTile />
          </DCArtboard>
        </DCSection>

        <DCSection id="singles" title="16 posts de feed · 1080 × 1080" subtitle="Rotan 6 plantillas: stat, hook, bold, list, versus, before/after. Una idea por post.">
          {SINGLES.map((post, i) => (
            <DCArtboard
              key={post.id}
              id={post.id}
              label={`${String(i + 1).padStart(2, '0')} · ${post.template.toUpperCase()} · ${post.category || ''}`}
              width={1080}
              height={1080}
            >
              {renderPost(post, 1080, 1080)}
            </DCArtboard>
          ))}
        </DCSection>

        {CAROUSELS.map((carousel, ci) => {
          const slidesToShow = t.carouselSlides === 3
            ? [...carousel.slides.slice(0, 2), carousel.slides[3]]
            : carousel.slides;
          return (
            <DCSection
              key={carousel.id}
              id={carousel.id}
              title={`Carrusel ${ci + 1} · ${carousel.title}`}
              subtitle={`1080 × 1350 · ${slidesToShow.length} slides · cierre siempre con CTA WhatsApp.`}
            >
              {slidesToShow.map((slide, si) => (
                <DCArtboard
                  key={slide.id}
                  id={slide.id}
                  label={`${carousel.id} · ${String(si + 1).padStart(2, '0')} · ${slide.template.toUpperCase()}`}
                  width={1080}
                  height={1350}
                >
                  {renderPost(slide, 1080, 1350)}
                </DCArtboard>
              ))}
            </DCSection>
          );
        })}
      </DesignCanvas>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Globales">
          <TweakRadio
            label="Acento global"
            value={t.globalAccent}
            options={[
              { value: 'auto', label: 'Auto' },
              { value: 'blue', label: 'Solo azul' },
              { value: 'orange', label: 'Solo naranja' },
            ]}
            onChange={(v) => setTweak('globalAccent', v)}
          />
          <TweakRadio
            label="Escala tipográfica"
            value={t.scale}
            options={[
              { value: 'normal', label: 'Normal' },
              { value: 'scream', label: 'Scream' },
            ]}
            onChange={(v) => setTweak('scale', v)}
          />
        </TweakSection>
        <TweakSection label="Carruseles">
          <TweakRadio
            label="Slides por carrusel"
            value={t.carouselSlides}
            options={[
              { value: 3, label: '3 slides' },
              { value: 4, label: '4 slides' },
            ]}
            onChange={(v) => setTweak('carouselSlides', v)}
          />
          <TweakToggle
            label="Ícono de WhatsApp en cierre"
            value={t.showWa}
            onChange={(v) => setTweak('showWa', v)}
          />
        </TweakSection>
      </TweaksPanel>
    </>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
