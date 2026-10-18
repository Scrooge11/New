const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const [,, svgdir, outdir, ogdir] = process.argv;
fs.mkdirSync(outdir, { recursive: true });
const jobs = [
  ['jemco-logo-primary.svg','jemco-logo-primary.png',2400],
  ['jemco-logo-primary-reverse.svg','jemco-logo-primary-reverse.png',2400],
  ['jemco-logo-primary-mono.svg','jemco-logo-primary-mono.png',2400],
  ['jemco-logo-primary-white.svg','jemco-logo-primary-white.png',2400],
  ['jemco-logo-horizontal.svg','jemco-logo-horizontal.png',2600],
  ['jemco-logo-horizontal-reverse.svg','jemco-logo-horizontal-reverse.png',2600],
  ['jemco-logo-horizontal-mono.svg','jemco-logo-horizontal-mono.png',2600],
  ['jemco-logo-horizontal-white.svg','jemco-logo-horizontal-white.png',2600],
  ['jemco-mark.svg','jemco-mark.png',2000],
  ['jemco-mark-mono.svg','jemco-mark-mono.png',2000],
  ['jemco-mark-white.svg','jemco-mark-white.png',2000],
  ['jemco-word.svg','jemco-word.png',2000],
  ['jemco-word-white.svg','jemco-word-white.png',2000],
  ['jemco-icon.svg','jemco-icon-1024.png',1024],
  ['jemco-icon.svg','jemco-icon-512.png',512],
  ['alt-jemco-mark-home.svg','alt-jemco-mark-home.png',2000],
  ['alt-jemco-logo-home.svg','alt-jemco-logo-home.png',2400],
];
const favs = [['favicon.svg','favicon-32.png',32],['favicon.svg','favicon-48.png',48],['favicon.svg','favicon-192.png',192],['favicon.svg','favicon-512.png',512],['favicon.svg','apple-touch-icon.png',180]];
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 2600, height: 2600 }, deviceScaleFactor: 1 });
  for (const [src, out, w] of [...jobs, ...favs]) {
    const svg = fs.readFileSync(path.join(svgdir, src), 'utf8');
    const m = svg.match(/viewBox="0 0 (\d+) (\d+)"/); const vw = +m[1], vh = +m[2];
    const h = Math.round(w * vh / vw);
    await page.setContent(`<html><body style="margin:0;background:transparent"><img id="i" src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" style="display:block;width:${w}px;height:${h}px"></body></html>`);
    await page.locator('#i').screenshot({ path: path.join(favs.includes(jobs) ? outdir : outdir, out), omitBackground: true });
    console.log('png', out, w + 'x' + h);
  }
  // Open Graph image 1200x630
  if (ogdir) {
    const svg = fs.readFileSync(path.join(svgdir, 'jemco-logo-horizontal-reverse.svg'), 'utf8');
    await page.setViewportSize({ width: 1200, height: 630 });
    await page.setContent(`<html><body style="margin:0;background:#0B1F3F;width:1200px;height:630px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:28px;font-family:Arial,sans-serif">
      <img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" style="width:1000px;display:block">
      <div style="color:#A9E4FF;font-size:30px;letter-spacing:.08em;text-transform:uppercase;font-weight:700">Licensed &amp; insured &nbsp;·&nbsp; Owner-operated</div></body></html>`);
    await page.screenshot({ path: path.join(ogdir, 'og-image.png') });
    console.log('png og-image.png 1200x630');
  }
  await browser.close();
})();
