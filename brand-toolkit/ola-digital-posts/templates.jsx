// Ola Digital — reusable post layouts
// Each template takes a `post` object + optional `scale` ("normal" | "scream") and an `accent` ("blue" | "orange").
// Posts render inside a fixed 1080x1080 or 1080x1350 board, so we use raw px units —
// the artboard's CSS transform handles fitting.

const WaIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 2.1.55 4.15 1.6 5.96L2 22l4.25-1.11a9.86 9.86 0 0 0 5.79 1.84h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.86 9.86 0 0 0 12.04 2zm0 18.15c-1.7 0-3.36-.46-4.81-1.31l-.35-.21-2.52.66.67-2.46-.23-.36a8.2 8.2 0 1 1 15.21-4.34c0 4.52-3.68 8.2-8.2 8.2zm4.49-6.14c-.25-.12-1.46-.72-1.69-.8-.23-.08-.39-.12-.56.12-.16.25-.64.8-.78.96-.14.16-.29.18-.54.06-.25-.12-1.04-.38-1.98-1.22a7.4 7.4 0 0 1-1.37-1.7c-.14-.25-.02-.38.11-.5.11-.11.25-.29.37-.43.13-.14.16-.25.25-.41.08-.16.04-.31-.02-.43-.06-.12-.56-1.35-.77-1.85-.2-.49-.41-.42-.56-.43h-.48c-.16 0-.43.06-.66.31s-.86.84-.86 2.06c0 1.21.88 2.38 1 2.55.12.16 1.74 2.65 4.21 3.71.59.25 1.05.4 1.4.51.59.19 1.13.16 1.55.1.47-.07 1.46-.6 1.66-1.17.2-.58.2-1.07.14-1.18-.06-.1-.22-.16-.47-.28z"/>
  </svg>
);

const Header = ({ tag }) => (
  <div className="od-head">
    <div className="od-wordmark"><span className="dot"></span>OLA DIGITAL</div>
    {tag ? <div className="od-tag">{tag}</div> : null}
  </div>
);

const Foot = ({ left, right }) => (
  <div className="od-foot">
    <div>{left}</div>
    <div className="pagenum">{right}</div>
  </div>
);

// =============== TEMPLATE 1: Big Stat ===============
const TplStat = ({ post, scale = 'normal', accent = 'blue' }) => (
  <div className="od-post">
    <div className="od-grid-bg"></div>
    <div className="od-blob" style={{ width: 480, height: 480, top: -120, right: -120, opacity: accent === 'blue' ? 0.6 : 0.15 }}></div>
    <Header tag={post.category} />
    <div className="od-body">
      {post.eyebrow ? <div className={`od-eyebrow ${accent === 'orange' ? 'orange' : ''}`}>{post.eyebrow}</div> : null}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginBottom: 28 }}>
        <span className={`od-stat ${accent === 'orange' ? 'orange' : ''} ${scale === 'scream' ? 'scream' : ''}`}>
          {post.stat}
          {post.unit ? <span className="unit">{post.unit}</span> : null}
        </span>
      </div>
      <div className="od-h3" style={{ maxWidth: 880 }}>{post.headline}</div>
      {post.sub ? <p className="od-lede">{post.sub}</p> : null}
    </div>
    <Foot left={post.foot || 'oladigital.com.ar'} right={post.pagenum || ''} />
  </div>
);

// =============== TEMPLATE 2: Hook Question ===============
const TplHook = ({ post, scale = 'normal', accent = 'blue' }) => (
  <div className="od-post">
    <div className="od-grid-bg"></div>
    <Header tag={post.category} />
    <div className="od-body" style={{ justifyContent: 'flex-start', paddingTop: 80 }}>
      <div className={`od-eyebrow ${accent === 'orange' ? 'orange' : ''}`}>{post.eyebrow || '¿Sabías que?'}</div>
      <h2 className={`od-h1 ${scale === 'scream' ? 'scream' : ''}`}>
        {post.headlinePre}{' '}
        <span className={accent === 'orange' ? 'od-orange' : 'od-blue'}>{post.headlineHi}</span>
        {post.headlinePost ? <> {post.headlinePost}</> : null}
      </h2>
      {post.sub ? <p className="od-lede" style={{ maxWidth: 880 }}>{post.sub}</p> : null}
    </div>
    <Foot left={post.foot || 'Fuente: Google · BrightLocal'} right={post.pagenum || ''} />
  </div>
);

