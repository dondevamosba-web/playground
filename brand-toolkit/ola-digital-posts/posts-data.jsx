// Ola Digital — 40 Instagram posts
// 16 single feed posts (1080x1080) + 6 carousels × 4 slides (1080x1350) = 40
// All copy is rioplatense Spanish (vos/ustedes).

// ============ 16 SINGLE FEED POSTS (1080x1080) ============
const SINGLES = [
  // 01 — Big stat
  {
    id: 'S01', template: 'stat', accent: 'blue', category: 'SEO Local',
    eyebrow: 'Búsquedas locales',
    stat: '89', unit: '%',
    headline: 'De las búsquedas que no te encuentran, se las queda tu competencia.',
    sub: 'Si tu negocio no aparece en Google Maps, ya estás perdiendo clientes hoy.',
    foot: 'Fuente: BrightLocal 2024',
  },
  // 02 — Hook question
  {
    id: 'S02', template: 'hook', accent: 'blue', category: '¿Sabías que?',
    eyebrow: '¿Sabías que…?',
    headlinePre: 'El',
    headlineHi: '87%',
    headlinePost: 'de las búsquedas locales convierten en menos de 7 días.',
    sub: 'No es marketing a futuro. Es marketing que vende esta semana.',
    foot: 'Fuente: Google',
  },
  // 03 — Bold statement
  {
    id: 'S03', template: 'bold', accent: 'orange', category: 'Manifesto',
    lines: [
      { text: 'Si no aparecés' },
      { text: 'en Google,', hi: true },
      { text: 'no existís.' },
    ],
    sub: 'Duele. Pero así piensan tus clientes hoy.',
    foot: 'Ola Digital · Olavarría',
  },
  // 04 — List
  {
    id: 'S04', template: 'list', accent: 'blue', category: 'Errores',
    eyebrow: '3 errores caros',
    headline: 'Esto está matando tu Instagram esta semana.',
    items: [
      { title: 'Postear sin estrategia', sub: 'Subir “lo que se te ocurre” es ruido, no marca.' },
      { title: 'Ignorar los DMs', sub: 'Cada mensaje sin responder es una venta perdida.' },
      { title: 'No medir nada', sub: 'Si no sabés qué funciona, todo es suerte.' },
    ],
  },
  // 05 — Stat (orange hero)
  {
    id: 'S05', template: 'stat', accent: 'orange', category: 'Email Marketing',
    eyebrow: 'Retorno real',
    stat: '$42', unit: '',
    headline: 'Es lo que devuelve cada $1 que invertís en email marketing.',
    sub: 'El canal más rentable del mundo digital. Y casi nadie lo usa bien.',
    foot: 'Fuente: DMA · Litmus',
  },
  // 06 — Versus competencia
  {
    id: 'S06', template: 'versus', accent: 'blue', category: 'Competencia',
    eyebrow: 'Mientras leés esto',
    headline: 'Tu competencia ya está corriendo Google Ads. ¿Y vos?',
    them: 'Aparecen primeros cuando alguien busca tu servicio en Olavarría.',
    you: 'Aparecés en la página 2. O ni aparecés.',
    sub: 'El primer resultado de Google se lleva el 28% de los clics. El de página 2: casi cero.',
  },
  // 07 — Hook question (orange)
  {
    id: 'S07', template: 'hook', accent: 'orange', category: '¿Sabías que?',
    eyebrow: '¿Sabías que…?',
    headlinePre: 'Perdés',
    headlineHi: '17 consultas',
    headlinePost: 'por mes sin un sitio web profesional.',
    sub: 'Promedio en pymes de Olavarría que mandamos a auditar.',
    foot: 'Fuente: Auditorías internas 2024',
  },
  // 08 — Bold scream (orange hi)
  {
    id: 'S08', template: 'bold', accent: 'blue', category: 'Manifesto',
    lines: [
      { text: 'El boca a boca' },
      { text: 'ya no alcanza.', hi: true },
    ],
    sub: 'Tu mejor cliente está buscando en el celular ahora mismo.',
  },
  // 09 — List (4 items)
  {
    id: 'S09', template: 'list', accent: 'orange', category: 'Checklist',
    eyebrow: 'Checklist 2026',
    headline: '4 cosas que tu Instagram necesita hoy.',
    items: [
      { title: 'Bio que vende en 5 segundos', sub: 'Qué hacés, para quién, dónde estás.' },
      { title: 'Highlights organizados', sub: 'Servicios, precios, ubicación, opiniones.' },
      { title: 'Link funcional', sub: 'A WhatsApp o a tu sitio. No a la nada.' },
      { title: 'Una promesa, no diez', sub: 'Confunde menos, vende más.' },
    ],
  },
  // 10 — Stat
  {
    id: 'S10', template: 'stat', accent: 'blue', category: 'Google Ads',
    eyebrow: 'ROI promedio',
    stat: '$4–7', unit: '',
    headline: 'Vuelven por cada $1 que pongas en Google Ads bien armado.',
    sub: 'Mal armado: 0. La diferencia la hace el setup, no el presupuesto.',
    foot: 'Fuente: Google Economic Impact',
  },
  // 11 — Bold
  {
    id: 'S11', template: 'bold', accent: 'orange', category: 'Verdad incómoda',
    lines: [
      { text: 'Tus clientes' },
      { text: 'están en el celu.', hi: true },
      { text: '¿Y tu negocio?' },
    ],
    foot: 'Ola Digital · Olavarría',
  },
  // 12 — Hook
  {
    id: 'S12', template: 'hook', accent: 'blue', category: 'Errores',
    eyebrow: 'El error más común',
    headlinePre: 'Postear mucho',
    headlineHi: 'sin saber',
    headlinePost: 'a quién le hablás.',
    sub: 'Sin público claro, no hay mensaje. Sin mensaje, no hay ventas.',
    foot: 'Diagnóstico gratis por WhatsApp',
  },
  // 13 — Versus
  {
    id: 'S13', template: 'versus', accent: 'orange', category: 'Mentalidad',
    eyebrow: 'Dos formas de pensar',
    headline: 'Gastar en marketing vs. invertir en marketing.',
    them: '“Voy a probar 3 meses y veo.”',
    you: '“Mido cada peso y escalo lo que funciona.”',
    sub: 'La diferencia entre un costo y un sistema de ventas.',
  },
  // 14 — List
  {
    id: 'S14', template: 'list', accent: 'blue', category: 'Sitio Web',
    eyebrow: '5 señales',
    headline: 'Necesitás un sitio web ya, no el año que viene.',
    items: [
      { title: 'Te preguntan dirección y horario todo el día' },
      { title: 'Tu competencia tiene sitio y vos no' },
      { title: 'Querés cobrar online o agendar turnos' },
      { title: 'Tu Instagram no muestra todo lo que hacés' },
      { title: 'Te googlean y aparece cualquier cosa' },
    ],
  },
  // 15 — Before / After (single 1080)
  {
    id: 'S15', template: 'beforeafter', accent: 'blue', category: 'Caso real',
    eyebrow: 'Cliente · rubro gastronomía',
    headline: 'Lo que cambió en 90 días con un plan en serio.',
    before: { val: '5/mes', sub: 'Consultas por Instagram. Sin estrategia.' },
    after: { val: '47/mes', sub: 'Consultas reales. Con SEO local + ads.' },
    tag: '+840% consultas',
  },
  // 16 — Big stat scream
  {
    id: 'S16', template: 'stat', accent: 'orange', category: 'Sitio Web',
    eyebrow: 'Sin sitio web',
    stat: '17', unit: '/mes',
    headline: 'Consultas perdidas al mes en pymes sin web. Promedio Olavarría.',
    sub: 'No las recuperás. Se las lleva quien sí está online.',
    foot: 'Auditorías Ola Digital · 2024',
  },
];

