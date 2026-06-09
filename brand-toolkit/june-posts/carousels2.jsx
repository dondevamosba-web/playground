/* OLA Digital — 3 new carousels (5 slides each = 15 artboards)
   1. Cómo aparecer primero en Google en Olavarría
   2. Antes y después: negocios que crecieron con marketing digital
   3. ¿Cuánto cuesta NO tener presencia online?
*/

// Shared carousel frame (mirrors Carousel1's frame conventions)
function Frame({ light, slideNum, total = 5, children }) {
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
      }}>{String(slideNum).padStart(2,"0")} / {String(total).padStart(2,"0")}</div>
      <div style={{ position: "absolute", bottom: 36, right: 80 }}>
        <FooterLogo light={!light} />
      </div>
    </div>
  );
}

function Dots({ active, light }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      {[1,2,3,4,5].map(i => (
        <span key={i} style={{
          width: i === active ? 48 : 12, height: 6, borderRadius: 999,
          background: i === active ? COL.accent : (light ? "#CBD5E1" : "#1E293B"),
        }}></span>
      ))}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════
// CAROUSEL B — Cómo aparecer primero en Google en Olavarría
// ════════════════════════════════════════════════════════════════════════

function CarBCover() {
  return (
    <Frame slideNum={1}>
      <div className="ola-anim" style={{ position: "absolute", inset: 0 }}>
        <div className="ola-grad" style={{ position: "absolute", inset: 0, background: GRAD }}></div>
        <WaveField color="rgba(255,255,255,0.10)" />

        <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
          <Tag>Guía rápida · SEO local</Tag>

          {/* Fake search result with you ranked #1 */}
          <div>
            <div className="ola-headline" style={{ background: "rgba(255,255,255,.96)", color: COL.navy, borderRadius: 18, padding: "20px 26px", maxWidth: 720, boxShadow: "0 30px 60px -20px rgba(2,8,30,.4)", marginBottom: 36 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 16, color: COL.slate, fontWeight: 500 }}>
                <span style={{ width: 28, height: 28, borderRadius: 999, background: COL.accent, color: "#FFFFFF", display: "inline-flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 14 }}>1</span>
                tunegocio.com.ar · Olavarría
              </div>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 28, color: COL.primaryDark, marginTop: 6 }}>Tu Negocio — el mejor de Olavarría</div>
            </div>

            <h1 className="ola-headline delay-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 102, lineHeight: 0.94, letterSpacing: "-0.035em", margin: 0 }}>
              Cómo aparecer<br /><span style={{ color: "#FDE68A" }}>primero</span> en<br />Google en<br /><span style={{ color: COL.tint }}>Olavarría</span>.
            </h1>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 14, color: "rgba(255,255,255,.85)", fontSize: 22 }}>
            5 pasos · deslizá <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 40, height: 40, borderRadius: 999, background: "rgba(255,255,255,.15)" }}>→</span>
          </div>
        </div>
      </div>
    </Frame>
  );
}

function StepSlide({ slideNum, light, num, title, body, icon, accent }) {
  const fg = light ? COL.navy : "#FFFFFF";
  const muted = light ? COL.slate : COL.cool;
  return (
    <Frame slideNum={slideNum} light={light}>
      <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 200, lineHeight: 1,
            color: accent || (light ? COL.primary : COL.tint),
            letterSpacing: "-0.06em",
            opacity: 0.18,
            marginLeft: -16,
          }}>{String(num).padStart(2,"0")}</div>
          <div style={{ marginLeft: -130, fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 22, color: accent || (light ? COL.primary : COL.tint), letterSpacing: "0.18em", textTransform: "uppercase" }}>
            PASO {num}
          </div>
        </div>

        <div style={{ marginTop: 12 }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 92, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0, color: fg, textWrap: "balance" }}>
            {title}
          </h2>
        </div>

        <div style={{ marginTop: 36, maxWidth: 860, fontSize: 30, lineHeight: 1.35, color: muted, fontWeight: 400 }}>
          {body}
        </div>

        {icon && (
          <div style={{ marginTop: 32, alignSelf: "flex-start", background: light ? "#FFFFFF" : COL.surface, border: light ? "1px solid #E0F2FE" : "1px solid #1E293B", borderRadius: 18, padding: "16px 22px", fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 18, color: light ? COL.primaryDark : COL.tint, letterSpacing: "0.06em" }}>
            {icon}
          </div>
        )}

        <div style={{ marginTop: "auto" }}><Dots active={slideNum} light={light} /></div>
      </div>
    </Frame>
  );
}

