/* OLA Digital — 5 NEW feed posts (1080×1080), all animated via .ola-anim
   Topics:
   1. ¿Cuántos clientes perdés porque no tenés web?
   2. Google Ads: plata que se convierte en clientes
   3. Tu competencia ya está en Instagram. ¿Y vos?
   4. Email marketing: el canal más barato que existe
   5. Reputación online — lo que dicen de vos cuando no estás
*/

// Helpers/shared tokens are on window: COL, GRAD, CTAButton, FooterLogo, Tag, WaveField

// Animated wave mark — drawing the three arcs
function AnimWave({ size = 64, color = "#FFFFFF" }) {
  return (
    <svg className="ola-wave" width={size} height={size} viewBox="0 0 100 100" fill="none" style={{ overflow: "visible" }}>
      <g stroke={color} strokeWidth="14" strokeLinecap="round" fill="none">
        <path d="M8 72 Q 30 40, 50 50 T 92 38" />
        <path d="M8 60 Q 30 28, 50 38 T 92 26" />
        <path d="M8 48 Q 30 16, 50 26 T 92 14" />
      </g>
    </svg>
  );
}

// ─── Feed 4: ¿Cuántos clientes perdés porque no tenés web? ─────────────
function Feed4() {
  return (
    <div className="ola-anim" style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: COL.navyBg, color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      <div className="ola-grad" style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(135deg, #0C4A6E 0%, #0369A1 50%, #0EA5E9 100%)",
        opacity: 0.4,
      }}></div>
      <WaveField color="rgba(56,189,248,0.08)" />

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag dark>Sin web · sin clientes</Tag>
          <FooterLogo />
        </div>

        <div className="ola-headline" style={{ marginTop: 56 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 116, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            ¿Cuántos<br />clientes <span style={{ color: "#FCA5A5" }}>perdés</span><br />porque no<br />tenés <span style={{ color: COL.tint }}>web?</span>
          </h1>
        </div>

        {/* big leak counter */}
        <div className="ola-headline delay-2" style={{ marginTop: 36, background: "rgba(15,23,42,.65)", border: "1px solid #1E293B", borderRadius: 24, padding: 32, display: "flex", alignItems: "center", gap: 28, backdropFilter: "blur(8px)" }}>
          <div>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 14, color: COL.cool, letterSpacing: "0.16em", textTransform: "uppercase" }}>Promedio en Olavarría</div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 6 }}>
              <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 112, color: "#FCA5A5", lineHeight: 1, letterSpacing: "-0.04em" }}>17</span>
              <span style={{ fontSize: 26, color: "#FFFFFF", fontWeight: 600 }}>consultas / mes</span>
            </div>
            <div style={{ marginTop: 4, fontSize: 20, color: COL.cool }}>que se van con la competencia.</div>
          </div>
          {/* dripping drops */}
          <svg width="120" height="160" viewBox="0 0 60 80" style={{ marginLeft: "auto" }}>
            <g fill="#FCA5A5">
              <path d="M30 8 C 24 18, 18 28, 18 38 a12 12 0 0 0 24 0 C 42 28, 36 18, 30 8z" opacity="0.95" />
              <circle cx="14" cy="62" r="4" opacity="0.6" />
              <circle cx="44" cy="68" r="3" opacity="0.45" />
              <circle cx="28" cy="76" r="2.4" opacity="0.3" />
            </g>
          </svg>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 22, color: COL.cool, lineHeight: 1.3, maxWidth: 460 }}>Una web hecha bien se paga sola<br />en menos de 60 días.</div>
          <div className="ola-cta"><CTAButton /></div>
        </div>
      </div>
    </div>
  );
}