// ============ 6 CAROUSELS × 4 SLIDES = 24 (1080x1350) ============
// Each carousel: 3 content slides + 1 CTA close (always last).

const CAROUSELS = [
  // ===== C1: SEO Local =====
  {
    id: 'C1', title: 'Por qué Google no te muestra',
    slides: [
      {
        id: 'C1-1', template: 'hook', accent: 'blue', category: 'Carrusel · 1/4', pagenum: '01 / 04',
        eyebrow: 'SEO Local',
        headlinePre: 'Por qué',
        headlineHi: 'Google no te muestra',
        headlinePost: 'a tus clientes en Olavarría.',
        sub: 'Deslizá →   3 razones + cómo arreglarlo.',
        foot: 'Ola Digital · SEO Local',
      },
      {
        id: 'C1-2', template: 'stat', accent: 'blue', category: 'Carrusel · 2/4', pagenum: '02 / 04',
        eyebrow: 'El problema',
        stat: '89', unit: '%',
        headline: 'De las búsquedas locales que no te encuentran, van a tu competencia.',
        sub: 'Y la mayoría compra en los próximos 7 días.',
        foot: 'Fuente: BrightLocal',
      },
      {
        id: 'C1-3', template: 'list', accent: 'blue', category: 'Carrusel · 3/4', pagenum: '03 / 04',
        eyebrow: '3 acciones',
        headline: 'Lo que hacemos para que Google te muestre.',
        items: [
          { title: 'Perfil de Google Business optimizado', sub: 'Categoría, horarios, fotos, palabras clave.' },
          { title: 'Reseñas reales y respondidas', sub: 'El factor #1 del ranking local.' },
          { title: 'Sitio rápido + datos estructurados', sub: 'Para que Google entienda qué vendés.' },
        ],
      },
      {
        id: 'C1-4', template: 'cta', accent: 'orange', category: 'Carrusel · 4/4', pagenum: '04 / 04',
        line1: '¿Querés que', line2: 'Google te encuentre?',
        sub: 'Te hacemos una auditoría de SEO local gratis. Sin compromiso, sin letra chica.',
        ctaTitle: 'Auditoría SEO local — gratis.',
      },
    ],
  },
  // ===== C2: Google Ads =====
  {
    id: 'C2', title: 'Google Ads: cuánto rinde',
    slides: [
      {
        id: 'C2-1', template: 'bold', accent: 'orange', category: 'Carrusel · 1/4', pagenum: '01 / 04',
        lines: [
          { text: 'Google Ads:' },
          { text: 'cuánto rinde', hi: true },
          { text: 'tu plata.' },
        ],
        sub: 'Deslizá →   números reales, no promesas.',
      },
      {
        id: 'C2-2', template: 'stat', accent: 'orange', category: 'Carrusel · 2/4', pagenum: '02 / 04',
        eyebrow: 'ROI promedio',
        stat: '$4–7', unit: '',
        headline: 'Vuelven por cada $1 invertido. Solo si está bien armado.',
        sub: 'Mal armado: quemás plata. Bien armado: es la palanca más rápida.',
        foot: 'Fuente: Google Economic Impact',
      },
      {
        id: 'C2-3', template: 'list', accent: 'orange', category: 'Carrusel · 3/4', pagenum: '03 / 04',
        eyebrow: 'Lo que cambia el resultado',
        headline: 'Lo que separa una campaña que vende de una que quema plata.',
        items: [
          { title: 'Palabras clave con intención de compra', sub: 'No “gastronomía”. Sí “pedidos parrilla Olavarría”.' },
          { title: 'Landing pensada para convertir', sub: 'Una sola promesa, un solo botón.' },
          { title: 'Medición real + optimización semanal', sub: 'Conversiones, no clicks vanidosos.' },
        ],
      },
      {
        id: 'C2-4', template: 'cta', accent: 'orange', category: 'Carrusel · 4/4', pagenum: '04 / 04',
        line1: 'Tirá tu presupuesto.', line2: 'Te decimos cuánto rinde.',
        sub: 'Te armamos una proyección concreta para tu rubro y tu zona, sin compromiso.',
        ctaTitle: 'Proyección de Google Ads — gratis.',
      },
    ],
  },
  // ===== C3: Email Marketing =====
  {
    id: 'C3', title: 'Email: la red social más rentable',
    slides: [
      {
        id: 'C3-1', template: 'hook', accent: 'orange', category: 'Carrusel · 1/4', pagenum: '01 / 04',
        eyebrow: 'Email marketing',
        headlinePre: 'El email no murió.',
        headlineHi: 'Está rindiendo',
        headlinePost: 'más que nunca.',
        sub: 'Deslizá →   por qué casi nadie lo usa bien.',
      },
      {
        id: 'C3-2', template: 'stat', accent: 'orange', category: 'Carrusel · 2/4', pagenum: '02 / 04',
        eyebrow: 'Retorno promedio',
        stat: '$42', unit: '',
        headline: 'Por cada $1 que invertís en email. Más que cualquier otro canal.',
        sub: 'Sin algoritmo. Sin pagar alcance. Sin depender de una red social.',
        foot: 'Fuente: DMA · Litmus',
      },
      {
        id: 'C3-3', template: 'list', accent: 'orange', category: 'Carrusel · 3/4', pagenum: '03 / 04',
        eyebrow: 'Cómo funciona acá',
        headline: 'Lo que armamos para tu negocio en 30 días.',
        items: [
          { title: 'Lista propia (no comprada)', sub: 'Capturada con un incentivo real.' },
          { title: 'Secuencia de bienvenida automática', sub: 'Vende mientras dormís.' },
          { title: 'Campañas mensuales con oferta clara', sub: 'Una promesa por email, no diez.' },
        ],
      },
      {
        id: 'C3-4', template: 'cta', accent: 'orange', category: 'Carrusel · 4/4', pagenum: '04 / 04',
        line1: '¿Empezamos a', line2: 'construir tu lista?',
        sub: 'Te mostramos cuánto valdría una lista de 1.000 clientes propios para tu negocio.',
        ctaTitle: 'Asesoría de email marketing — gratis.',
      },
    ],
  },
  // ===== C4: Sitio Web =====
  {
    id: 'C4', title: 'Sin web, perdés clientes',
    slides: [
      {
        id: 'C4-1', template: 'bold', accent: 'blue', category: 'Carrusel · 1/4', pagenum: '01 / 04',
        lines: [
          { text: 'Sin sitio web,' },
          { text: 'perdés clientes', hi: true },
          { text: 'todos los días.' },
        ],
        sub: 'Deslizá →   números reales de Olavarría.',
      },
      {
        id: 'C4-2', template: 'stat', accent: 'orange', category: 'Carrusel · 2/4', pagenum: '02 / 04',
        eyebrow: 'Promedio Olavarría',
        stat: '17', unit: '/mes',
        headline: 'Consultas perdidas al mes en pymes sin sitio web.',
        sub: 'Gente que te googleó, no te encontró, y compró en otro lado.',
        foot: 'Auditorías Ola Digital 2024',
      },
      {
        id: 'C4-3', template: 'list', accent: 'blue', category: 'Carrusel · 3/4', pagenum: '03 / 04',
        eyebrow: 'Para qué sirve',
        headline: 'Lo que un sitio bien hecho hace por tu negocio.',
        items: [
          { title: 'Aparecer en Google cuando te buscan', sub: 'Más allá de Instagram.' },
          { title: 'Vender o agendar 24/7', sub: 'Mientras vos no estás.' },
          { title: 'Mostrar todo en un lugar', sub: 'Servicios, precios, opiniones, ubicación.' },
          { title: 'Construir confianza', sub: 'El 75% juzga tu seriedad por tu sitio.' },
        ],
      },
      {
        id: 'C4-4', template: 'cta', accent: 'orange', category: 'Carrusel · 4/4', pagenum: '04 / 04',
        line1: '¿Tu sitio', line2: 'te trae clientes?',
        sub: 'Auditamos lo que tenés (o lo que te falta) y te decimos qué cambiar primero.',
        ctaTitle: 'Auditoría web — gratis.',
      },
    ],
  },
  // ===== C5: 3 errores en redes =====
  {
    id: 'C5', title: '3 errores que matan tu marca',
    slides: [
      {
        id: 'C5-1', template: 'hook', accent: 'orange', category: 'Carrusel · 1/4', pagenum: '01 / 04',
        eyebrow: 'Redes sociales',
        headlinePre: 'Los',
        headlineHi: '3 errores',
        headlinePost: 'que destruyen tu marca en redes.',
        sub: 'Deslizá →   y fijate cuántos estás cometiendo.',
      },
      {
        id: 'C5-2', template: 'versus', accent: 'orange', category: 'Carrusel · 2/4', pagenum: '02 / 04',
        eyebrow: 'Error #1',
        headline: 'Postear sin saber a quién le hablás.',
        them: 'Posteo lo que “queda lindo” y espero que pase algo.',
        you: 'Cada post le habla a un cliente puntual con una promesa puntual.',
        sub: 'Si tu post le habla a todos, no le habla a nadie.',
      },
      {
        id: 'C5-3', template: 'list', accent: 'orange', category: 'Carrusel · 3/4', pagenum: '03 / 04',
        eyebrow: 'Errores #2 y #3',
        headline: 'Los otros dos que matan tus ventas en silencio.',
        items: [
          { title: 'No responder los DMs en el día', sub: 'El 47% compra al primero que le contesta.' },
          { title: 'Medir likes en vez de consultas', sub: 'Los likes no pagan el alquiler. Las ventas sí.' },
        ],
      },
      {
        id: 'C5-4', template: 'cta', accent: 'orange', category: 'Carrusel · 4/4', pagenum: '04 / 04',
        line1: '¿Querés que', line2: 'tu Insta venda?',
        sub: 'Te hacemos una auditoría sin filtro y te decimos las 3 cosas que cambiarías esta semana.',
        ctaTitle: 'Auditoría de redes — gratis.',
      },
    ],
  },
  // ===== C6: Caso real =====
  {
    id: 'C6', title: 'Caso real: 5 a 47 consultas',
    slides: [
      {
        id: 'C6-1', template: 'bold', accent: 'blue', category: 'Carrusel · 1/4', pagenum: '01 / 04',
        lines: [
          { text: 'De 5 a 47' },
          { text: 'consultas', hi: true },
          { text: 'por mes.' },
        ],
        sub: 'Deslizá →   un caso real de Olavarría, en 90 días.',
      },
      {
        id: 'C6-2', template: 'beforeafter', accent: 'blue', category: 'Carrusel · 2/4', pagenum: '02 / 04',
        eyebrow: 'Antes y después',
        headline: 'Lo que cambió en 90 días.',
        before: { val: '5/mes', sub: 'Consultas por DM. Sin estrategia ni medición.' },
        after: { val: '47/mes', sub: 'Consultas reales con SEO local + ads + email.' },
        tag: '+840% consultas',
      },
      {
        id: 'C6-3', template: 'list', accent: 'blue', category: 'Carrusel · 3/4', pagenum: '03 / 04',
        eyebrow: 'Qué hicimos',
        headline: 'Los 3 movimientos que cambiaron el partido.',
        items: [
          { title: 'Optimizamos Google Business + reseñas', sub: 'Pasaron de página 3 a top 3 en Maps.' },
          { title: 'Google Ads con palabras de intención', sub: '$25.000 ARS de ads → 22 consultas pagas.' },
          { title: 'Email automático a la base existente', sub: 'Reactivamos clientes que no compraban hace 6 meses.' },
        ],
      },
      {
        id: 'C6-4', template: 'cta', accent: 'orange', category: 'Carrusel · 4/4', pagenum: '04 / 04',
        line1: '¿Hacemos lo mismo', line2: 'con tu negocio?',
        sub: 'Te mostramos en 20 minutos qué de esto aplica a tu rubro y a tu zona.',
        ctaTitle: 'Reunión de diagnóstico — gratis.',
      },
    ],
  },
];

Object.assign(window, { SINGLES, CAROUSELS });
