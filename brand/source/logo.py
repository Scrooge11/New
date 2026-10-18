"""Generate JEMCO Contracting & Electrical Services logo SVGs.
Run: python3 logo.py <outdir>
Letterforms: Saira Black Italic (SIL OFL) converted to outlines. The E is rebuilt as a polygon with its
middle arm replaced by a lightning bolt; the cord and plug are drawn geometrically.
"""
import sys, os, math, re
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
# Mark geometry. Box: 0..1760 x 0..540. Baseline of letters y=390, cap height 330 (cap top y=60).
# --------------------------------------------------------------------------
CAP = 330
BASE = 390
X0 = 92            # origin of the J
GAP_E = 60         # extra space after the E so the bolt has room before the M
MARK_W, MARK_H = 1760, 540

# Bolt that replaces the middle arm of the E: the brand's lightning bolt rotated to point right and a little
# down, anchored inside the stem so it looks like it comes out of the letter (E-local coordinates, baseline y=0).
_BOLT_BASE = [(356, 40), (256, 238), (324, 238), (262, 452), (398, 212), (334, 212)]
def rotated_bolt(theta_deg, k, ax, ay):
    th = math.radians(theta_deg); c, sn = math.sin(th) * 0 + math.cos(th), math.sin(th)
    ox, oy = _BOLT_BASE[0]
    return [(ax + k * ((x - ox) * c - (y - oy) * sn), ay + k * ((x - ox) * sn + (y - oy) * c)) for x, y in _BOLT_BASE]
BOLT_E = rotated_bolt(-83, 0.64, 82, -170)

# Cord from the hook of the J, under the word, to the plug.
PLUG_AT = (1562.0, 446.0)
PLUG_ANG = -8.0
CORD = (f"M {fmt(X0-14)} {fmt(BASE-38)} C {fmt(X0-86)} {fmt(BASE+58)}, {fmt(X0-30)} {fmt(BASE+82)}, {fmt(X0+300)} {fmt(BASE+82)} "
        f"C {fmt(X0+900)} {fmt(BASE+82)}, {fmt(PLUG_AT[0]-220)} {fmt(BASE+82)}, {fmt(PLUG_AT[0])} {fmt(PLUG_AT[1])}")

def poly(pts):
    return 'M ' + ' L '.join('%s %s' % (fmt(x), fmt(y)) for x, y in pts) + ' Z'

def parse_polygon(d):
    """Absolute M/L/H/V/Z path (straight lines only) -> list of points."""
    toks = re.findall(r'[MLHVZ]|-?\d+\.?\d*', d)
    pts, cmd, x, y, i = [], None, 0.0, 0.0, 0
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVZ':
            cmd = t; i += 1
            if cmd == 'Z': break
            continue
        if cmd in ('M', 'L'):
            x, y = float(t), float(toks[i+1]); i += 2
        elif cmd == 'H':
            x = float(t); i += 1
        elif cmd == 'V':
            y = float(t); i += 1
        pts.append((x, y))
        if cmd == 'M': cmd = 'L'
    return pts

_glyphs = None
def glyphs():
    """Shaped JEMCO: list of (char, x, path_d) in mark coordinates, plus the E polygon without its middle arm."""
    global _glyphs
    if _glyphs is None:
        t = tp(SAIRA_I, 900)
        size = CAP / (t.cap_height / 1000.0)
        s = size / t.upem
        out, x = [], X0
        for ch, (g, adv, xo, yo) in zip("JEMCO", t._shape("JEMCO")):
            if ch == 'E':
                d, _ = t.path('E', size)
                pts = parse_polygon(d)
                # drop the two outer corners of the middle arm; the stem edge between the arms stays
                keep = [p for p in pts if not (abs(p[1] + 205.8) < 0.5 and p[0] > 200) and not (abs(p[1] + 127.6) < 0.5 and p[0] > 200)]
                out.append((ch, x, poly(keep)))
            else:
                d, _ = t.path(ch, size)
                out.append((ch, x, d))
            x += adv * s + (GAP_E if ch == 'E' else 0)
        _glyphs = out
    return _glyphs

def letters(fill):
    return '\n    '.join(f'<path transform="translate({fmt(x)} {BASE})" d="{d}" fill="{fill}"/>' for ch, x, d in glyphs())

def e_origin():
    return [x for ch, x, d in glyphs() if ch == 'E'][0]

def bolt(fill, x=None, y=BASE):
    """The bolt is drawn before the letters, so the stem of the E covers its root: no knockout needed."""
    x = e_origin() if x is None else x
    return f'<path transform="translate({fmt(x)} {fmt(y)})" d="{poly(BOLT_E)}" fill="{fill}"/>'

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
    """JEMCO with the bolt E (+ cord & plug). Coordinates in the 1760x540 mark box."""
    letter_fill = mono or 'url(#gLetter)'
    bolt_fill = mono or 'url(#gBolt)'
    cord_fill = mono or 'url(#gCord)'
    parts = []
    if cord:
        parts.append(f'<path d="{CORD}" fill="none" stroke="{cord_fill}" stroke-width="22" stroke-linecap="round"/>')
        if not mono:
            parts.append(f'<path d="{CORD}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity="0.28" transform="translate(0 -5)"/>')
        parts.append(plug(*PLUG_AT, PLUG_ANG, mono))
    parts.append(bolt(bolt_fill))
    parts.append(letters(letter_fill))
    return '<g id="mark">\n    ' + '\n    '.join(parts) + '\n  </g>'