function CarB2() { return <StepSlide slideNum={2} light={true}  num={1} title={<>Cargá tu <span style={{ color: COL.primary }}>Google Business Profile</span>.</>} body={<>Es gratis y es lo más importante. Foto, horarios, dirección, teléfono. Si no estás ahí, no existís para Google Maps.</>} icon="$ google.com/business" />; }
function CarB3() { return <StepSlide slideNum={3} light={false} num={2} title={<>Usá las palabras que <span style={{ color: COL.tint }}>busca la gente</span>.</>} body={<>“Plomero Olavarría”, no “servicios hidráulicos”. La gente busca como habla. Tu web tiene que sonar igual.</>} icon='# tag: "plomero olavarría"' />; }
function CarB4() { return <StepSlide slideNum={4} light={true}  num={3} title={<>Pedile <span style={{ color: COL.primary }}>reseñas</span> a tus clientes.</>} body={<>Cada estrella nueva te empuja más arriba. Mandales el link directo por WhatsApp — toma 30 segundos responder.</>} icon="★★★★★ +12 reseñas / mes" />; }
function CarB5() {
  return (
    <Frame slideNum={5}>
      <div className="ola-anim" style={{ position: "absolute", inset: 0 }}>
        <div className="ola-grad" style={{ position: "absolute", inset: 0, background: GRAD }}></div>
        <WaveField color="rgba(255,255,255,0.10)" />
        <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
          <Tag>Paso siguiente</Tag>
          <div>
            <h1 className="ola-headline" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
              Hagámoslo<br /><span style={{ color: "#FDE68A" }}>juntos</span>.
            </h1>
            <div style={{ marginTop: 36, fontSize: 28, color: "#E0F2FE", maxWidth: 780, lineHeight: 1.4 }}>
              Auditamos tu presencia en Google gratis. Te decimos exactamente qué te falta para subir.
            </div>
          </div>
          <div className="ola-cta" style={{ alignSelf: "flex-start" }}><CTAButton label="Pedí tu auditoría gratis" size={1.05} /></div>
        </div>
      </div>
    </Frame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// CAROUSEL C — Antes y después
// ════════════════════════════════════════════════════════════════════════

function CarCCover() {
  return (
    <Frame slideNum={1}>
      <div className="ola-anim" style={{ position: "absolute", inset: 0, background: COL.navyBg, color: "#FFFFFF" }}>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 80% 60% at 20% 80%, rgba(14,165,233,.40) 0%, rgba(10,15,30,0) 65%), radial-gradient(ellipse 60% 50% at 90% 20%, rgba(249,115,22,.20) 0%, rgba(10,15,30,0) 60%)" }}></div>

        <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <Tag dark>Casos reales · Olavarría</Tag>

          <div>
            <div className="ola-headline" style={{ display: "flex", alignItems: "baseline", gap: 24, marginBottom: 16, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800 }}>
              <span style={{ fontSize: 76, color: "#475569", textDecoration: "line-through", textDecorationColor: "#EF4444", textDecorationThickness: 6 }}>antes</span>
              <span style={{ fontSize: 76, color: COL.tint }}>→ después.</span>
            </div>
            <h1 className="ola-headline delay-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 84, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0 }}>
              Negocios de Olavarría<br />que <span style={{ color: "#FDE68A" }}>crecieron</span> con<br />marketing digital.
            </h1>
          </div>

          <Dots active={1} />
        </div>
      </div>
    </Frame>
  );
}

function BeforeAfterSlide({ slideNum, biz, sector, antes, despues, metric, light }) {
  const fg = light ? COL.navy : "#FFFFFF";
  const muted = light ? COL.slate : COL.cool;
  return (
    <Frame slideNum={slideNum} light={light}>
      <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ width: 64, height: 64, borderRadius: 14, background: light ? COL.primary : COL.tint, color: light ? "#FFFFFF" : COL.navyBg, display: "inline-flex", alignItems: "center", justifyContent: "center", fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 30 }}>
            {biz.slice(0,2).toUpperCase()}
          </div>
          <div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 32, color: fg, letterSpacing: "-0.02em" }}>{biz}</div>
            <div style={{ fontSize: 18, color: muted, letterSpacing: "0.16em", textTransform: "uppercase", fontWeight: 600 }}>{sector} · Olavarría</div>
          </div>
        </div>

        <div style={{ marginTop: 36, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div style={{ background: light ? "#FFFFFF" : COL.surface, border: light ? "1px solid #E2E8F0" : "1px solid #1E293B", borderRadius: 20, padding: 28 }}>
            <div style={{ fontSize: 16, color: "#EF4444", fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase" }}>ANTES</div>
            <ul style={{ margin: 0, marginTop: 14, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
              {antes.map((t, i) => (
                <li key={i} style={{ display: "flex", gap: 10, fontSize: 21, color: muted, lineHeight: 1.3 }}>
                  <span style={{ color: "#EF4444", fontWeight: 700 }}>×</span>{t}
                </li>
              ))}
            </ul>
          </div>
          <div style={{ background: "linear-gradient(160deg, #0369A1, #0EA5E9)", borderRadius: 20, padding: 28, color: "#FFFFFF", boxShadow: "0 30px 60px -25px rgba(3,105,161,.5)" }}>
            <div style={{ fontSize: 16, color: "#BAE6FD", fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase" }}>DESPUÉS</div>
            <ul style={{ margin: 0, marginTop: 14, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
              {despues.map((t, i) => (
                <li key={i} style={{ display: "flex", gap: 10, fontSize: 21, color: "#FFFFFF", lineHeight: 1.3 }}>
                  <span style={{ color: "#FDE68A", fontWeight: 700 }}>✓</span>{t}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* hero metric */}
        <div style={{ marginTop: 32, background: light ? "#0F172A" : "#FFFFFF", color: light ? "#FFFFFF" : COL.navy, borderRadius: 20, padding: "24px 30px", display: "flex", alignItems: "center", gap: 22 }}>
          <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 80, color: COL.accent, lineHeight: 1, letterSpacing: "-0.03em" }}>{metric.value}</span>
          <div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 24, lineHeight: 1.15 }}>{metric.label}</div>
            <div style={{ fontSize: 16, color: light ? "#94A3B8" : COL.slate, marginTop: 4 }}>{metric.window}</div>
          </div>
        </div>

        <div style={{ marginTop: "auto" }}><Dots active={slideNum} light={light} /></div>
      </div>
    </Frame>
  );
}

function CarC2() {
  return <BeforeAfterSlide
    slideNum={2} light={false}
    biz="Panadería del Centro" sector="Gastronomía"
    antes={["Sin Instagram activo", "Pedidos solo por teléfono", "Clientes de la cuadra"]}
    despues={["Reels 3×/semana", "Pedidos por WhatsApp", "Clientes de toda la ciudad"]}
    metric={{ value: "+62%", label: "facturación mensual", window: "primer trimestre con OLA" }}
  />;
}
function CarC3() {
  return <BeforeAfterSlide
    slideNum={3} light={true}
    biz="Estudio Contable Ríos" sector="Servicios profesionales"
    antes={["Sin web", "Boca a boca", "Consultas estancadas"]}
    despues={["Web + blog SEO", "Aparece en Google #1", "Agenda llena 2 meses"]}
    metric={{ value: "×4", label: "consultas calificadas", window: "en 6 meses" }}
  />;
}
function CarC4() {
  return <BeforeAfterSlide
    slideNum={4} light={false}
    biz="Casa Hogar Norte" sector="Retail · muebles"
    antes={["Foto del local en Facebook", "Sin reseñas", "Vendía solo presencial"]}
    despues={["Catálogo online", "4.8★ con 87 reseñas", "Envíos a toda la zona"]}
    metric={{ value: "+ $1,2M", label: "facturación en ventas online", window: "primeros 5 meses" }}
  />;
}
function CarC5() {
  return (
    <Frame slideNum={5}>
      <div className="ola-anim" style={{ position: "absolute", inset: 0 }}>
        <div className="ola-grad" style={{ position: "absolute", inset: 0, background: GRAD }}></div>
        <WaveField color="rgba(255,255,255,0.10)" />
        <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
          <Tag>Tu turno</Tag>
          <div>
            <h1 className="ola-headline" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 108, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
              ¿El próximo<br />caso sos <span style={{ color: "#FDE68A" }}>vos</span>?
            </h1>
            <div style={{ marginTop: 36, fontSize: 28, color: "#E0F2FE", maxWidth: 760, lineHeight: 1.4 }}>
              Charlemos 20 minutos. Te mostramos cómo armamos el plan para tu negocio.
            </div>
          </div>
          <div className="ola-cta" style={{ alignSelf: "flex-start" }}><CTAButton size={1.1} /></div>
        </div>
      </div>
    </Frame>
  );
}

// ════════════════════════════════════════════════════════════════════════
// CAROUSEL D — ¿Cuánto cuesta NO tener presencia online?
// ════════════════════════════════════════════════════════════════════════

function CarDCover() {
  return (
    <Frame slideNum={1}>
      <div className="ola-anim" style={{ position: "absolute", inset: 0, background: COL.navyBg, color: "#FFFFFF" }}>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 60% 50% at 80% 30%, rgba(252,165,165,.20) 0%, rgba(10,15,30,0) 65%), radial-gradient(ellipse 70% 50% at 10% 90%, rgba(14,165,233,.30) 0%, rgba(10,15,30,0) 60%)" }}></div>

        <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <Tag dark>El costo invisible</Tag>

          <div>
            <div className="ola-headline" style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 22, color: COL.tint, letterSpacing: "0.16em", marginBottom: 24 }}>
              SPOILER: NO ES CERO.
            </div>
            <h1 className="ola-headline delay-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 100, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
              ¿Cuánto cuesta<br /><span style={{ color: "#FCA5A5" }}>NO</span> tener<br />presencia <span style={{ color: COL.tint }}>online?</span>
            </h1>
          </div>

          <Dots active={1} />
        </div>
      </div>
    </Frame>
  );
}

function CostSlide({ slideNum, light, num, headline, cost, perWhat, body }) {
  const fg = light ? COL.navy : "#FFFFFF";
  const muted = light ? COL.slate : COL.cool;
  return (
    <Frame slideNum={slideNum} light={light}>
      <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: "'Inter', sans-serif", fontWeight: 700, fontSize: 22, color: light ? COL.primary : COL.tint, letterSpacing: "0.18em", textTransform: "uppercase" }}>
          <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 48, height: 48, borderRadius: 999, background: light ? COL.ice : COL.surface, color: light ? COL.primary : COL.tint, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800 }}>{num}</span>
          Lo que dejás de ganar
        </div>

        <div style={{ marginTop: 28 }}>
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 80, lineHeight: 0.98, letterSpacing: "-0.035em", margin: 0, color: fg, textWrap: "balance" }}>
            {headline}
          </h2>
        </div>

        {/* big cost */}
        <div style={{ marginTop: 32, display: "flex", alignItems: "baseline", gap: 16, paddingBottom: 24, borderBottom: light ? "2px solid #E2E8F0" : "2px solid #1E293B" }}>
          <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 140, color: COL.accent, lineHeight: 1, letterSpacing: "-0.04em" }}>{cost}</span>
          <span style={{ fontSize: 26, color: muted, fontWeight: 500 }}>{perWhat}</span>
        </div>

        <div style={{ marginTop: 28, maxWidth: 860, fontSize: 26, lineHeight: 1.4, color: muted }}>{body}</div>

        <div style={{ marginTop: "auto" }}><Dots active={slideNum} light={light} /></div>
      </div>
    </Frame>
  );
}

