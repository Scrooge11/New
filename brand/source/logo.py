"""Generate JEMCO Contracting & Electrical Services logo SVGs.
Run: python3 logo.py <outdir>
Letterforms: Saira Black Italic (SIL OFL) converted to outlines. The lightning bolt under the name is drawn
geometrically; it is the one device of the brand and it stands in for an underline.
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
WHITE   = '#FFFFFF'

NAME = "JEMCO Contracting & Electrical Services"

def fmt(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')

_tp = {}
def tp(font, wght, wdth=100):
    k = (font, wght, wdth)
    if k not in _tp:
        _tp[k] = TextPath(font, {'wght': wght, 'wdth': wdth})
    return _tp[k]

# --------------------------------------------------------------------------
# Mark geometry. Box: 0..1760 x 0..600. Baseline of letters y=390, cap height 330 (cap top y=60).
# The word spans x 73 (hook of the J) .. 1612 (right edge of the O).
# --------------------------------------------------------------------------
CAP = 330
BASE = 390
X0 = 110
MARK_W, MARK_H = 1760, 600
LETTERS_CX = 860

# The bolt: a long zigzag under the word, tucked under the hook of the J, pointing past the O.
# Local coordinates (y down), then lifted 2 degrees so it rises toward the tip.
def staple_points(L=1640, tilt=-2.5):
    A1, A2 = (8, -40), (0, -4)           # left end, cut on the italic slant
    E1, D1 = (430, -50), (376, -104)     # upper edge: the step up, under the E
    C1, B1 = (470, -22), (526, 30)       # lower edge: the step
    T = (L, 14)                          # the tip, a long taper past the O
    pts = [A1, E1, D1, T, C1, B1, A2]
    th = math.radians(tilt); c, s = math.cos(th), math.sin(th)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]
STAPLE_AT = (X0 - 20, BASE + 128)

# The bolt that strikes through the stem of the J, pointing down and to the left, out of the letter.
def jbolt_points(theta_deg=60.0, k=0.72, ax=X0 + 190, ay=BASE - 215):
    th = math.radians(theta_deg); c, s = math.cos(th), math.sin(th)
    ox, oy = BOLT_PTS[0]
    return [(ax + k * ((x - ox) * c - (y - oy) * s), ay + k * ((x - ox) * s + (y - oy) * c)) for x, y in BOLT_PTS]

# The brand bolt on its own (vertical), used for the favicon.
BOLT_PTS = [(356, 40), (256, 238), (324, 238), (262, 452), (398, 212), (334, 212)]

def poly(pts):
    return 'M ' + ' L '.join('%s %s' % (fmt(x), fmt(y)) for x, y in pts) + ' Z'

_glyphs = None
def glyphs():
    """Shaped JEMCO: list of (char, x, path_d) in mark coordinates."""
    global _glyphs
    if _glyphs is None:
        t = tp(SAIRA_I, 900)
        size = CAP / (t.cap_height / 1000.0)
        s = size / t.upem
        out, x = [], X0
        for ch, (g, adv, xo, yo) in zip("JEMCO", t._shape("JEMCO")):
            d, _ = t.path(ch, size)
            out.append((ch, x, d))
            x += adv * s
        _glyphs = out
    return _glyphs

def letters(fill):
    return '\n    '.join(f'<path transform="translate({fmt(x)} {BASE})" d="{d}" fill="{fill}"/>' for ch, x, d in glyphs())

def staple(fill):
    return f'<path transform="translate({fmt(STAPLE_AT[0])} {fmt(STAPLE_AT[1])})" d="{poly(staple_points())}" fill="{fill}"/>'

def jbolt(fill, knock, dx=0, dy=0):
    d = poly(jbolt_points())
    g = f'<g transform="translate({fmt(dx)} {fmt(dy)})">' if (dx or dy) else '<g>'
    return (g + f'\n      <path d="{d}" fill="{knock}" stroke="{knock}" stroke-width="26" stroke-linejoin="miter" stroke-miterlimit="8"/>'
            f'\n      <path d="{d}" fill="{fill}"/>\n    </g>')

def defs(uid=''):
    return f'''<defs>
    <linearGradient id="gLetter{uid}" x1="0" y1="0" x2="0.25" y2="1">
      <stop offset="0" stop-color="{BLUE_L}"/><stop offset="0.55" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE_D}"/>
    </linearGradient>
    <linearGradient id="gLetterW{uid}" x1="0" y1="0" x2="0.25" y2="1">
      <stop offset="0" stop-color="{WHITE}"/><stop offset="0.6" stop-color="#EEF4FF"/><stop offset="1" stop-color="#BFD3F2"/>
    </linearGradient>
    <linearGradient id="gBolt{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE}"/><stop offset="0.55" stop-color="{ELEC}"/><stop offset="1" stop-color="{ELEC_L}"/>
    </linearGradient>
    <linearGradient id="gBoltV{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{ELEC_L}"/><stop offset="0.5" stop-color="{ELEC}"/><stop offset="1" stop-color="{BLUE_L}"/>
    </linearGradient>
    <linearGradient id="gRoof{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE_D}"/><stop offset="0.6" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE_L}"/>
    </linearGradient>
  </defs>'''

def mark(mono=None, bolt=True, on_dark=False, jb=True):
    """JEMCO with the bolt through the J and the streak underneath. Coordinates in the 1760x600 mark box."""
    letter_fill = mono or ('url(#gLetterW)' if on_dark else 'url(#gLetter)')
    bolt_fill = mono or ('url(#gBoltV)' if on_dark else 'url(#gBolt)')
    knock = NAVY if on_dark else WHITE
    parts = []
    if bolt:
        parts.append(staple(bolt_fill))
    parts.append(letters(letter_fill))
    if jb:
        parts.append(jbolt(mono or 'url(#gBoltV)', knock))
    return '<g id="mark">\n    ' + '\n    '.join(parts) + '\n  </g>'

# --------------------------------------------------------------------------
# Wordmark (the descriptor line)
# --------------------------------------------------------------------------
def fit(text, wght, target_w, tracking):
    t = tp(SAIRA, wght)
    w100 = t.width(text, 100, tracking)
    size = 100 * target_w / w100
    d, w = t.path(text, size, tracking)
    return d, size, w, t.cap_height / 1000 * size

def wordmark_line(cx, top, width, c1, c2):
    """One line, 'CONTRACTING' in c1 and '& ELECTRICAL SERVICES' in c2, fitted to width."""
    t = tp(SAIRA, 700)
    tr = 0.12
    a, b = "CONTRACTING", "& ELECTRICAL SERVICES"
    wa, wb = t.width(a, 100, tr), t.width(b, 100, tr)
    space = 100 * 0.42
    size = 100 * width / (wa + space + wb)
    da, wa = t.path(a, size, tr)
    db, wb = t.path(b, size, tr)
    cap = t.cap_height / 1000 * size
    x = cx - (wa + space * size / 100 + wb) / 2
    y = top + cap
    return (f'<g id="wordmark">\n'
            f'    <path transform="translate({fmt(x)} {fmt(y)})" d="{da}" fill="{c1}"/>\n'
            f'    <path transform="translate({fmt(x + wa + space * size / 100)} {fmt(y)})" d="{db}" fill="{c2}"/>\n  </g>'), y

def wordmark_side(x, center_y, width, c1, c2):
    """Two-line descriptor for the horizontal lockup, vertically centred on center_y.
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