def bolt_e(mono=None, on_dark=False):
    """The E with the bolt, alone, at the E's own origin (for icons)."""
    letter_fill = mono or 'url(#gLetter)'
    bolt_fill = mono or 'url(#gBolt)'
    d = [d for ch, x, d in glyphs() if ch == 'E'][0]
    return (f'<g id="bolt-e">\n    ' + bolt(bolt_fill, x=0, y=0) + f'\n    <path d="{d}" fill="{letter_fill}"/>\n  </g>')

# --------------------------------------------------------------------------
# Wordmark
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

def svg(vb_w, vb_h, body, bg=None, label=NAME + " logo"):
    bgrect = f'\n  <rect width="{vb_w}" height="{vb_h}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" role="img" aria-labelledby="t">\n'
            f'  <title id="t">{label.replace("&", "&amp;")}</title>\n  {defs()}{bgrect}\n  {body}\n</svg>\n')

# --------------------------------------------------------------------------
# Lockups
# --------------------------------------------------------------------------
LETTERS_CX = 872   # visual centre of the word (J hook at x=73, O right edge at x=1672)
def primary(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    wm, _ = wordmark_line(LETTERS_CX, 548, 1500, c1, c2)
    return svg(MARK_W, 700, mark(mono, on_dark) + '\n  ' + wm, bg)

def horizontal(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    s = 0.62
    m = f'<g transform="translate(0 22) scale({s})">\n  {mark(mono, on_dark)}\n  </g>'
    x = MARK_W * s + 40
    wm, _ = wordmark_side(x, 190, 700, c1, c2)
    return svg(int(x + 700 + 40), 380, m + '\n  ' + wm, bg)

def icon(bg=NAVY, mono=None):
    # 512 square, rounded; the bolt E only, centred (E + bolt spans x -2..354, y -330..0)
    e = bolt_e(mono=mono, on_dark=True)
    body = (f'<rect width="512" height="512" rx="96" fill="{bg}"/>\n'
            f'  <g transform="translate(256 256) scale(1.02) translate(-168 165)">\n  {e}\n  </g>')
    return svg(512, 512, body, label=NAME)

def favicon():
    e = bolt_e(on_dark=True)
    body = (f'<rect width="512" height="512" rx="112" fill="{NAVY}"/>\n'
            f'  <g transform="translate(256 256) scale(1.18) translate(-168 165)">\n  {e}\n  </g>')
    return svg(512, 512, body, label="JEMCO")

ROOF_APEX = (868, -290)
ROOF = f"M 140 24 L {ROOF_APEX[0]} {ROOF_APEX[1]} L 1600 24"
def _roof(fill):
    # chimney on the right slope
    cx = 1400
    slope = (24 - ROOF_APEX[1]) / (1600 - ROOF_APEX[0])
    ry = ROOF_APEX[1] + (cx - ROOF_APEX[0]) * slope
    return (f'<path d="{ROOF}" fill="none" stroke="{fill}" stroke-width="30" stroke-linejoin="miter" stroke-linecap="butt"/>'
            f'<rect x="{cx}" y="{fmt(ry - 100)}" width="48" height="{fmt(100 + 14)}" fill="{fill}"/>')

def mark_home(mono=None, on_dark=False, bg=None):
    """Alternate mark: roofline over JEMCO, ridge above the M."""
    roof_fill = mono or 'url(#gCord)'
    m = mark(mono, on_dark)
    m = m.replace('<g id="mark">\n    ', '<g id="mark">\n    ' + _roof(roof_fill) + '\n    ', 1)
    body = f'<g transform="translate(0 320)">{m}</g>'
    return svg(MARK_W, 860, body, bg)

def primary_home(mono=None, on_dark=False, bg=None):
    c1 = mono or (WHITE if on_dark else NAVY)
    c2 = mono or (ELEC if on_dark else BLUE)
    roof_fill = mono or 'url(#gCord)'
    m = mark(mono, on_dark)
    m = m.replace('<g id="mark">\n    ', '<g id="mark">\n    ' + _roof(roof_fill) + '\n    ', 1)
    wm, _ = wordmark_line(LETTERS_CX, 548 + 320, 1500, c1, c2)
    return svg(MARK_W, 1020, f'<g transform="translate(0 320)">{m}</g>\n  ' + wm, bg)

def mark_only(mono=None, on_dark=False, bg=None):
    return svg(MARK_W, MARK_H, mark(mono, on_dark), bg)

def word_only(mono=None, on_dark=False, bg=None):
    """JEMCO with the bolt E, no cord: for places that need the name alone."""
    return svg(MARK_W, 450, mark(mono, on_dark, cord=False), bg)

FILES = {
    'jemco-logo-primary.svg': lambda: primary(),
    'jemco-logo-primary-reverse.svg': lambda: primary(on_dark=True, bg=NAVY),
    'jemco-logo-primary-mono.svg': lambda: primary(mono=NAVY),
    'jemco-logo-primary-white.svg': lambda: primary(mono=WHITE, on_dark=True),
    'jemco-logo-horizontal.svg': lambda: horizontal(),
    'jemco-logo-horizontal-reverse.svg': lambda: horizontal(on_dark=True, bg=NAVY),
    'jemco-logo-horizontal-mono.svg': lambda: horizontal(mono=NAVY),
    'jemco-logo-horizontal-white.svg': lambda: horizontal(mono=WHITE, on_dark=True),
    'jemco-mark.svg': lambda: mark_only(),
    'jemco-mark-mono.svg': lambda: mark_only(mono=NAVY),
    'jemco-mark-reverse.svg': lambda: mark_only(on_dark=True),
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