// ─── Feed 5: Google Ads ─────────────────────────────────────────────────
function Feed5() {
  return (
    <div className="ola-anim" style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      <div className="ola-grad" style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(135deg, #0C4A6E 0%, #0369A1 30%, #0EA5E9 65%, #06B6D4 100%)",
      }}></div>
      <WaveField color="rgba(255,255,255,0.08)" />

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag>Google Ads</Tag>
          <FooterLogo />
        </div>

        <div className="ola-headline" style={{ marginTop: 56 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0 }}>
            Plata que<br />se convierte<br />en <span style={{ color: "#FDE68A" }}>clientes</span>.
          </h1>
        </div>

        {/* peso → person flow */}
        <div className="ola-headline delay-2" style={{ marginTop: 48, background: "rgba(255,255,255,.10)", border: "1px solid rgba(255,255,255,.20)", borderRadius: 24, padding: 28, backdropFilter: "blur(10px)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, color: "#FFFFFF", lineHeight: 1 }}>$1</div>
              <div style={{ fontSize: 18, color: "#BAE6FD", marginTop: 6 }}>invertido</div>
            </div>
            <svg width="100" height="40" viewBox="0 0 100 40" fill="none">
              <path d="M4 20 L86 20" stroke="#FDE68A" strokeWidth="3" strokeLinecap="round" strokeDasharray="6 6" />
              <path d="M76 8 L92 20 L76 32" stroke="#FDE68A" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            </svg>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 72, color: "#FDE68A", lineHeight: 1 }}>$4–7</div>
              <div style={{ fontSize: 18, color: "#FFFFFF", marginTop: 6 }}>de retorno</div>
            </div>
          </div>
          <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid rgba(255,255,255,.18)", display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
            {[
              ["Solo a tu zona", "Olavarría + 50km"],
              ["Solo tu rubro", "Buscando lo que vendés"],
              ["Pagás por click", "No por mostrar"],
            ].map(([t, d]) => (
              <div key={t}>
                <div style={{ fontWeight: 700, fontSize: 19, color: "#FFFFFF" }}>{t}</div>
                <div style={{ fontSize: 15, color: "#BAE6FD", marginTop: 4 }}>{d}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 22, color: "#BAE6FD", lineHeight: 1.3, maxWidth: 460 }}>Llegan clientes nuevos<br />desde el primer día.</div>
          <div className="ola-cta"><CTAButton /></div>
        </div>
      </div>
    </div>
  );
}

// ─── Feed 6: Tu competencia ya está en Instagram ────────────────────────
function MiniPostCard({ avatar, name, label, image, dark }) {
  return (
    <div style={{ background: dark ? "#111827" : "#FFFFFF", borderRadius: 18, overflow: "hidden", border: dark ? "1px solid #1E293B" : "1px solid #E5E7EB", boxShadow: "0 20px 50px -20px rgba(2,8,30,.45)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 14px" }}>
        <div style={{ width: 36, height: 36, borderRadius: 999, background: avatar, border: `2px solid ${dark ? COL.tint : COL.primary}` }}></div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, color: dark ? "#FFFFFF" : COL.navy }}>{name}</div>
          <div style={{ fontSize: 11, color: dark ? COL.cool : COL.slate }}>{label}</div>
        </div>
        <span style={{ marginLeft: "auto", color: dark ? "#FFFFFF" : COL.navy, fontWeight: 700, letterSpacing: 2 }}>···</span>
      </div>
      <div style={{ height: 200, background: image, position: "relative" }}>
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0) 60%, rgba(0,0,0,.4))" }}></div>
      </div>
      <div style={{ padding: "10px 14px 14px", display: "flex", alignItems: "center", gap: 12, color: dark ? "#FFFFFF" : COL.navy }}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="M12 21s-7-4.5-9.5-9C.9 9.4 1.9 5.7 5 4.6c2-.7 4.1.1 5.3 1.7l1.7 2 1.7-2C14.9 4.7 17 3.9 19 4.6c3.1 1.1 4.1 4.8 2.5 7.4C19 16.5 12 21 12 21z" /></svg>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="M21 15a4 4 0 0 1-4 4H8l-5 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" /></svg>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" /></svg>
        <span style={{ marginLeft: "auto", fontSize: 13, fontWeight: 600, color: dark ? COL.cool : COL.slate }}>2.4k</span>
      </div>
    </div>
  );
}

