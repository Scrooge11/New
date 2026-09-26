import sys, os
REPO = sys.argv[1]

PALETTE = [
  ("Navy", "#0B1F3F", "Primary dark. Headers, footers, wordmark on light backgrounds."),
  ("Deep Blue", "#0E3A7A", "Bottom of the letter gradient. Hover states on dark."),
  ("JS Blue", "#1655B8", "The brand blue. Buttons, links, the second line of the wordmark."),
  ("Bright Blue", "#2F82F5", "Top of the letter gradient. Eyebrow labels, hover states on light."),
  ("Electric", "#3DB4FF", "The bolt. Accents and labels on navy. Never for body text on white."),
  ("Electric Light", "#A9E4FF", "Highlight in the bolt. Large text on navy only."),
  ("Hi-Vis Amber", "#FFB020", "Call-to-action only: phone buttons, the emergency stripe. Use once per screen."),
  ("Ink", "#16202E", "Body text."),
  ("Steel", "#8B96A5", "Secondary text, plug blades."),
  ("Line", "#D9E0EA", "Borders and dividers."),
  ("Off-white", "#F4F7FB", "Page background. A cool white, biased toward the blue."),
]

def hex_to_rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0): return (0, 0, 0, 100)
    c, m, y = 1 - r/255, 1 - g/255, 1 - b/255
    k = min(c, m, y)
    return tuple(round(100 * v) for v in ((c-k)/(1-k), (m-k)/(1-k), (y-k)/(1-k), k))

def swatches():
    out = []
    for name, hx, use in PALETTE:
        r, g, b = hex_to_rgb(hx); c, m, y, k = rgb_to_cmyk(r, g, b)
        dark = (r*299 + g*587 + b*114) / 1000 < 140
        out.append(f'''<div class="swatch">
  <div class="chip" style="background:{hx};color:{'#fff' if dark else '#0B1F3F'}"><span>{hx}</span></div>
  <div class="swatch-meta"><strong>{name}</strong><span>RGB {r}, {g}, {b}</span><span>CMYK {c}, {m}, {y}, {k}</span><p>{use}</p></div>
</div>''')
    return '\n'.join(out)

FILES = [
  ("js-logo-primary", "Primary stacked lockup, full color", "Default. Business cards, invoices, truck doors, signage, social profiles with room."),
  ("js-logo-primary-reverse", "Primary on navy", "Dark backgrounds: shirts, dark website sections, vehicle wraps on dark paint."),
  ("js-logo-primary-mono", "Primary, one-color navy", "Single-color print, embroidery, stamps, fax cover sheets."),
  ("js-logo-primary-white", "Primary, one-color white", "Embroidery or screen print on dark garments; etched or engraved surfaces."),
  ("js-logo-horizontal", "Horizontal lockup, full color", "Website header, email signatures, letterhead, banners: anywhere wide and short."),
  ("js-logo-horizontal-reverse", "Horizontal on navy", "Dark headers and footers."),
  ("js-logo-horizontal-mono", "Horizontal, one-color navy", "One-color print."),
  ("js-logo-horizontal-white", "Horizontal, one-color white", "Footer of the website, dark garments."),
  ("js-mark", "Mark only (JS, bolt, cord, plug)", "Hero graphics, hard hats, shirt sleeves, when the name is printed nearby."),
  ("js-mark-reverse", "Mark only, for dark backgrounds", "Same as above on navy."),
  ("js-mark-mono", "Mark only, one-color navy", "Embroidery, stamps."),
  ("js-mark-white", "Mark only, one-color white", "Dark garments, engraving."),
  ("js-icon", "Square app icon", "Social profile avatars, Google Business Profile, app icons."),
  ("favicon", "Favicon", "Browser tab icon (also exported as PNG at 32, 48, 192 and 512 px)."),
  ("alt-js-mark-home", "Alternate mark with roofline", "Optional. Home-services advertising where the house needs to be explicit (mailers, yard signs)."),
  ("alt-js-logo-home", "Alternate stacked lockup with roofline", "Optional. Same uses as above, with the name."),
]