// =============== TEMPLATE 3: Bold Statement (type-only) ===============
const TplBold = ({ post, scale = 'normal', accent = 'blue' }) => (
  <div className="od-post" style={{ background: post.bg || 'var(--od-bg)' }}>
    {accent === 'orange'
      ? <div className="od-blob" style={{ width: 700, height: 700, bottom: -300, left: -200, background: 'radial-gradient(circle, rgba(249,115,22,0.5), transparent 60%)', opacity: 0.7 }}></div>
      : <div className="od-blob" style={{ width: 700, height: 700, bottom: -300, left: -200, opacity: 0.55 }}></div>}
    <Header tag={post.category} />
    <div className="od-body" style={{ justifyContent: 'center' }}>
      <h2 className={`od-h1 ${scale === 'scream' ? 'scream' : ''}`} style={{ fontSize: scale === 'scream' ? 150 : 116, maxWidth: 920 }}>
        {post.lines ? post.lines.map((line, i) => (
          <div key={i} style={{ color: line.hi ? (accent === 'orange' ? 'var(--od-orange)' : 'var(--od-blue)') : 'var(--od-white)' }}>
            {line.text}
          </div>
        )) : post.headline}
      </h2>
      {post.sub ? <p className="od-lede">{post.sub}</p> : null}
    </div>
    <Foot left={post.foot || 'Ola Digital · Olavarría'} right={post.pagenum || ''} />
  </div>
);

// =============== TEMPLATE 4: Numbered List ===============
const TplList = ({ post, scale = 'normal', accent = 'blue' }) => (
  <div className="od-post">
    <div className="od-grid-bg"></div>
    <Header tag={post.category} />
    <div className="od-body" style={{ justifyContent: 'flex-start', paddingTop: 56, gap: 36 }}>
      <div>
        <div className={`od-eyebrow ${accent === 'orange' ? 'orange' : ''}`}>{post.eyebrow}</div>
        <h2 className="od-h2" style={{ maxWidth: 880 }}>{post.headline}</h2>
      </div>
      <ol className="od-list">
        {post.items.map((it, i) => (
          <li key={i}>
            <span className={`num ${accent === 'orange' ? 'orange' : ''}`}>{String(i + 1).padStart(2, '0')}</span>
            <div>
              <div className="item-title">{it.title}</div>
              {it.sub ? <span className="item-sub">{it.sub}</span> : null}
            </div>
          </li>
        ))}
      </ol>
    </div>
    <Foot left={post.foot || 'oladigital.com.ar'} right={post.pagenum || ''} />
  </div>
);

// =============== TEMPLATE 5: Before / After ===============
const TplBeforeAfter = ({ post, scale = 'normal', accent = 'blue' }) => (
  <div className="od-post">
    <div className="od-grid-bg"></div>
    <Header tag={post.category} />
    <div className="od-body" style={{ gap: 36 }}>
      <div>
        <div className={`od-eyebrow ${accent === 'orange' ? 'orange' : ''}`}>{post.eyebrow || 'Caso real'}</div>
        <h2 className="od-h2" style={{ maxWidth: 880 }}>{post.headline}</h2>
      </div>
      <div className="od-ba">
        <div className="col">
          <div className="ba-label">Antes</div>
          <div>
            <div className="ba-val">{post.before.val}</div>
            <div className="ba-sub">{post.before.sub}</div>
          </div>
        </div>
        <div className="col after">
          <div className="ba-label">Después</div>
          <div>
            <div className="ba-val">{post.after.val}</div>
            <div className="ba-sub">{post.after.sub}</div>
          </div>
        </div>
      </div>
      {post.tag ? <div className="od-chip" style={{ alignSelf: 'flex-start' }}>{post.tag}</div> : null}
    </div>
    <Foot left={post.foot || 'Cliente real · Olavarría'} right={post.pagenum || ''} />
  </div>
);