function Feed6() {
  return (
    <div className="ola-anim" style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: COL.navyBg, color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      <div className="ola-grad" style={{
        position: "absolute", inset: 0,
        background: "radial-gradient(ellipse 80% 60% at 30% 20%, rgba(14,165,233,.40) 0%, rgba(10,15,30,0) 60%), radial-gradient(ellipse 70% 50% at 90% 90%, rgba(6,182,212,.30) 0%, rgba(10,15,30,0) 60%)",
      }}></div>

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag dark>Instagram</Tag>
          <FooterLogo />
        </div>

        <div className="ola-headline" style={{ marginTop: 48 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 112, lineHeight: 0.96, letterSpacing: "-0.04em", margin: 0 }}>
            Tu <span style={{ color: COL.tint }}>competencia</span><br />ya está acá.<br /><span style={{ color: "#FDE68A" }}>¿Y vos?</span>
          </h1>
        </div>

        {/* two mini posts */}
        <div className="ola-headline delay-2" style={{ marginTop: 36, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, alignItems: "start" }}>
          <div style={{ transform: "rotate(-2deg)" }}>
            <MiniPostCard
              avatar="linear-gradient(135deg, #F97316, #FBBF24)"
              name="@panaderia.lacompetencia"
              label="Olavarría · 2 h"
              image="linear-gradient(135deg, #92400E, #FBBF24, #FDE68A)"
            />
            <div style={{ marginTop: 12, fontSize: 14, color: "#22C55E", fontFamily: "'JetBrains Mono', ui-monospace, monospace", letterSpacing: "0.12em" }}>● POSTEANDO 3×/SEMANA</div>
          </div>
          <div style={{ transform: "rotate(2deg)" }}>
            <MiniPostCard
              avatar="#334155"
              name="@tu.negocio"
              label="último post: 2024"
              image="repeating-linear-gradient(45deg, #1E293B 0 20px, #111827 20px 40px)"
              dark
            />
            <div style={{ marginTop: 12, fontSize: 14, color: "#EF4444", fontFamily: "'JetBrains Mono', ui-monospace, monospace", letterSpacing: "0.12em" }}>● SIN ACTIVIDAD HACE 14 MESES</div>
          </div>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 22, color: COL.cool, lineHeight: 1.3, maxWidth: 460 }}>Te armamos contenido que la gente<br />de Olavarría sí quiere ver.</div>
          <div className="ola-cta"><CTAButton /></div>
        </div>
      </div>
    </div>
  );
}

// ─── Feed 7: Email marketing ───────────────────────────────────────────
function Feed7() {
  return (
    <div className="ola-anim" style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: COL.ice, color: COL.navy, fontFamily: "'Inter', sans-serif" }}>
      {/* abstract gradient corner */}
      <div className="ola-grad" style={{
        position: "absolute", top: -200, right: -200, width: 800, height: 800, borderRadius: 999,
        background: "linear-gradient(135deg, #0EA5E9, #06B6D4, #38BDF8)",
        filter: "blur(40px)", opacity: 0.5,
      }}></div>

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag dark>Email marketing</Tag>
          <FooterLogo light={false} />
        </div>

        <div className="ola-headline" style={{ marginTop: 56 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 124, lineHeight: 0.94, letterSpacing: "-0.04em", margin: 0, color: COL.navy }}>
            El canal<br />más <span style={{ color: COL.primary }}>barato</span><br />que existe.
          </h1>
        </div>

        {/* inbox mock */}
        <div className="ola-headline delay-2" style={{ marginTop: 40, background: "#FFFFFF", borderRadius: 22, padding: 8, boxShadow: "0 30px 70px -25px rgba(3,105,161,.25)", border: "1px solid #E0F2FE" }}>
          {[
            { from: "Vos · tunegocio.com.ar", subj: "Promo de invierno — 20% off solo esta semana", time: "9:02", unread: true, badge: "+$48.300" },
            { from: "Vos · tunegocio.com.ar", subj: "Volvieron las empanadas de los jueves 🌮", time: "ayer", unread: true, badge: "+12 pedidos" },
            { from: "Vos · tunegocio.com.ar", subj: "Hola Juan, te extrañamos — vení con un café gratis", time: "lun", unread: false, badge: "abierto" },
          ].map((m, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 18, padding: "20px 22px",
              borderBottom: i < 2 ? "1px solid #F0F9FF" : "none",
              background: m.unread ? "#F0F9FF" : "transparent",
            }}>
              <div style={{ width: 12, height: 12, borderRadius: 999, background: m.unread ? COL.primary : "transparent", flexShrink: 0 }}></div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
                  <span style={{ fontWeight: 700, fontSize: 17, color: COL.navy }}>{m.from}</span>
                  <span style={{ marginLeft: "auto", fontSize: 14, color: COL.cool, fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>{m.time}</span>
                </div>
                <div style={{ fontSize: 18, color: m.unread ? COL.navy : COL.slate, marginTop: 4, fontWeight: m.unread ? 600 : 400, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {m.subj}
                </div>
              </div>
              <div style={{ background: COL.accent, color: "#FFFFFF", padding: "8px 14px", borderRadius: 999, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 16, whiteSpace: "nowrap" }}>{m.badge}</div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 22, color: COL.slate, lineHeight: 1.3, maxWidth: 480 }}>
            <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, color: COL.navy }}>$42×</span> de retorno por cada peso<br />invertido. Sí, leíste bien.
          </div>
          <div className="ola-cta"><CTAButton /></div>
        </div>
      </div>
    </div>
  );
}

