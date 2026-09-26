const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const [,, svgdir, outdir, ogdir] = process.argv;
fs.mkdirSync(outdir, { recursive: true });
const jobs = [
  ['js-logo-primary.svg','js-logo-primary.png',2000],
  ['js-logo-primary-reverse.svg','js-logo-primary-reverse.png',2000],
  ['js-logo-primary-mono.svg','js-logo-primary-mono.png',2000],
  ['js-logo-primary-white.svg','js-logo-primary-white.png',2000],
  ['js-logo-horizontal.svg','js-logo-horizontal.png',2400],
  ['js-logo-horizontal-reverse.svg','js-logo-horizontal-reverse.png',2400],
  ['js-logo-horizontal-mono.svg','js-logo-horizontal-mono.png',2400],
  ['js-logo-horizontal-white.svg','js-logo-horizontal-white.png',2400],
  ['js-mark.svg','js-mark.png',1600],
  ['js-mark-mono.svg','js-mark-mono.png',1600],
  ['js-mark-white.svg','js-mark-white.png',1600],
  ['js-icon.svg','js-icon-1024.png',1024],
  ['js-icon.svg','js-icon-512.png',512],
  ['alt-js-mark-home.svg','alt-js-mark-home.png',1600],
  ['alt-js-logo-home.svg','alt-js-logo-home.png',2000],
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
    const svg = fs.readFileSync(path.join(svgdir, 'js-logo-horizontal-reverse.svg'), 'utf8');
    await page.setViewportSize({ width: 1200, height: 630 });
    await page.setContent(`<html><body style="margin:0;background:#0B1F3F;width:1200px;height:630px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:28px;font-family:Arial,sans-serif">
      <img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" style="width:900px;display:block">
      <div style="color:#A9E4FF;font-size:30px;letter-spacing:.08em;text-transform:uppercase;font-weight:700">Licensed &amp; insured &nbsp;·&nbsp; Owner-operated</div></body></html>`);
    await page.screenshot({ path: path.join(ogdir, 'og-image.png') });
    console.log('png og-image.png 1200x630');
  }
  await browser.close();
})();