function CarD2() {
  return <CostSlide
    slideNum={2} light={true} num="01"
    headline={<>Cada cliente que no te <span style={{ color: COL.primary }}>encuentra</span>.</>}
    cost="$45.000" perWhat="por venta perdida (promedio en Olavarría)"
    body={<>Si 5 personas por semana te buscan y no aparecés, son <strong>$900.000</strong> al mes que cobra tu competencia, no vos.</>}
  />;
}
function CarD3() {
  return <CostSlide
    slideNum={3} light={false} num="02"
    headline={<>Cada hora que <span style={{ color: COL.tint }}>perdés</span> en redes mal usadas.</>}
    cost="20 hs" perWhat="por mes posteando sin estrategia"
    body={<>Tiempo que podría volver a tu negocio. Sin un plan, son posts que nadie ve. Con plan, son clientes que llegan.</>}
  />;
}
function CarD4() {
  return <CostSlide
    slideNum={4} light={true} num="03"
    headline={<>Cada reseña <span style={{ color: COL.primary }}>negativa</span> sin respuesta.</>}
    cost="−$280k" perWhat="en ventas potenciales por mes"
    body={<>El 88% de la gente lee reseñas antes de comprar. Una mala sin respuesta = clientes que ni te escriben.</>}
  />;
}
function CarD5() {
  return (
    <Frame slideNum={5}>
      <div className="ola-anim" style={{ position: "absolute", inset: 0 }}>
        <div className="ola-grad" style={{ position: "absolute", inset: 0, background: GRAD }}></div>
        <WaveField color="rgba(255,255,255,0.10)" />
        <div style={{ position: "absolute", inset: 0, padding: "80px 80px 130px", display: "flex", flexDirection: "column", justifyContent: "space-between", color: "#FFFFFF" }}>
          <Tag>Frená el goteo</Tag>
          <div>
            <h1 className="ola-headline" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 110, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
              No tener<br />presencia<br /><span style={{ color: "#FDE68A" }}>cuesta más</span><br />que tenerla.
            </h1>
            <div style={{ marginTop: 28, fontSize: 26, color: "#E0F2FE", maxWidth: 760, lineHeight: 1.4 }}>
              Calculemos tu costo real juntos. Sin compromiso, sin vueltas.
            </div>
          </div>
          <div className="ola-cta" style={{ alignSelf: "flex-start" }}><CTAButton label="Hablemos por WhatsApp" size={1.05} /></div>
        </div>
      </div>
    </Frame>
  );
}

Object.assign(window, {
  CarBCover, CarB2, CarB3, CarB4, CarB5,
  CarCCover, CarC2, CarC3, CarC4, CarC5,
  CarDCover, CarD2, CarD3, CarD4, CarD5,
});