def file_rows():
    return '\n'.join(f'<tr><td><code>{n}.svg</code></td><td>{d}</td><td>{u}</td></tr>' for n, d, u in FILES)

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JS Brand Guidelines</title>
<meta name="description" content="Logo, color, typography and usage rules for JS Contracting & Electrical Services.">
<link rel="icon" href="logo/svg/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira:wght@600;700;800&family=Barlow:wght@400;500;600;700&display=swap">
<style>
:root{{--navy:#0B1F3F;--blue:#1655B8;--bright:#2F82F5;--electric:#3DB4FF;--amber:#FFB020;--ink:#16202E;--muted:#5B6675;--line:#D9E0EA;--bg:#F4F7FB;--display:"Saira","Barlow","Arial Narrow",Arial,sans-serif;--body:"Barlow","Helvetica Neue",Arial,sans-serif}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:1.0625rem;line-height:1.6}}
img{{max-width:100%;height:auto;display:block}}
h1,h2,h3{{font-family:var(--display);color:var(--navy);line-height:1.1;margin:0 0 .5em;text-wrap:balance}}
h1{{font-size:clamp(2rem,4vw,3rem);font-weight:800}} h2{{font-size:clamp(1.5rem,2.6vw,2.1rem);font-weight:800}} h3{{font-size:1.15rem;font-weight:700}}
p{{margin:0 0 1em}} code{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em;background:#E6F0FF;padding:.1em .35em;border-radius:4px}}
.wrap{{max-width:1080px;margin-inline:auto;padding-inline:clamp(16px,4vw,40px)}}
.top{{background:var(--navy);color:#fff;padding-block:clamp(2.5rem,6vw,5rem)}}
.top h1{{color:#fff}} .top p{{color:#C9D6EA;max-width:38em;font-size:1.15rem}}
.top img{{width:min(100%,460px);margin-bottom:2rem}}
.eyebrow{{font-family:var(--display);text-transform:uppercase;letter-spacing:.14em;font-size:.8rem;font-weight:700;color:var(--bright);margin:0 0 .5rem}}
.top .eyebrow{{color:var(--electric)}}
section{{padding-block:clamp(2.5rem,5vw,4rem);border-bottom:1px solid var(--line)}}
.intro{{max-width:46em;color:var(--muted);font-size:1.1rem}}
.grid{{display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fit,minmax(225px,1fr))}}
.tile{{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}}
.tile .art{{padding:1.5rem;display:flex;align-items:center;justify-content:center;min-height:220px;background:#fff}}
.tile .art.dark{{background:var(--navy)}} .tile .art.grid-bg{{background:repeating-linear-gradient(0deg,#EEF2F7 0 1px,transparent 1px 24px),repeating-linear-gradient(90deg,#EEF2F7 0 1px,transparent 1px 24px),#fff}}
.tile .art img{{max-height:200px;width:auto}}
.tile .cap{{padding:1rem 1.25rem;border-top:1px solid var(--line)}} .tile .cap strong{{display:block;color:var(--navy);font-family:var(--display)}} .tile .cap span{{color:var(--muted);font-size:.95rem}}
.swatches{{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}}
.swatch{{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}}
.chip{{height:96px;display:flex;align-items:flex-end;padding:.75rem;font-family:var(--display);font-weight:700;letter-spacing:.04em}}
.swatch-meta{{padding:.9rem 1rem;display:grid;gap:.15rem;font-size:.92rem}} .swatch-meta strong{{color:var(--navy);font-size:1rem}} .swatch-meta span{{color:var(--muted);font-variant-numeric:tabular-nums}} .swatch-meta p{{margin:.5rem 0 0;color:var(--ink)}}
.type-sample{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:1.5rem;display:grid;gap:1rem}}
.type-sample .display{{font-family:var(--display);font-weight:800;font-size:2.6rem;line-height:1.05;color:var(--navy)}}
.type-sample .label{{font-family:var(--display);font-weight:700;text-transform:uppercase;letter-spacing:.14em;font-size:.85rem;color:var(--bright)}}
.type-sample .body{{max-width:60ch}} .type-sample .meta{{color:var(--muted);font-size:.9rem;border-top:1px solid var(--line);padding-top:.75rem}}
.two{{display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
.rules{{display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
.rules ul{{margin:0;padding-left:1.2rem;display:grid;gap:.5rem}} .rules h3{{margin-bottom:.5rem}}
.do h3{{color:#16613A}} .dont h3{{color:#8A1C1C}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:.95rem}}
th{{text-align:left;background:var(--navy);color:#fff;font-family:var(--display);text-transform:uppercase;letter-spacing:.08em;font-size:.75rem;padding:.75rem .9rem}}
td{{padding:.7rem .9rem;border-top:1px solid var(--line);vertical-align:top}}
.table-wrap{{overflow-x:auto}}
/* application mockups */
.mock{{display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
.card{{aspect-ratio:3.5/2;border-radius:10px;box-shadow:0 12px 30px rgba(11,31,63,.14);padding:6%;display:flex;flex-direction:column;justify-content:space-between;background:#fff;border:1px solid var(--line)}}
.card img{{width:62%}} .card .who{{font-family:var(--display);color:var(--navy)}} .card .who strong{{display:block;font-size:1.05rem}} .card .who span{{display:block;color:var(--muted);font-size:.85rem;font-family:var(--body)}}
.card.back{{background:var(--navy);align-items:center;justify-content:center}} .card.back img{{width:55%}}
.door{{aspect-ratio:4/3;border-radius:14px;background:linear-gradient(180deg,#F6F8FB,#E3E8EF);border:1px solid #C9D1DC;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1rem;padding:8%}}
.door img{{width:70%}} .door .phone{{font-family:var(--display);font-weight:800;font-size:clamp(1.4rem,3vw,2rem);color:var(--navy);letter-spacing:.02em}} .door .lic{{font-family:var(--display);font-weight:600;font-size:.85rem;letter-spacing:.12em;color:var(--blue);text-transform:uppercase}}
.shirt{{aspect-ratio:4/3;border-radius:14px;background:#0B1F3F;display:flex;align-items:flex-start;justify-content:flex-end;padding:10% 12%}} .shirt img{{width:30%}}
.mock-cap{{font-size:.9rem;color:var(--muted);margin:.5rem 0 0}}
.clear{{position:relative;background:#fff;border:1px solid var(--line);border-radius:10px;padding:2rem;display:flex;justify-content:center}}
.clear .box{{position:relative;padding:12.5%;outline:2px dashed var(--bright);outline-offset:-1px}}
.clear .box img{{width:min(100%,360px)}}
.clear .tag{{position:absolute;top:.35rem;left:.5rem;font-family:var(--display);font-size:.75rem;font-weight:700;letter-spacing:.1em;color:var(--bright);text-transform:uppercase}}
.minsize{{display:flex;align-items:flex-end;gap:2rem;flex-wrap:wrap;background:#fff;border:1px solid var(--line);border-radius:10px;padding:1.5rem}}
.minsize figure{{margin:0;text-align:center}} .minsize figcaption{{font-size:.8rem;color:var(--muted);margin-top:.5rem}}
footer{{padding-block:2rem;color:var(--muted);font-size:.9rem}}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <img src="logo/svg/js-logo-horizontal-reverse.svg" alt="JS Contracting &amp; Electrical Services" width="1280" height="380">
    <p class="eyebrow">Brand guidelines, version 1.0, September 2026</p>
    <h1>How the JS brand goes together.</h1>
    <p>One mark, two blues, one accent, two typefaces. Everything here is built to look right on a truck door, a shirt, an invoice, and a phone screen without redrawing anything.</p>
  </div>
</header>

<section>
  <div class="wrap">
    <p class="eyebrow">The idea</p>
    <h2>Electric, but built.</h2>
    <p class="intro">The mark is the JS monogram with a lightning bolt through the gap and a cord that runs out of the J to a two-prong plug. The letters are heavy and slanted for momentum; the bolt says electrical, the cord and plug say the job gets finished and plugged in. The wordmark underneath is set in Saira, a squared industrial sans, with "Contracting" carrying the weight and "&amp; Electrical Services" spaced out beneath it.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Logo system</p>
    <h2>Four ways to use the logo</h2>
    <div class="grid">
      <div class="tile"><div class="art"><img src="logo/svg/js-logo-primary.svg" alt="Primary stacked logo"></div><div class="cap"><strong>Primary</strong><span>The default. Use whenever there is room for a square-ish logo.</span></div></div>
      <div class="tile"><div class="art"><img src="logo/svg/js-logo-horizontal.svg" alt="Horizontal logo"></div><div class="cap"><strong>Horizontal</strong><span>Website header, letterhead, email signature, banners.</span></div></div>
      <div class="tile"><div class="art"><img src="logo/svg/js-mark.svg" alt="Mark only"></div><div class="cap"><strong>Mark</strong><span>When the full name is already nearby: hard hats, sleeves, hero graphics.</span></div></div>
      <div class="tile"><div class="art"><img src="logo/svg/js-icon.svg" alt="Square icon" style="max-height:160px"></div><div class="cap"><strong>Icon</strong><span>Social avatars, Google Business Profile, app icons, favicon.</span></div></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Color versions</p>
    <h2>Full color first, one color when you must</h2>
    <p class="intro">Use the full-color version on white or very light backgrounds and the reverse version on navy. The one-color versions exist for embroidery, single-color print, engraving, and anywhere gradients will not reproduce.</p>
    <div class="grid">
      <div class="tile"><div class="art"><img src="logo/svg/js-logo-primary.svg" alt="Full color on white"></div><div class="cap"><strong>Full color on white</strong><span>Default.</span></div></div>
      <div class="tile"><div class="art dark"><img src="logo/svg/js-logo-primary-reverse.svg" alt="Full color on navy"></div><div class="cap"><strong>Reverse on navy</strong><span>Dark backgrounds and garments.</span></div></div>
      <div class="tile"><div class="art"><img src="logo/svg/js-logo-primary-mono.svg" alt="One color navy"></div><div class="cap"><strong>One-color navy</strong><span>Single-color print, stamps, embroidery on light fabric.</span></div></div>
      <div class="tile"><div class="art dark"><img src="logo/svg/js-logo-primary-white.svg" alt="One color white"></div><div class="cap"><strong>One-color white</strong><span>Embroidery and screen print on dark fabric, engraving.</span></div></div>
    </div>
    <h3 style="margin-top:2rem">Alternate: the roofline mark</h3>
    <p class="intro">An optional version with a roof over the letters for home-services advertising (mailers, yard signs, home-show banners) where the house needs to be explicit. Keep the primary mark as the default everywhere else so the brand stays consistent.</p>
    <div class="two">
      <div class="tile"><div class="art"><img src="logo/svg/alt-js-mark-home.svg" alt="Alternate mark with roofline"></div><div class="cap"><strong>Roofline mark</strong><span>alt-js-mark-home.svg</span></div></div>
      <div class="tile"><div class="art"><img src="logo/svg/alt-js-logo-home.svg" alt="Alternate stacked logo with roofline"></div><div class="cap"><strong>Roofline stacked lockup</strong><span>alt-js-logo-home.svg</span></div></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Clear space and minimum size</p>
    <h2>Give it room</h2>
    <div class="two">
      <div>
        <div class="clear"><div class="box"><span class="tag">Clear space = height of the S</span><img src="logo/svg/js-logo-primary.svg" alt="Primary logo with clear space"></div></div>
        <p class="mock-cap">Keep a margin equal to the cap height of the S on all sides. Nothing else (text, photos, other logos, the edge of a card) goes inside it.</p>
      </div>
      <div>
        <div class="minsize">
          <figure><img src="logo/svg/js-logo-primary.svg" width="120" alt=""><figcaption>Primary: 120 px / 1.25 in wide</figcaption></figure>
          <figure><img src="logo/svg/js-logo-horizontal.svg" width="180" alt=""><figcaption>Horizontal: 180 px / 2 in wide</figcaption></figure>
          <figure><img src="logo/svg/js-mark.svg" width="56" alt=""><figcaption>Mark: 56 px / 0.6 in</figcaption></figure>
          <figure><img src="logo/svg/js-icon.svg" width="32" alt=""><figcaption>Icon: 32 px</figcaption></figure>
        </div>
        <p class="mock-cap">Below these sizes the wordmark stops being readable. Use the mark or the icon instead.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Color</p>
    <h2>Two blues, an electric accent, and hi-vis amber</h2>
    <p class="intro">The blues carry the brand. Electric is for the bolt and for highlights on navy. Amber is the tradesman's hi-vis: it is reserved for the one action you want someone to take, like the phone number, and for the warning stripe. If amber is on every button it means nothing.</p>
    <div class="swatches">
{swatches()}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Typography</p>
    <h2>Saira for headlines, Barlow for everything else</h2>
    <div class="two">
      <div class="type-sample">
        <div class="label">Saira, ExtraBold 800 and Bold 700</div>
        <div class="display">Panel upgrades, EV chargers, generators.</div>
        <div class="label">Labels in uppercase, tracked +0.14em</div>
        <div class="meta">The display face. Headlines, buttons, labels, prices on quotes. Free (SIL Open Font License) on Google Fonts, so it can be installed on any computer for print work.</div>
      </div>
      <div class="type-sample">
        <div class="label">Barlow, Regular 400, Medium 500, SemiBold 600</div>
        <div class="body">Barlow is the workhorse: body copy, forms, invoices, emails, and anything that has to be read at length. It has the same slightly squared shapes as Saira, so the two sit together without fighting. Keep body text between 16 and 18 px on screen and 10 to 11 pt in print.</div>
        <div class="meta">Also free on Google Fonts. If neither font is available (a text-only email, a sign shop with a limited library), use Arial or Helvetica Bold for headlines and Arial for body.</div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Voice</p>
    <h2>Say it like the person doing the work</h2>
    <div class="rules">
      <div><h3>Sounds like JS</h3><ul><li>"Written quote before we start."</li><li>"Breaker keeps tripping? Call today, not next week."</li><li>"We pull the permit and meet the inspector."</li><li>"One crew for the wiring and the walls."</li></ul></div>
      <div><h3>Does not sound like JS</h3><ul><li>"Your premier full-service solution provider."</li><li>"We go above and beyond to exceed expectations."</li><li>"Synergy", "best-in-class", "world-class".</li><li>Exclamation points. The work speaks for itself.</li></ul></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Applications</p>
    <h2>How it looks in the real world</h2>
    <div class="mock">
      <div>
        <div class="card"><img src="logo/svg/js-logo-horizontal.svg" alt=""><div class="who"><strong>[Owner name]</strong><span>Owner, Master Electrician</span><span>(000) 000-0000 &middot; office@yourdomain.com</span></div></div>
        <p class="mock-cap">Business card, front. 3.5 x 2 in, white stock, horizontal logo top-left.</p>
      </div>
      <div>
        <div class="card back"><img src="logo/svg/js-logo-primary-reverse.svg" alt=""></div>
        <p class="mock-cap">Business card, back. Solid navy with the reverse primary logo centered.</p>
      </div>
      <div>
        <div class="door"><img src="logo/svg/js-logo-primary.svg" alt=""><div class="phone">(000) 000-0000</div><div class="lic">Licensed &amp; insured &middot; Lic. #00000000</div></div>
        <p class="mock-cap">Truck door on white or silver paint. Primary logo, phone number in Saira 800, license line under it.</p>
      </div>
      <div>
        <div class="shirt"><img src="logo/svg/js-mark-white.svg" alt=""></div>
        <p class="mock-cap">Navy work shirt, left chest: one-color white mark, 3.5 in wide. Full name and phone across the back in white.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Rules</p>
    <h2>Do and do not</h2>
    <div class="rules">
      <div class="do"><h3>Do</h3><ul>
        <li>Use the SVG files whenever the software allows; they scale to any size without blurring.</li>
        <li>Put the full-color logo on white or off-white, and the reverse logo on navy.</li>
        <li>Keep the clear space, especially on business cards and yard signs.</li>
        <li>Send the vector files (SVG or PDF) to sign shops and embroiderers, not screenshots.</li>
        <li>Use the one-color versions for single-color printing and embroidery.</li>
      </ul></div>
      <div class="dont"><h3>Do not</h3><ul>
        <li>Stretch, squash, rotate, or add drop shadows, glows, or outlines.</li>
        <li>Recolor the mark (no red bolt, no black letters) or set it on a busy photo.</li>
        <li>Retype the wordmark in another font or rearrange the lines.</li>
        <li>Put the full-color logo on mid-tone or bright backgrounds; use navy or white behind it.</li>
        <li>Separate the bolt from the letters or use the plug on its own as a logo.</li>
      </ul></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">Files</p>
    <h2>What is in the package</h2>
    <p class="intro">Every logo is in <code>brand/logo/svg/</code> as vector art (text converted to outlines, so no fonts are needed to open them) and in <code>brand/logo/png/</code> as high-resolution PNG with transparent backgrounds. The source that draws them is in <code>brand/source/</code>.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>File</th><th>What it is</th><th>Use it for</th></tr></thead>
      <tbody>
{file_rows()}
      </tbody>
    </table></div>
  </div>
</section>

<footer><div class="wrap">JS Contracting &amp; Electrical Services brand guidelines. Saira and Barlow are used under the SIL Open Font License.</div></footer>
</body>
</html>
'''
open(os.path.join(REPO, 'brand', 'index.html'), 'w').write(HTML)
print('wrote brand/index.html', len(HTML))