// =============== TEMPLATE 6: Versus Competition ===============
const TplVersus = ({ post, scale = 'normal', accent = 'blue' }) => (
  <div className="od-post">
    <div className="od-grid-bg"></div>
    <Header tag={post.category} />
    <div className="od-body" style={{ gap: 40 }}>
      <div>
        <div className={`od-eyebrow ${accent === 'orange' ? 'orange' : ''}`}>{post.eyebrow || 'Vos vs tu competencia'}</div>
        <h2 className="od-h2" style={{ maxWidth: 880 }}>{post.headline}</h2>
      </div>
      <div className="od-vs">
        <div className="panel them">
          <div className="vs-eyebrow">Ellos</div>
          <div className="vs-body">{post.them}</div>
        </div>
        <div className="vs-arrow">→</div>
        <div className="panel you">
          <div className="vs-eyebrow">Vos</div>
          <div className="vs-body">{post.you}</div>
        </div>
      </div>
      {post.sub ? <p className="od-body-text" style={{ margin: 0 }}>{post.sub}</p> : null}
    </div>
    <Foot left={post.foot || 'oladigital.com.ar'} right={post.pagenum || ''} />
  </div>
);

// =============== TEMPLATE 7: CTA close ===============
const TplCTA = ({ post, scale = 'normal', accent = 'orange', showWa = true }) => (
  <div className="od-post">
    <div className="od-blob" style={{ width: 700, height: 700, top: -250, right: -250, opacity: 0.45 }}></div>
    <Header tag={post.category || 'Hablemos'} />
    <div className="od-body" style={{ gap: 32 }}>
      <div className="od-eyebrow orange">Tu próximo paso</div>
      <h2 className="od-h1" style={{ fontSize: scale === 'scream' ? 130 : 108, maxWidth: 920 }}>
        {post.line1}<br/>
        <span className="od-orange">{post.line2}</span>
      </h2>
      <p className="od-lede" style={{ maxWidth: 820, marginTop: 0 }}>{post.sub}</p>
      <div className="od-cta-card">
        <div className="od-cta-label">Escribinos por WhatsApp</div>
        <div className="od-cta-title">{post.ctaTitle || 'Diagnóstico gratis de tu marketing.'}</div>
        <div className="od-cta-row">
          <div className="od-cta-handle">@oladigital.ok</div>
          {showWa ? (
            <div className="od-wa-pill">
              <WaIcon />
              <span>+54 9 2284 · escribir</span>
            </div>
          ) : (
            <div className="od-wa-pill" style={{ background: '#0F172A' }}>oladigital.com.ar</div>
          )}
        </div>
      </div>
    </div>
    <Foot left={post.foot || '— diagnóstico sin costo —'} right={post.pagenum || ''} />
  </div>
);

// dispatch
const TEMPLATES = {
  stat: TplStat,
  hook: TplHook,
  bold: TplBold,
  list: TplList,
  beforeafter: TplBeforeAfter,
  versus: TplVersus,
  cta: TplCTA,
};

const Post = ({ post, accent, scale, showWa }) => {
  const T = TEMPLATES[post.template] || TplBold;
  return <T post={post} accent={accent || post.accent || 'blue'} scale={scale || 'normal'} showWa={showWa !== false} />;
};

Object.assign(window, { Post, TEMPLATES, TplStat, TplHook, TplBold, TplList, TplBeforeAfter, TplVersus, TplCTA, WaIcon });
