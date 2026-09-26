"""Generate JS Contracting & Electrical Services logo SVGs.
Run: python3 logo.py <outdir>
Letterforms: Saira Black Italic (SIL OFL) converted to outlines; bolt/cord/plug drawn geometrically.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from text2path import TextPath

FONTS = os.path.join(os.path.dirname(__file__), '..', 'fonts')
SAIRA = os.path.join(FONTS, 'Saira[wdth,wght].ttf')
SAIRA_I = os.path.join(FONTS, 'Saira-Italic[wdth,wght].ttf')

# ---- Brand palette ----
NAVY    = '#0B1F3F'
BLUE_D  = '#0E3A7A'
BLUE    = '#1655B8'
BLUE_L  = '#2F82F5'
ELEC    = '#3DB4FF'
ELEC_L  = '#A9E4FF'
STEEL_D = '#8B96A5'
WHITE   = '#FFFFFF'

def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')

_tp = {}
def tp(font, wght, wdth=100):
    k = (font, wght, wdth)
    if k not in _tp:
        _tp[k] = TextPath(font, {'wght': wght, 'wdth': wdth})
    return _tp[k]

# --------------------------------------------------------------------------
# Mark geometry. Box: 0..800 x 0..520. Baseline of letters y=415, cap 330.
# --------------------------------------------------------------------------
CAP = 330
BASE = 415
XJ = 150
GAP = 34
BOLT_PTS = [(356, 40), (256, 238), (324, 238), (262, 452), (398, 212), (334, 212)]
BOLT_TX = "skewX(-9) translate(116 0)"
CORD = "M 200 400 C 150 500, 340 548, 566 494 C 640 476, 660 462, 682 448"
PLUG_AT = (682, 448)
PLUG_ANG = math.degrees(math.atan2(448 - 462, 682 - 660))

def poly(pts):
    return 'M ' + ' L '.join('%s %s' % (fmt(x), fmt(y)) for x, y in pts) + ' Z'

def letters(fill):
    t = tp(SAIRA_I, 900)
    size = CAP / (t.cap_height / 1000.0)
    dj, wj = t.path('J', size)
    ds, ws = t.path('S', size)
    xs = XJ + wj + GAP
    return (f'<path transform="translate({fmt(XJ)} {BASE})" d="{dj}" fill="{fill}"/>\n'
            f'    <path transform="translate({fmt(xs)} {BASE})" d="{ds}" fill="{fill}"/>')

def bolt(knock, fill):
    d = poly(BOLT_PTS)
    return (f'<g transform="{BOLT_TX}">\n'
            f'      <path d="{d}" fill="{knock}" stroke="{knock}" stroke-width="24" stroke-linejoin="miter" stroke-miterlimit="8"/>\n'
            f'      <path d="{d}" fill="{fill}"/>\n    </g>')

def plug(x, y, angle, mono=None):
    body = mono or 'url(#gPlug)'
    blade = mono or 'url(#gBlade)'
    ridge = mono or NAVY
    op = '1' if mono else '0.8'
    return f'''<g transform="translate({fmt(x)} {fmt(y)}) rotate({fmt(angle)})">
      <rect x="-46" y="-13" width="50" height="26" rx="7" fill="{body}"/>
      <rect x="-38" y="-17" width="7" height="34" rx="3" fill="{ridge}" opacity="{op}"/>
      <rect x="-24" y="-17" width="7" height="34" rx="3" fill="{ridge}" opacity="{op}"/>
      <rect x="0" y="-32" width="84" height="64" rx="16" fill="{body}"/>
      <rect x="82" y="-21" width="40" height="11" rx="3" fill="{blade}"/>
      <rect x="82" y="10" width="40" height="11" rx="3" fill="{blade}"/>
    </g>'''

def defs(uid=''):
    return f'''<defs>
    <linearGradient id="gLetter{uid}" x1="0" y1="0" x2="0.25" y2="1">
      <stop offset="0" stop-color="{BLUE_L}"/><stop offset="0.55" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE_D}"/>
    </linearGradient>
    <linearGradient id="gBolt{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{ELEC_L}"/><stop offset="0.5" stop-color="{ELEC}"/><stop offset="1" stop-color="{BLUE_L}"/>
    </linearGradient>
    <linearGradient id="gCord{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE_D}"/><stop offset="0.6" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE_L}"/>
    </linearGradient>
    <linearGradient id="gPlug{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BLUE_L}"/><stop offset="1" stop-color="{BLUE_D}"/>
    </linearGradient>
    <linearGradient id="gBlade{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F2F5F8"/><stop offset="1" stop-color="{STEEL_D}"/>
    </linearGradient>
  </defs>'''

def mark(mono=None, on_dark=False, cord=True):
    """JS + bolt (+ cord & plug). Coordinates in the 800x520 mark box."""
    letter_fill = mono or 'url(#gLetter)'
    bolt_fill = mono or 'url(#gBolt)'
    cord_fill = mono or 'url(#gCord)'
    knock = NAVY if on_dark else WHITE
    parts = []
    if cord:
        parts.append(f'<path d="{CORD}" fill="none" stroke="{cord_fill}" stroke-width="22" stroke-linecap="round"/>')
        if not mono:
            parts.append(f'<path d="{CORD}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity="0.28" transform="translate(0 -5)"/>')
        parts.append(plug(*PLUG_AT, PLUG_ANG, mono))
    parts.append(letters(letter_fill))
    parts.append(bolt(knock, bolt_fill))
    return '<g id="mark">\n    ' + '\n    '.join(parts) + '\n  </g>'

# --------------------------------------------------------------------------
# Wordmark
# --------------------------------------------------------------------------
def fit(text, wght, target_w, tracking):
    t = tp(SAIRA, wght)
    w100 = t.width(text, 100, tracking)
    size = 100 * target_w / w100
    d, w = t.path(text, size, tracking)
    return d, size, w, t.cap_height / 1000 * size

def wordmark_stacked(cx, top, width, c1, c2):
    d1, s1, w1, cap1 = fit("CONTRACTING", 800, width, 0.02)
    d2, s2, w2, cap2 = fit("& ELECTRICAL SERVICES", 600, width * 0.985, 0.16)
    y1 = top + cap1
    y2 = y1 + cap1 * 0.42 + cap2
    return (f'<g id="wordmark">\n'
            f'    <path transform="translate({fmt(cx - w1/2)} {fmt(y1)})" d="{d1}" fill="{c1}"/>\n'
            f'    <path transform="translate({fmt(cx - w2/2)} {fmt(y2)})" d="{d2}" fill="{c2}"/>\n  </g>'), y2

def wordmark_side(x, center_y, width, c1, c2):
    """Two-line wordmark for the horizontal lockup, vertically centred on center_y.
    Line 2 is sized at 66% of line 1 so it stays legible at header sizes."""
    d1, s1, w1, cap1 = fit("CONTRACTING &", 800, width, 0.02)
    t2 = tp(SAIRA, 700)
    s2 = s1 * 0.66
    tr = 0.06
    d2, w2 = t2.path("ELECTRICAL SERVICES", s2, tr)
    if w2 > width * 1.01:
        tr = max(0.0, tr - (w2 - width) / (18 * s2))
        d2, w2 = t2.path("ELECTRICAL SERVICES", s2, tr)
    cap2 = t2.cap_height / 1000 * s2
    gap = cap1 * 0.36
    block = cap1 + gap + cap2
    y1 = center_y - block / 2 + cap1
    y2 = y1 + gap + cap2
    return (f'<g id="wordmark">\n'
            f'    <path transform="translate({fmt(x)} {fmt(y1)})" d="{d1}" fill="{c1}"/>\n'
            f'    <path transform="translate({fmt(x)} {fmt(y2)})" d="{d2}" fill="{c2}"/>\n  </g>'), y2

def svg(vb_w, vb_h, body, bg=None, label="JS Contracting & Electrical Services logo"):
    bgrect = f'\n  <rect width="{vb_w}" height="{vb_h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" role="img" aria-labelledby="t">\n'
            f'  <title id="t">{label.replace("&", "&amp;")}</title>\n  {defs()}{bgrect}\n  {body}\n</svg>\n')

# --------------------------------------------------------------------------
# Lockups
# --------------------------------------------------------------------------
def primary(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    wm, _ = wordmark_stacked(400, 560, 700, c1, c2)
    return svg(800, 800, mark(mono, on_dark) + '\n  ' + wm, bg)

def horizontal(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    m = f'<g transform="translate(0 20) scale(0.62)">\n  {mark(mono, on_dark)}\n  </g>'
    wm, _ = wordmark_side(556, 186, 700, c1, c2)
    return svg(1280, 380, m + '\n  ' + wm, bg)

def icon(bg=NAVY, mono=None):
    # 512 square, rounded; JS + bolt only, centred
    m = mark(mono=mono, on_dark=True, cord=False)
    # letters span x 131..693, y 85..419 -> centre (412, 252); scale 0.72
    body = (f'<rect width="512" height="512" rx="96" fill="{bg}"/>\n'
            f'  <g transform="translate(256 256) scale(0.7) translate(-412 -250)">\n  {m}\n  </g>')
    return svg(512, 512, body, label="JS Contracting & Electrical Services")

def favicon():
    m = mark(mono=None, on_dark=True, cord=False)
    body = (f'<rect width="512" height="512" rx="112" fill="{NAVY}"/>\n'
            f'  <g transform="translate(256 256) scale(0.8) translate(-412 -250)">\n  {m}\n  </g>')
    return svg(512, 512, body, label="JS")

ROOF = "M 96 105 L 436 -40 L 776 105"
def mark_home(mono=None, on_dark=False, bg=None):
    """Alternate mark: roofline over the JS, bolt strikes through the ridge."""
    roof_fill = mono or 'url(#gCord)'
    m = mark(mono, on_dark)
    roof = (f'<path d="{ROOF}" fill="none" stroke="{roof_fill}" stroke-width="30" stroke-linejoin="miter" stroke-linecap="butt"/>'
            f'<rect x="660" y="6" width="44" height="72" fill="{roof_fill}"/>')
    # insert roof before letters (behind bolt knockout)
    m = m.replace('<g id="mark">\n    ', '<g id="mark">\n    ' + roof + '\n    ', 1)
    body = f'<g transform="translate(0 70)">{m}</g>'
    return svg(800, 590, body, bg)

def primary_home(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    roof_fill = mono or 'url(#gCord)'
    m = mark(mono, on_dark)
    roof = (f'<path d="{ROOF}" fill="none" stroke="{roof_fill}" stroke-width="30" stroke-linejoin="miter" stroke-linecap="butt"/>'
            f'<rect x="660" y="6" width="44" height="72" fill="{roof_fill}"/>')
    m = m.replace('<g id="mark">\n    ', '<g id="mark">\n    ' + roof + '\n    ', 1)
    wm, _ = wordmark_stacked(400, 630, 700, c1, c2)
    return svg(800, 870, f'<g transform="translate(0 70)">{m}</g>\n  ' + wm, bg)

def mark_only(mono=None, on_dark=False, bg=None):
    return svg(800, 520, mark(mono, on_dark), bg)

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    files = {
        'js-logo-primary.svg': primary(),
        'js-logo-primary-reverse.svg': primary(on_dark=True, bg=NAVY),
        'js-logo-primary-mono.svg': primary(mono=NAVY),
        'js-logo-primary-white.svg': primary(mono=WHITE, on_dark=True),
        'js-logo-horizontal.svg': horizontal(),
        'js-logo-horizontal-reverse.svg': horizontal(on_dark=True, bg=NAVY),
        'js-logo-horizontal-mono.svg': horizontal(mono=NAVY),
        'js-logo-horizontal-white.svg': horizontal(mono=WHITE, on_dark=True),
        'js-mark.svg': mark_only(),
        'js-mark-mono.svg': mark_only(mono=NAVY),
        'js-mark-reverse.svg': mark_only(on_dark=True),
        'js-mark-white.svg': mark_only(mono=WHITE, on_dark=True),
        'js-icon.svg': icon(),
        'alt-js-mark-home.svg': mark_home(),
        'alt-js-logo-home.svg': primary_home(),
        'alt-js-logo-home-reverse.svg': primary_home(on_dark=True, bg=NAVY),
        'alt-js-mark-home-mono.svg': mark_home(mono=NAVY),
        'favicon.svg': favicon(),
    }
    for n, s in files.items():
        open(os.path.join(out, n), 'w').write(s)
    print('wrote', len(files), 'files')