def svg(vb_w, vb_h, body, bg=None, label=NAME + " logo"):
    bgrect = f'\n  <rect width="{vb_w}" height="{vb_h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" role="img" aria-labelledby="t">\n'
            f'  <title id="t">{label.replace("&", "&amp;")}</title>\n  {defs()}{bgrect}\n  {body}\n</svg>\n')

# --------------------------------------------------------------------------
# Lockups
# --------------------------------------------------------------------------
def primary(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    wm, _ = wordmark_line(LETTERS_CX, 628, 1480, c1, c2)
    return svg(MARK_W, 760, mark(mono, on_dark=on_dark) + '\n  ' + wm, bg)

def horizontal(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    s = 0.6
    m = f'<g transform="translate(0 10) scale({s})">\n  {mark(mono, on_dark=on_dark)}\n  </g>'
    x = MARK_W * s + 30
    wm, _ = wordmark_side(x, 190, 700, c1, c2)
    return svg(int(x + 700 + 40), 380, m + '\n  ' + wm, bg)

def jmark(scale, fill='url(#gLetterW)'):
    """The J with the bolt through it, centred on the origin (J spans x 73..320, y 60..390; bolt tip to x ~24)."""
    ch, x, d = glyphs()[0]
    body = (f'<path transform="translate({fmt(x)} {BASE})" d="{d}" fill="{fill}"/>\n    ' + jbolt('url(#gBoltV)', NAVY))
    return f'<g transform="scale({fmt(scale)}) translate(-174 -225)">\n    {body}\n  </g>'

def icon(bg=NAVY, mono=None):
    # 512 square, rounded; the J with the bolt, as on the reference
    return svg(512, 512, (f'<rect width="512" height="512" rx="96" fill="{bg}"/>\n'
                          f'  <g transform="translate(262 256)">{jmark(1.05)}</g>'), label=NAME)

def favicon():
    return svg(512, 512, (f'<rect width="512" height="512" rx="112" fill="{NAVY}"/>\n'
                          f'  <g transform="translate(266 256)">{jmark(1.22)}</g>'), label="JEMCO")

ROOF_APEX = (860, -290)
ROOF = f"M 128 24 L {ROOF_APEX[0]} {ROOF_APEX[1]} L 1592 24"
def _roof(fill):
    cx = 1400
    slope = (24 - ROOF_APEX[1]) / (1592 - ROOF_APEX[0])
    ry = ROOF_APEX[1] + (cx - ROOF_APEX[0]) * slope
    return (f'<path d="{ROOF}" fill="none" stroke="{fill}" stroke-width="30" stroke-linejoin="miter" stroke-linecap="butt"/>'
            f'<rect x="{cx}" y="{fmt(ry - 100)}" width="48" height="{fmt(100 + 14)}" fill="{fill}"/>')

def mark_home(mono=None, on_dark=False, bg=None):
    """Alternate mark: roofline over JEMCO, ridge above the M, the bolt underneath."""
    roof_fill = mono or ('url(#gBoltV)' if on_dark else 'url(#gRoof)')
    m = mark(mono, on_dark=on_dark)
    m = m.replace('<g id="mark">\n    ', '<g id="mark">\n    ' + _roof(roof_fill) + '\n    ', 1)
    return svg(MARK_W, 920, f'<g transform="translate(0 320)">{m}</g>', bg)

def primary_home(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    roof_fill = mono or ('url(#gBoltV)' if on_dark else 'url(#gRoof)')
    m = mark(mono, on_dark=on_dark)
    m = m.replace('<g id="mark">\n    ', '<g id="mark">\n    ' + _roof(roof_fill) + '\n    ', 1)
    wm, _ = wordmark_line(LETTERS_CX, 628 + 320, 1480, c1, c2)
    return svg(MARK_W, 1080, f'<g transform="translate(0 320)">{m}</g>\n  ' + wm, bg)

def mark_only(mono=None, on_dark=False, bg=None):
    return svg(MARK_W, MARK_H, mark(mono, on_dark=on_dark), bg)

def word_only(mono=None, on_dark=False, bg=None):
    """JEMCO with the bolt through the J, no streak: for narrow spaces."""
    return svg(MARK_W, 450, mark(mono, bolt=False, on_dark=on_dark), bg)

FILES = {
    'jemco-logo-primary.svg': lambda: primary(),
    'jemco-logo-primary-reverse.svg': lambda: primary(on_dark=True, bg=NAVY),
    'jemco-logo-primary-mono.svg': lambda: primary(mono=NAVY),
    'jemco-logo-primary-white.svg': lambda: primary(mono=WHITE, on_dark=True),
    'jemco-logo-horizontal.svg': lambda: horizontal(),
    'jemco-logo-horizontal-reverse.svg': lambda: horizontal(on_dark=True, bg=NAVY),
    'jemco-logo-horizontal-mono.svg': lambda: horizontal(mono=NAVY),
    'jemco-logo-horizontal-white.svg': lambda: horizontal(mono=WHITE, on_dark=True),
    'jemco-logo-horizontal-ondark.svg': lambda: horizontal(on_dark=True),
    'jemco-mark.svg': lambda: mark_only(),
    'jemco-mark-mono.svg': lambda: mark_only(mono=NAVY),
    'jemco-mark-reverse.svg': lambda: mark_only(on_dark=True),
    'jemco-mark-reverse-bg.svg': lambda: mark_only(on_dark=True, bg=NAVY),
    'jemco-mark-white.svg': lambda: mark_only(mono=WHITE, on_dark=True),
    'jemco-word.svg': lambda: word_only(),
    'jemco-word-white.svg': lambda: word_only(mono=WHITE, on_dark=True),
    'jemco-icon.svg': lambda: icon(),
    'alt-jemco-mark-home.svg': lambda: mark_home(),
    'alt-jemco-mark-home-reverse.svg': lambda: mark_home(on_dark=True),
    'alt-jemco-logo-home.svg': lambda: primary_home(),
    'alt-jemco-logo-home-reverse.svg': lambda: primary_home(on_dark=True, bg=NAVY),
    'alt-jemco-mark-home-mono.svg': lambda: mark_home(mono=NAVY),
    'favicon.svg': lambda: favicon(),
}

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, f in FILES.items():
        open(os.path.join(out, n), 'w').write(f())
    print('wrote', len(FILES), 'files')
