// Puppeteer screenshot script — renders every OLA Digital brand asset
// and saves them as PNG files in /brand-toolkit/ola-digital-assets/
//
// Run: node screenshot-all.js
// Requires: npm install puppeteer (already done in /tmp/screenshot-tool)

const puppeteer = require('/tmp/screenshot-tool/node_modules/puppeteer');
const path = require('path');
const fs   = require('fs');

const BASE_URL   = 'http://localhost:8743/render-stage.html';
const OUTPUT_DIR = path.join(__dirname, '..', 'ola-digital-assets');

// ── Complete manifest ─────────────────────────────────────────────────────
const MANIFEST = [
  // Logos
  { folder:'01-logos',           name:'logo-01-neon-dark',             w:600,  h:400,  comp:'LogoNeonDark' },
  { folder:'01-logos',           name:'logo-01-neon-gradiente',        w:600,  h:400,  comp:'LogoNeonOnGrad' },
  { folder:'01-logos',           name:'logo-01-neon-mono',             w:600,  h:400,  comp:'LogoNeonMono' },
  { folder:'01-logos',           name:'logo-02-wordmark-claro',        w:600,  h:400,  comp:'LogoMinimalLight' },
  { folder:'01-logos',           name:'logo-02-wordmark-oscuro',       w:600,  h:400,  comp:'LogoMinimalDark' },
  { folder:'01-logos',           name:'logo-02-wordmark-reversed',     w:600,  h:400,  comp:'LogoMinimalReversed' },
  { folder:'01-logos',           name:'logo-03-gradiente-claro',       w:600,  h:400,  comp:'LogoGradLight' },
  { folder:'01-logos',           name:'logo-03-gradiente-oscuro',      w:600,  h:400,  comp:'LogoGradDark' },
  { folder:'01-logos',           name:'logo-03-gradiente-reversed',    w:600,  h:400,  comp:'LogoGradReversed' },
  { folder:'01-logos',           name:'logo-04-badge-claro',           w:600,  h:400,  comp:'LogoBadgeLight' },
  { folder:'01-logos',           name:'logo-04-badge-oscuro',          w:600,  h:400,  comp:'LogoBadgeDark' },
  { folder:'01-logos',           name:'logo-04-badge-gradiente',       w:600,  h:400,  comp:'LogoBadgeOnGrad' },
  { folder:'01-logos',           name:'logo-05-whatsapp-dp',           w:600,  h:600,  comp:'LogoWhatsAppDP' },
  { folder:'01-logos',           name:'logo-06-email-signature',       w:900,  h:400,  comp:'LogoEmailSig' },
  { folder:'01-logos',           name:'logo-07-favicon',               w:800,  h:500,  comp:'LogoFavicon' },
  { folder:'01-logos',           name:'logo-08-powered-by',            w:600,  h:500,  comp:'LogoPoweredBy' },
  // Feed tanda 1
  { folder:'02-feed-posts',      name:'feed-01-seo-local',             w:1080, h:1350, comp:'Feed1' },
  { folder:'02-feed-posts',      name:'feed-02-redes-sociales',        w:1080, h:1350, comp:'Feed2' },
  { folder:'02-feed-posts',      name:'feed-03-sitios-web',            w:1080, h:1350, comp:'Feed3' },
  // Feed tanda 2
  { folder:'02-feed-posts',      name:'feed-04-sin-web',               w:1080, h:1350, comp:'Feed4' },
  { folder:'02-feed-posts',      name:'feed-05-google-ads',            w:1080, h:1350, comp:'Feed5' },
  { folder:'02-feed-posts',      name:'feed-06-instagram-competencia', w:1080, h:1350, comp:'Feed6' },
  { folder:'02-feed-posts',      name:'feed-07-email-marketing',       w:1080, h:1350, comp:'Feed7' },
  { folder:'02-feed-posts',      name:'feed-08-reputacion-online',     w:1080, h:1350, comp:'Feed8' },
  // Carousel A
  { folder:'03-carruseles',      name:'carA-1-cover',                  w:1080, h:1080, comp:'Carousel1' },
  { folder:'03-carruseles',      name:'carA-2-error-01',               w:1080, h:1080, comp:'Carousel2' },
  { folder:'03-carruseles',      name:'carA-3-error-02',               w:1080, h:1080, comp:'Carousel3' },
  { folder:'03-carruseles',      name:'carA-4-error-03',               w:1080, h:1080, comp:'Carousel4' },
  { folder:'03-carruseles',      name:'carA-5-cta',                    w:1080, h:1080, comp:'Carousel5' },
  // Carousel B
  { folder:'03-carruseles',      name:'carB-1-cover',                  w:1080, h:1080, comp:'CarBCover' },
  { folder:'03-carruseles',      name:'carB-2-paso-01',                w:1080, h:1080, comp:'CarB2' },
  { folder:'03-carruseles',      name:'carB-3-paso-02',                w:1080, h:1080, comp:'CarB3' },
  { folder:'03-carruseles',      name:'carB-4-paso-03',                w:1080, h:1080, comp:'CarB4' },
  { folder:'03-carruseles',      name:'carB-5-cta',                    w:1080, h:1080, comp:'CarB5' },
  // Carousel C
  { folder:'03-carruseles',      name:'carC-1-cover',                  w:1080, h:1080, comp:'CarCCover' },
  { folder:'03-carruseles',      name:'carC-2-panaderia',              w:1080, h:1080, comp:'CarC2' },
  { folder:'03-carruseles',      name:'carC-3-estudio-contable',       w:1080, h:1080, comp:'CarC3' },
  { folder:'03-carruseles',      name:'carC-4-casa-hogar',             w:1080, h:1080, comp:'CarC4' },
  { folder:'03-carruseles',      name:'carC-5-cta',                    w:1080, h:1080, comp:'CarC5' },
  // Carousel D
  { folder:'03-carruseles',      name:'carD-1-cover',                  w:1080, h:1080, comp:'CarDCover' },
  { folder:'03-carruseles',      name:'carD-2-costo-01',               w:1080, h:1080, comp:'CarD2' },
  { folder:'03-carruseles',      name:'carD-3-costo-02',               w:1080, h:1080, comp:'CarD3' },
  { folder:'03-carruseles',      name:'carD-4-costo-03',               w:1080, h:1080, comp:'CarD4' },
  { folder:'03-carruseles',      name:'carD-5-cta',                    w:1080, h:1080, comp:'CarD5' },
  // Reels
  { folder:'04-reels',           name:'reel-01-hook',                  w:1080, h:1920, comp:'Reel1' },
  { folder:'04-reels',           name:'reel-02-stat-cards',            w:1080, h:1920, comp:'Reel2' },
  { folder:'04-reels',           name:'reel-03-wave-build',            w:1080, h:1920, comp:'Reel3' },
  { folder:'04-reels',           name:'reel-04-logo-cta',              w:1080, h:1920, comp:'Reel4' },
  // Stories
  { folder:'05-stories',         name:'story-01-countdown',            w:1080, h:1920, comp:'Story1' },
  { folder:'05-stories',         name:'story-02-encuesta',             w:1080, h:1920, comp:'Story2' },
  { folder:'05-stories',         name:'story-03-testimonio',           w:1080, h:1920, comp:'Story3' },
  { folder:'05-stories',         name:'story-04-tip-del-dia',          w:1080, h:1920, comp:'Story4' },
  { folder:'05-stories',         name:'story-05-behind-scenes',        w:1080, h:1920, comp:'Story5' },
  // Email headers
  { folder:'06-email-headers',   name:'email-01-newsletter',           w:1080, h:540,  comp:'Email1' },
  { folder:'06-email-headers',   name:'email-02-oferta',               w:1080, h:540,  comp:'Email2' },
  { folder:'06-email-headers',   name:'email-03-reporte',              w:1080, h:540,  comp:'Email3' },
  // Motion spec
  { folder:'07-motion-spec',     name:'motion-spec',                   w:1080, h:1400, comp:'MotionSpec' },
  // Junio singles
  { folder:'08-junio-singles',   name:'jun-A-de-2-a-15-reservas',      w:1080, h:1080, comp:'PostA' },
  { folder:'08-junio-singles',   name:'jun-B-google-my-business',      w:1080, h:1080, comp:'PostB' },
  { folder:'08-junio-singles',   name:'jun-C-dato-89',                 w:1080, h:1080, comp:'PostC' },
  { folder:'08-junio-singles',   name:'jun-D-reels-publico',           w:1080, h:1080, comp:'PostD' },
  { folder:'08-junio-singles',   name:'jun-E-perfil-vidriera',         w:1080, h:1080, comp:'PostE' },
  { folder:'08-junio-singles',   name:'jun-F-dato-87',                 w:1080, h:1080, comp:'PostF' },
  { folder:'08-junio-singles',   name:'jun-G-cero-a-agenda',           w:1080, h:1080, comp:'PostG' },
  { folder:'08-junio-singles',   name:'jun-H-consistencia',            w:1080, h:1080, comp:'PostH' },
  { folder:'08-junio-singles',   name:'jun-I-cierre-dramatico',        w:1080, h:1080, comp:'PostI' },
  // Junio carruseles
  { folder:'09-junio-carruseles',name:'jun-C1-1-cover',                w:1080, h:1080, comp:'C1S1' },
  { folder:'09-junio-carruseles',name:'jun-C1-2-paso-01',              w:1080, h:1080, comp:'C1S2' },
  { folder:'09-junio-carruseles',name:'jun-C1-3-paso-02',              w:1080, h:1080, comp:'C1S3' },
  { folder:'09-junio-carruseles',name:'jun-C1-4-cta',                  w:1080, h:1080, comp:'C1S4' },
  { folder:'09-junio-carruseles',name:'jun-C2-1-cover',                w:1080, h:1080, comp:'C2S1' },
  { folder:'09-junio-carruseles',name:'jun-C2-2-diferencia',           w:1080, h:1080, comp:'C2S2' },
  { folder:'09-junio-carruseles',name:'jun-C2-3-rubros',               w:1080, h:1080, comp:'C2S3' },
  { folder:'09-junio-carruseles',name:'jun-C2-4-cta',                  w:1080, h:1080, comp:'C2S4' },
  { folder:'09-junio-carruseles',name:'jun-C3-1-cover',                w:1080, h:1080, comp:'C3S1' },
  { folder:'09-junio-carruseles',name:'jun-C3-2-error-01',             w:1080, h:1080, comp:'C3S2' },
  { folder:'09-junio-carruseles',name:'jun-C3-3-error-02',             w:1080, h:1080, comp:'C3S3' },
  { folder:'09-junio-carruseles',name:'jun-C3-4-cta',                  w:1080, h:1080, comp:'C3S4' },
  { folder:'09-junio-carruseles',name:'jun-C4-1-cover',                w:1080, h:1080, comp:'C4S1' },
  { folder:'09-junio-carruseles',name:'jun-C4-2-sintoma-causa',        w:1080, h:1080, comp:'C4S2' },
  { folder:'09-junio-carruseles',name:'jun-C4-3-insight',              w:1080, h:1080, comp:'C4S3' },
  { folder:'09-junio-carruseles',name:'jun-C4-4-cta',                  w:1080, h:1080, comp:'C4S4' },
  { folder:'09-junio-carruseles',name:'jun-C5-1-cover',                w:1080, h:1080, comp:'C5S1' },
  { folder:'09-junio-carruseles',name:'jun-C5-2-paso-01',              w:1080, h:1080, comp:'C5S2' },
  { folder:'09-junio-carruseles',name:'jun-C5-3-paso-02',              w:1080, h:1080, comp:'C5S3' },
  { folder:'09-junio-carruseles',name:'jun-C5-4-cta',                  w:1080, h:1080, comp:'C5S4' },
  { folder:'09-junio-carruseles',name:'jun-C6-1-cover',                w:1080, h:1080, comp:'C6S1' },
  { folder:'09-junio-carruseles',name:'jun-C6-2-journey',              w:1080, h:1080, comp:'C6S2' },
  { folder:'09-junio-carruseles',name:'jun-C6-3-resultados',           w:1080, h:1080, comp:'C6S3' },
  { folder:'09-junio-carruseles',name:'jun-C6-4-cta',                  w:1080, h:1080, comp:'C6S4' },
  // Julio singles
  { folder:'10-julio-singles',   name:'jul-J-sin-google-maps',         w:1080, h:1080, comp:'PostJ' },
  { folder:'10-julio-singles',   name:'jul-K-73pct-reviews',           w:1080, h:1080, comp:'PostK' },
  { folder:'10-julio-singles',   name:'jul-L-respuesta-30s',           w:1080, h:1080, comp:'PostL' },
  { folder:'10-julio-singles',   name:'jul-M-instagram-nunca-cierra',  w:1080, h:1080, comp:'PostM' },
  { folder:'10-julio-singles',   name:'jul-N-caso-estudio-contable',   w:1080, h:1080, comp:'PostN' },
  { folder:'10-julio-singles',   name:'jul-O-3-cosas-bio',             w:1080, h:1080, comp:'PostO' },
  { folder:'10-julio-singles',   name:'jul-P-si-no-en-google',         w:1080, h:1080, comp:'PostP' },
  { folder:'10-julio-singles',   name:'jul-Q-5-segundos',              w:1080, h:1080, comp:'PostQ' },
  { folder:'10-julio-singles',   name:'jul-R-web-lenta-vs-rapida',     w:1080, h:1080, comp:'PostR' },
  { folder:'10-julio-singles',   name:'jul-S-que-se-vea',              w:1080, h:1080, comp:'PostS' },
];