// ─── Feed 8: Reputación online ─────────────────────────────────────────
function Star({ filled, color = "#F59E0B" }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill={filled ? color : "none"} stroke={color} strokeWidth="1.8" strokeLinejoin="round">
      <path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z" />
    </svg>
  );
}

function Feed8() {
  return (
    <div className="ola-anim" style={{ width: 1080, height: 1350, position: "relative", overflow: "hidden", background: COL.navyBg, color: "#FFFFFF", fontFamily: "'Inter', sans-serif" }}>
      <div className="ola-grad" style={{
        position: "absolute", inset: 0,
        background: "radial-gradient(ellipse 50% 40% at 50% 30%, rgba(245,158,11,.20) 0%, rgba(10,15,30,0) 65%), radial-gradient(ellipse 60% 50% at 80% 95%, rgba(14,165,233,.30) 0%, rgba(10,15,30,0) 65%)",
      }}></div>

      <div style={{ position: "absolute", inset: 0, padding: 80, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Tag dark>Reputación online</Tag>
          <FooterLogo />
        </div>

        <div className="ola-headline" style={{ marginTop: 48 }}>
          <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 104, lineHeight: 0.96, letterSpacing: "-0.04em", margin: 0 }}>
            Lo que dicen<br />de vos cuando<br /><span style={{ color: COL.tint }}>no estás</span>.
          </h1>
        </div>

        {/* review cards stack */}
        <div className="ola-headline delay-2" style={{ marginTop: 32, display: "flex", flexDirection: "column", gap: 16 }}>
          {/* bad */}
          <div style={{ background: "#111827", border: "1px solid #1E293B", borderLeft: `4px solid #EF4444`, borderRadius: 16, padding: "20px 24px", transform: "rotate(-0.6deg)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {[1,1,0,0,0].map((f, i) => <Star key={i} filled={!!f} color="#EF4444" />)}
              <span style={{ marginLeft: 8, fontSize: 14, color: COL.cool, fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>· hace 3 semanas</span>
            </div>
            <div style={{ fontSize: 22, color: "#FFFFFF", marginTop: 8, lineHeight: 1.3 }}>"Mandé un mensaje el viernes, todavía no me contestaron. Lo terminé comprando en otro lado."</div>
          </div>
          {/* good */}
          <div style={{ background: "linear-gradient(135deg, #0369A1, #0EA5E9)", borderRadius: 16, padding: "22px 26px", transform: "rotate(0.6deg)", boxShadow: "0 30px 60px -25px rgba(3,105,161,.6)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {[1,1,1,1,1].map((f, i) => <Star key={i} filled={!!f} color="#FDE68A" />)}
              <span style={{ marginLeft: 8, fontSize: 14, color: "#BAE6FD", fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>· hace 2 días · verificado</span>
            </div>
            <div style={{ fontSize: 22, color: "#FFFFFF", marginTop: 8, lineHeight: 1.3, fontWeight: 500 }}>"Atención impecable, te contestan al toque y resolvieron todo por WhatsApp. 100% recomendable."</div>
          </div>
          {/* meh */}
          <div style={{ background: "#111827", border: "1px solid #1E293B", borderLeft: `4px solid ${COL.accentAlt}`, borderRadius: 16, padding: "20px 24px", transform: "rotate(-0.3deg)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {[1,1,1,0,0].map((f, i) => <Star key={i} filled={!!f} color={COL.accentAlt} />)}
              <span style={{ marginLeft: 8, fontSize: 14, color: COL.cool, fontFamily: "'JetBrains Mono', ui-monospace, monospace" }}>· hace 1 mes</span>
            </div>
            <div style={{ fontSize: 22, color: "#FFFFFF", marginTop: 8, lineHeight: 1.3 }}>"El producto está bien pero la página web no funcionaba en el celu, tuve que llamarlos."</div>
          </div>
        </div>

        <div style={{ marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 22, color: COL.cool, lineHeight: 1.3, maxWidth: 460 }}>Gestionamos reseñas, respuestas<br />y reputación. Todo.</div>
          <div className="ola-cta"><CTAButton /></div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Feed4, Feed5, Feed6, Feed7, Feed8, AnimWave });