async function run() {
  // create output folders
  const folders = [...new Set(MANIFEST.map(m => m.folder))];
  folders.forEach(f => fs.mkdirSync(path.join(OUTPUT_DIR, f), { recursive: true }));

  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
  });

  const page = await browser.newPage();

  // load the render stage page (waits for all scripts to compile)
  await page.goto(BASE_URL, { waitUntil: 'networkidle0', timeout: 60000 });
  // wait for fonts
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 500));

  let done = 0;
  for (const item of MANIFEST) {
    const { folder, name, w, h, comp } = item;

    // resize viewport and render the component
    await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
    await page.evaluate(({ comp, w, h }) => window.renderComp(comp, w, h), { comp, w, h });
    // wait for render + fonts + any CSS animations to settle
    await new Promise(r => setTimeout(r, 700));

    const outPath = path.join(OUTPUT_DIR, folder, `${name}.png`);
    await page.screenshot({ path: outPath, clip: { x: 0, y: 0, width: w, height: h } });

    done++;
    process.stdout.write(`\r[${done}/${MANIFEST.length}] ${name}.png`);
  }

  await browser.close();
  console.log(`\n\nDone! ${MANIFEST.length} files saved to:\n${OUTPUT_DIR}`);
  // open the output folder in Finder
  require('child_process').exec(`open "${OUTPUT_DIR}"`);
}

run().catch(err => { console.error(err); process.exit(1); });
