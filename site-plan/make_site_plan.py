"""Draw the proposed house placements on top of the PLACES Associates ECP sheet.
Outputs a multi-sheet PDF (same 18x24 sheet, same 1"=10' scale as the ECP) and PNG previews."""
import math, os
import pymupdf
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union, nearest_points
import geometry as G
from analysis import ENV, feasible_T, pick_translation, part_report, line_of, max_projection

ECP = os.environ.get("ECP_PDF", "/root/.claude/uploads/0c69f11e-6262-51c7-8647-ea16206f0d07/391613af-5827_-_ECP_9-22-2026.pdf")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUT_PDF = os.path.join(OUT_DIR, "199-Central-St_Proposed-Site-Plan.pdf")

BLUE = (0.05, 0.25, 0.75); BLUE_FILL = (0.62, 0.78, 1.0)
TAN = (0.75, 0.55, 0.25); TAN_FILL = (0.96, 0.9, 0.75)
RED = (0.85, 0.05, 0.05); ORANGE = (0.95, 0.5, 0.0); GRAY = (0.45, 0.45, 0.45); DGRAY = (0.25, 0.25, 0.25)
DRIVE_FILL = (0.82, 0.82, 0.82); WHITE = (1, 1, 1); BLACK = (0, 0, 0); PINK = (1, 0.75, 0.75)
P = G.ft2pt

# ------------------------------------------------------------------ drawing helpers
def _polys(g):
    if g.geom_type == "Polygon": return [g]
    if g.geom_type == "MultiPolygon": return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]

def draw_poly(shape, poly, color=BLACK, fill=None, width=1.0, dashes=None, fill_opacity=1.0, stroke_opacity=1.0):
    for pg in _polys(poly):
        shape.draw_polyline([pymupdf.Point(*P(x, y)) for x, y in pg.exterior.coords])
        shape.finish(color=color, fill=fill, width=width, dashes=dashes, closePath=True,
                     fill_opacity=fill_opacity, stroke_opacity=stroke_opacity)

def draw_hatch(shape, poly, spacing_ft=1.5, color=BLUE, width=0.5, angle=45):
    minx, miny, maxx, maxy = poly.bounds
    L = max(maxx-minx, maxy-miny) * 2; cx, cy = (minx+maxx)/2, (miny+maxy)/2
    n = int(L / spacing_ft) + 2; a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    for i in range(-n, n+1):
        ox, oy = cx + nx*i*spacing_ft, cy + ny*i*spacing_ft
        ln = LineString([(ox-ux*L, oy-uy*L), (ox+ux*L, oy+uy*L)]).intersection(poly)
        if ln.is_empty: continue
        for g in ([ln] if ln.geom_type == "LineString" else [g for g in ln.geoms if g.geom_type == "LineString"]):
            c = list(g.coords); shape.draw_line(pymupdf.Point(*P(*c[0])), pymupdf.Point(*P(*c[-1])))
    shape.finish(color=color, width=width)

def text(page, x_ft, y_ft, s, size=7, color=BLACK, angle=0.0, align="left", font="helv"):
    pt = pymupdf.Point(*P(x_ft, y_ft)); w = pymupdf.get_text_length(s, fontname=font, fontsize=size)
    if align == "center": pt = pt + pymupdf.Point(-w/2, 0)
    elif align == "right": pt = pt + pymupdf.Point(-w, 0)
    if angle:
        page.insert_text(pt, s, fontsize=size, fontname=font, color=color, morph=(pymupdf.Point(*P(x_ft, y_ft)), pymupdf.Matrix(-angle)))
    else:
        page.insert_text(pt, s, fontsize=size, fontname=font, color=color)

def wrap(s, width_pt, size, font="helv"):
    words = s.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if pymupdf.get_text_length(t, fontname=font, fontsize=size) <= width_pt or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def _textbox_height(r, paras, size, title, title_size, lh):
    y = 4 + (title_size*1.5 if title else 0); usable = r.width - 10
    for p in paras:
        if p == "": y += size*0.7; continue
        bold = p.startswith("**"); s = p[2:] if bold else p
        y += size*lh*len(wrap(s, usable, size, "hebo" if bold else "helv"))
    return y + 4

def textbox(page, rect_pt, paras, size=None, color=BLACK, title=None, title_size=8.5, fill=WHITE, border=BLACK, lh=1.22):
    """paras: list of strings. '**' prefix = bold; '' = blank line. Long lines wrap. size=None -> largest that fits (7.2..5.2)."""
    r = pymupdf.Rect(*rect_pt)
    if size is None:
        size = 5.2
        for s in [7.2, 7.0, 6.8, 6.6, 6.4, 6.2, 6.0, 5.8, 5.6, 5.4, 5.2]:
            if _textbox_height(r, paras, s, title, title_size, lh) <= r.height: size = s; break
    sh = page.new_shape(); sh.draw_rect(r); sh.finish(color=border, fill=fill, width=0.8, fill_opacity=0.94); sh.commit()
    y = r.y0 + 4; usable = r.width - 10
    if title:
        page.insert_text((r.x0+5, y+title_size), title, fontsize=title_size, fontname="hebo", color=color); y += title_size*1.5
    for p in paras:
        if p == "": y += size*0.7; continue
        bold = p.startswith("**"); s = p[2:] if bold else p; font = "hebo" if bold else "helv"
        for ln in wrap(s, usable, size, font):
            page.insert_text((r.x0+5, y+size), ln, fontsize=size, fontname=font, color=color); y += size*lh
    if y > r.y1: print("WARNING: textbox overflow by %.0f pt (%s)" % (y-r.y1, title))
    return y

def arrow(shape, p_ft, q_ft, color=RED, width=0.7, head=3.5):
    p = pymupdf.Point(*P(*p_ft)); q = pymupdf.Point(*P(*q_ft))
    shape.draw_line(p, q); shape.finish(color=color, width=width)
    for a, b in ((p, q), (q, p)):
        d = b - a; L = abs(d)
        if L < 1e-6: continue
        d = d / L; n = pymupdf.Point(-d.y, d.x); base = a + d*head
        shape.draw_polyline([a, base + n*head*0.4, base - n*head*0.4]); shape.finish(color=color, fill=color, width=0.3, closePath=True)

def dim_to_line(page, shape, pt_ft, line_name, label_offset=(0, 0), color=RED, size=6.5):
    ln = line_of(line_name); q = nearest_points(Point(pt_ft), ln)[1]; d = Point(pt_ft).distance(ln)
    arrow(shape, pt_ft, (q.x, q.y), color=color)
    text(page, (pt_ft[0]+q.x)/2 + label_offset[0], (pt_ft[1]+q.y)/2 + label_offset[1] - 0.35, "%.1f'" % d, size=size, color=color, align="center")
    return d

HOUSE_V = None   # unit vector (sheet frame) of the house's front->rear axis, set per sheet

def corner(poly, which):
    """Corner of a placed rectangle in house terms: front = smallest projection on the house's
    front->rear axis (HOUSE_V); west = smaller sheet x within each pair."""
    cs = list(poly.exterior.coords)[:-1]
    vx, vy = HOUSE_V
    cs = sorted(cs, key=lambda c: c[0]*vx + c[1]*vy)
    front, rear = sorted(cs[:2]), sorted(cs[2:])
    return {"sw": front[0], "se": front[1], "nw": rear[0], "ne": rear[1]}[which]

def set_house_axis(theta):
    global HOUSE_V
    a = math.radians(theta); HOUSE_V = (-math.sin(a), math.cos(a))

# ------------------------------------------------------------------ sheet furniture
def sheet_base(doc, src):
    page = doc.new_page(width=src[0].rect.width, height=src[0].rect.height)
    page.show_pdf_page(page.rect, src, 0); return page

def fade_existing(page):
    sh = page.new_shape()
    for poly in (G.EXISTING_MAIN, G.EXISTING_BH):
        draw_poly(sh, poly, color=GRAY, fill=WHITE, width=0.9, dashes="[4 3] 0", fill_opacity=0.82)
    sh.commit()
    text(page, 44.5, 33.2, "EXISTING #199", size=6.5, color=GRAY, align="center")
    text(page, 44.5, 31.8, "TO BE REMOVED", size=6.5, color=GRAY, align="center")

def draw_envelope(page):
    sh = page.new_shape(); draw_poly(sh, ENV, color=ORANGE, width=1.6, dashes="[7 4] 0", stroke_opacity=0.9); sh.commit()

def banner(page, title, subtitle):
    r = pymupdf.Rect(340, 58, 796, 142)
    sh = page.new_shape(); sh.draw_rect(r); sh.finish(color=BLUE, fill=WHITE, width=1.4, fill_opacity=0.96); sh.commit()
    y = r.y0 + 13
    page.insert_text((r.x0+8, y), "CONCEPT SITE PLAN OVERLAY  -  NOT FOR CONSTRUCTION  -  NOT A SURVEY", fontsize=8, fontname="hebo", color=RED); y += 14
    for ln in wrap(title, r.width-16, 9.2, "hebo"):
        page.insert_text((r.x0+8, y), ln, fontsize=9.2, fontname="hebo", color=BLUE); y += 11
    for ln in wrap(subtitle, r.width-16, 6.6):
        page.insert_text((r.x0+8, y), ln, fontsize=6.6, fontname="helv", color=BLACK); y += 8
    for ln in wrap("Base drawing: PLACES Associates, Inc. Existing Conditions Plan, Project 5827 / Plan 5827-ECP dated Sept. 11, 2026 (1\"=10'). House: AFAB Enterprises 'New Single Family Residence' plan set (file 'Carter', sheets 1, 3, 4, 5; 1/4\"=1'-0\"). Overlay prepared %s." % "22 Sept. 2026", r.width-16, 5.6):
        page.insert_text((r.x0+8, y), ln, fontsize=5.6, fontname="helv", color=DGRAY); y += 6.8

def legend(page, items):
    r = pymupdf.Rect(66, 80, 282, 80 + 15*len(items) + 22)
    sh = page.new_shape(); sh.draw_rect(r); sh.finish(color=BLACK, fill=WHITE, width=0.8, fill_opacity=0.94); sh.commit()
    page.insert_text((r.x0+5, r.y0+12), "LEGEND", fontsize=8, fontname="hebo"); y = r.y0 + 21
    for (kind, color, fill, dash, label) in items:
        sh = page.new_shape(); box = pymupdf.Rect(r.x0+6, y, r.x0+28, y+9)
        if kind == "poly": sh.draw_rect(box); sh.finish(color=color, fill=fill, width=1.2, dashes=dash, fill_opacity=0.5 if fill else 1)
        elif kind == "line": sh.draw_line(pymupdf.Point(box.x0, box.y0+4.5), pymupdf.Point(box.x1, box.y0+4.5)); sh.finish(color=color, width=1.4, dashes=dash)
        elif kind == "tree":
            c = pymupdf.Point(box.x0+11, box.y0+4.5); sh.draw_circle(c, 4.5); sh.finish(color=RED, width=1.1)
            sh.draw_line(c+(-3, -3), c+(3, 3)); sh.draw_line(c+(-3, 3), c+(3, -3)); sh.finish(color=RED, width=1.1)
        sh.commit()
        page.insert_text((r.x0+33, y+7.5), label, fontsize=5.9, fontname="helv"); y += 15

STD_LEGEND = [
    ("poly", BLUE, BLUE_FILL, None, "Proposed dwelling: enclosed footprint (main body + garage bay)"),
    ("poly", BLUE, WHITE, None, "Covered front porch (roof extent; open sides)"),
    ("poly", TAN, TAN_FILL, None, "Rear deck (uncovered) and deck stair"),
    ("poly", DGRAY, WHITE, None, "Bulkhead ('size may vary' per AFAB)"),
    ("poly", GRAY, WHITE, "[4 3] 0", "Existing dwelling #199 to be removed"),
    ("line", ORANGE, None, "[7 4] 0", "Setback envelope per ECP (20' front/15' sides/23.2' rear)"),
    ("poly", GRAY, DRIVE_FILL, None, "Proposed driveway / apron (conceptual)"),
    ("line", RED, None, None, "Distance from proposed structure to lot line (ft)"),
    ("tree", RED, None, None, "Existing tree within 3' of footprint or drive"),
]

# ------------------------------------------------------------------ house / site elements
def driveway_polygon(mirror, theta, tx, ty, proj):
    u0 = G.GARAGE_DOORS[0][0] - 1.0; u1 = G.GARAGE_DOORS[1][1] + 1.0
    seg = G.place(LineString([(u0, -proj), (u1, -proj)]), mirror, theta, tx, ty)
    (ax, ay), (bx, by) = list(seg.coords)
    dv = G.place(LineString([(0, 0), (0, -1)]), mirror, theta, 0, 0); (x0, y0), (x1, y1) = list(dv.coords); dx, dy = x1-x0, y1-y0
    return Polygon([(ax, ay), (bx, by), (bx + dx*(-by/dy), 0.0), (ax + dx*(-ay/dy), 0.0)])

def tree_conflicts(footprint, drive):
    zone = unary_union([footprint, drive]).buffer(3.0)
    return [t for t in G.TREES if zone.contains(Point(t[0], t[1]))]

def protected_trees():
    yard = G.LOT.difference(ENV)
    return [t for t in G.TREES if t[2] >= 6 and yard.contains(Point(t[0], t[1]))]

def mark_trees(page, trees):
    sh = page.new_shape()
    for x, y, dbh, kind in trees:
        c = pymupdf.Point(*P(x, y)); r = 7.2*1.3
        sh.draw_circle(c, r); sh.finish(color=RED, width=1.2)
        sh.draw_line(c + (-r*0.7, -r*0.7), c + (r*0.7, r*0.7)); sh.draw_line(c + (-r*0.7, r*0.7), c + (r*0.7, -r*0.7)); sh.finish(color=RED, width=1.2)
    sh.commit()

def draw_house(page, parts, enclosed, mirror, theta, tx, ty, garage_proj=G.PROJ, porch_proj=G.PROJ):
    sh = page.new_shape()
    draw_poly(sh, parts["deck"], color=TAN, fill=TAN_FILL, width=1.0, fill_opacity=0.55)
    draw_poly(sh, parts["stair"], color=TAN, fill=TAN_FILL, width=0.8, fill_opacity=0.55)
    draw_poly(sh, parts["bulkhead"], color=DGRAY, fill=WHITE, width=0.9, fill_opacity=0.8)
    if porch_proj > 0: draw_poly(sh, parts["porch"], color=BLUE, fill=WHITE, width=1.0, fill_opacity=0.75)
    draw_poly(sh, enclosed, color=BLUE, fill=BLUE_FILL, width=2.2, fill_opacity=0.45)
    sh.commit()
    if porch_proj > 0:
        sh = page.new_shape(); draw_hatch(sh, parts["porch"], spacing_ft=1.2, color=BLUE, width=0.45); sh.commit()
    sh = page.new_shape()
    for (u0, u1) in G.GARAGE_DOORS:
        seg = G.place(LineString([(u0, -garage_proj), (u1, -garage_proj)]), mirror, theta, tx, ty)
        (ax, ay), (bx, by) = list(seg.coords)
        sh.draw_line(pymupdf.Point(*P(ax, ay)), pymupdf.Point(*P(bx, by))); sh.finish(color=DGRAY, width=3.0)
    sh.commit()
    def lab(u, v, s, size=7, color=BLUE):
        pt = G.place(Point(u, v), mirror, theta, tx, ty); text(page, pt.x, pt.y, s, size=size, color=color, angle=theta, align="center")
    lab(20, 24.5, "PROPOSED 2-STORY DWELLING", 7.5)
    lab(20, 22, "40'-0\" x 45'-0\" MAIN BODY", 6.5)
    lab(20, 19.8, "(AFAB 'NEW SINGLE FAMILY RESIDENCE')", 5.5)
    if garage_proj > 2.5: lab(28, -garage_proj/2 - 0.4, "GARAGE BAY", 6)
    if porch_proj > 2.5: lab(8, -porch_proj/2 - 0.4, "PORCH", 6)
    lab(21.5, 45 + 7, "DECK 16' x 14'", 6, TAN)
    lab(8.5, 45 + 3.0, "BH", 5.5, DGRAY)

def dims_for(page, parts, enclosed_parts=("garage",)):
    sh = page.new_shape(); d = {}; done = []
    gar, por, main, deck, bh = parts["garage"], parts["porch"], parts["main"], parts["deck"], parts["bulkhead"]
    def front_dim(pt, off):
        # skip a second arrow on a corner shared by the garage bay and the porch (same projection)
        if any(math.dist(pt, q) < 0.1 for q in done): return Point(pt).distance(line_of("front"))
        done.append(pt); return dim_to_line(page, sh, pt, "front", off)
    d["gar_e"] = front_dim(corner(gar, "se"), (2.3, 0)); d["gar_w"] = front_dim(corner(gar, "sw"), (-2.3, 0))
    d["por_e"] = front_dim(corner(por, "se"), (2.3, 0)); d["por_w"] = front_dim(corner(por, "sw"), (-2.3, 0))
    d["w_f"] = dim_to_line(page, sh, corner(main, "sw"), "west", (0, 1.5)); d["w_r"] = dim_to_line(page, sh, corner(main, "nw"), "west", (0, 1.5))
    d["e_f"] = dim_to_line(page, sh, corner(main, "se"), "east", (0, 1.5)); d["e_r"] = dim_to_line(page, sh, corner(main, "ne"), "east", (0, 1.5))
    d["r_w"] = dim_to_line(page, sh, corner(main, "nw"), "rear_lower", (-2.5, 0)); d["r_e"] = dim_to_line(page, sh, corner(main, "ne"), "rear_lower", (2.5, 0))
    d["deck_w"] = dim_to_line(page, sh, corner(deck, "nw"), "rear_lower", (-2.5, 0)); d["deck_e"] = dim_to_line(page, sh, corner(deck, "ne"), "rear_lower", (2.5, 0))
    d["bh"] = dim_to_line(page, sh, corner(bh, "nw"), "rear_lower", (-2.5, 0))
    sh.commit(); return d

def fmt_ftin(x):
    ft = int(x); inch = round((x-ft)*12)
    if inch == 12: ft += 1; inch = 0
    return "%d'-%d\"" % (ft, inch)

ZONING_PARAS = [
    "**ZONING BASIS (Concord Zoning Bylaw - verify current text with the Building Commissioner)",
    "Residence C, Table III: min. lot 10,000 sf (lot is 7,511 sf), min. frontage 80' (lot has 73.4'), front yard 20', side yards 15', rear yard = lesser of 30' or 25% of lot depth (= 23.2' on the ECP), max. height 35' (mean of plate and ridge, Sec. 6.2.11).",
    "Sec. 6.2.6 / 6.2.8: front and rear yards are measured to the nearest point of ANY structure; only uncovered steps and ramps, walls and fences may cross the line. The covered porch, deck and bulkhead therefore all count against the setbacks.",
]
PERMIT_PARAS = [
    "**PERMITTING FLAGS (from bylaw research - confirm with Town staff)",
    "1. Pre-existing nonconforming lot: a replacement house over 150% of the existing gross floor area needs a ZBA special permit (Sec. 7.1.5 / 11.6); the 3,387 sf plan is well over that unless the existing house is > 2,258 sf. Precedents show the ZBA routinely grants these when setbacks are met - encroachments (above) weaken the case.",
    "2. Residential floor-area cap (Table III / Sec. 6.2.13, sq ft per acre): obtain the Residence C figure - on a 0.17-acre lot it may limit house size before setbacks do.",
    "3. Demolition Review: #199 is c.1908 and appears on the West Concord historic resources survey list - Historical Commission review, possible 12-month delay.",
    "4. Tree Preservation Bylaw: trees >= 6\" DBH with trunks in the setback strips are protected; removal needs a Tree Permit with replanting or $375/inch mitigation.",
    "5. CPW driveway permit for any new/altered curb cut; Engineering sign-off on drainage.",
]

# ------------------------------------------------------------------ build
def make():
    src = pymupdf.open(ECP); doc = pymupdf.open(); theta = G.LOT_TILT; set_house_axis(theta)
    T = feasible_T(G.MAIN, False, theta)
    tx, ty = pick_translation(T, False, theta, G.MAIN, "rear")
    txf, tyf = pick_translation(T, False, theta, G.MAIN, "front"); slide = math.hypot(txf-tx, tyf-ty)
    prot = protected_trees()
    results = {"theta": theta, "slide": slide, "protected_trees": prot}

    for sheet_no, (mirror, title, sub) in enumerate([
        (True,  "OPTION 1 - PLAN MIRRORED (GARAGE ON WEST, DRIVEWAY SIDE); HOUSE PARALLEL WITH SIDE LOT LINES",
                "40'x45' main body rotated 6.3 deg clockwise from the sheet vertical (mean bearing of the side lot lines), centred between the 15' side setback lines with its rear wall on the rear setback line. Recommended orientation and side - see notes."),
        (False, "OPTION 2 - PLAN AS DRAWN (GARAGE ON EAST); HOUSE PARALLEL WITH SIDE LOT LINES",
                "Same placement of the 40'x45' main body as Option 1, plan not mirrored. Shown for comparison of driveway location, trees and the front-yard encroachment of the garage bay."),
    ], start=1):
        page = sheet_base(doc, src)
        parts = G.placed_parts(mirror, theta, tx, ty); enclosed = G.place(G.ENCLOSED, mirror, theta, tx, ty)
        rep = part_report(parts); drive = driveway_polygon(mirror, theta, tx, ty, G.PROJ)
        fade_existing(page); draw_envelope(page)
        sh = page.new_shape(); draw_poly(sh, drive, color=GRAY, fill=DRIVE_FILL, width=0.8, fill_opacity=0.5); sh.commit()
        draw_house(page, parts, enclosed, mirror, theta, tx, ty)
        c = drive.centroid; text(page, c.x, c.y, "PROPOSED DRIVE", size=6, color=DGRAY, align="center")
        footprint = unary_union([parts[k] for k in ("main", "garage", "porch", "deck", "bulkhead")])
        conf = tree_conflicts(footprint, drive); mark_trees(page, conf)
        d = dims_for(page, parts)
        banner(page, title, sub); legend(page, STD_LEGEND)
        gside, pside = ("WEST", "EAST") if mirror else ("EAST", "WEST")
        big = min(Point(G.TREES[0][0], G.TREES[0][1]).distance(parts[k]) for k in ("main", "garage", "porch", "deck"))
        notes = [
          "**PROPOSED DWELLING",
          "AFAB Enterprises 'New Single Family Residence': 2-story, 40'-0\" x 45'-0\" main body; 24'-0\" wide garage bay and 16'-0\" wide covered porch both project 7'-6\" toward the street (52'-6\" overall); 16' x 14' rear deck; 5'-4\" x 6'-2\" bulkhead. 1st fl 1,400 sf + 2nd fl 1,987 sf = 3,387 sf (AFAB sheet 4). Plan %s." % ("MIRRORED so the garage is on the %s (existing driveway/curb-cut side)" % gside if mirror else "as drawn, garage on the %s" % gside),
          "",
          "**PLACEMENT",
          "House axis parallel with the mean bearing of the side lot lines: 6.3 deg clockwise from the sheet vertical (west line S 4-43-20 E leans 6.7 deg, east line S 5-29-50 E leans 5.9 deg). Main body centred between the side setback lines (%.1f' / %.1f' to the lot lines) with its rear wall on the rear setback line; main-body front wall %.1f' from Central Street at the %s corner." % (rep["main"]["west"], rep["main"]["east"], rep["main"]["front"], "east"),
          "The main body can slide only %.1f' toward the street before it reaches the 20' front line; each foot of slide reduces the rear-yard encroachment of the deck/bulkhead by a foot and increases the front-yard encroachment of the garage/porch by a foot." % slide,
          "",
          "**SETBACK CHECK  (front 20' / sides 15' / rear 23.2')",
          "Main body 40'x45': %.1f' street, %.1f' W, %.1f' E, %.1f' rear  -  COMPLIES (%.1f' spare each side)." % (rep["main"]["front"], rep["main"]["west"], rep["main"]["east"], rep["main"]["rear_lower"], min(rep["main"]["west"], rep["main"]["east"])-15),
          "Garage bay (%s): %.1f' to %.1f' from street  -  %.1f' INSIDE the front setback." % (gside, min(d["gar_e"], d["gar_w"]), max(d["gar_e"], d["gar_w"]), 20-min(d["gar_e"], d["gar_w"])),
          "Covered porch (%s): %.1f' to %.1f' from street  -  %.1f' INSIDE the front setback." % (pside, min(d["por_e"], d["por_w"]), max(d["por_e"], d["por_w"]), 20-min(d["por_e"], d["por_w"])),
          "Rear deck: %.1f' to %.1f' from rear lot line  -  %.1f' INSIDE the rear setback." % (min(d["deck_w"], d["deck_e"]), max(d["deck_w"], d["deck_e"]), 23.2-min(d["deck_w"], d["deck_e"])),
          "Bulkhead: %.1f' from rear lot line  -  %.1f' INSIDE the rear setback." % (d["bh"], 23.2-d["bh"]),
          "=> The enclosed house as drawn does NOT fit the envelope in any orientation: a 40'-wide rectangle parallel with the lot can be at most ~46.3' deep here, vs. 52'-6\" for this plan. Sheet 4 shows the largest front projection that fits (3'-0\" with the garage on the west, 1'-3\" with it on the east); the memo lists the relief/redesign options.",
          "",
          "**SITE, TREES, UTILITIES",
          "Trees within 3' of the footprint or drive (marked X): %s." % (", ".join("%d\"%s" % (t[2], t[3]) for t in conf) if conf else "none"),
          "Protected trees (>= 6\" DBH in the setback strips, Tree Preservation Bylaw): %s." % ", ".join("%d\"%s" % (t[2], t[3]) for t in prot),
          "50\" deciduous tree on the east line is ~%.0f' from the nearest proposed structure; keep excavation and the drive out of its root zone (arborist review)." % big,
          "Existing water service (centre of lot), overhead electric from the poles at the SW corner, the concrete-curb retaining wall and the bituminous pad at the rear are all affected - re-route/remove as required. %s" % ("The existing west-side driveway/curb cut can be closed and restored or kept as a parking pad; the new apron needs a CPW driveway permit." if mirror else "A new east-side curb cut is needed; the existing west driveway would be abandoned."),
          "Grade falls ~5' from Central St (el. 155) to the rear line (el. 150-151), so the deck and bulkhead will stand well above grade; AFAB's 'bulkhead size may vary' note applies.",
          "",
        ] + ZONING_PARAS + [""] + PERMIT_PARAS + ["", "**Red dimensions are scaled from the ECP linework (+/- 0.3'); verify by field layout before permitting."]
        textbox(page, (972, 700, 1240, 1228), notes, title="NOTES - OPTION %d" % sheet_no, title_size=8.5)
        results[sheet_no] = dict(mirror=mirror, rep=rep, conf=conf, d=d)

    # ---------------- Sheet 3: orientation study ----------------
    page = sheet_base(doc, src); fade_existing(page); draw_envelope(page)
    par = G.place(G.MAIN, False, theta, tx, ty)
    a = 21.55; sq = Polygon([(a, 20), (a+40, 20), (a+40, 65), (a, 65)])
    sh = page.new_shape()
    draw_poly(sh, sq, color=RED, fill=PINK, width=1.8, dashes="[6 3] 0", fill_opacity=0.35)
    draw_poly(sh, par, color=BLUE, fill=BLUE_FILL, width=2.2, fill_opacity=0.35); sh.commit()
    sh = page.new_shape(); set_house_axis(0.0)
    for w in ("nw", "sw"): dim_to_line(page, sh, corner(sq, w), "west", (0, 1.5))
    for w in ("ne", "se"): dim_to_line(page, sh, corner(sq, w), "east", (0, 1.5))
    sh.commit(); sh = page.new_shape(); set_house_axis(theta)
    for w in ("nw", "sw"): dim_to_line(page, sh, corner(par, w), "west", (0, -1.7), color=BLUE)
    for w in ("ne", "se"): dim_to_line(page, sh, corner(par, w), "east", (0, -1.7), color=BLUE)
    sh.commit()
    text(page, 41.6, 47.5, "MAIN BODY 40' x 45' - PARALLEL WITH SIDE LOT LINES", 7, BLUE, angle=theta, align="center")
    text(page, 41.6, 38.5, "MAIN BODY 40' x 45' - SQUARE TO STREET", 7, RED, align="center")
    banner(page, "SHEET 3 - ORIENTATION STUDY: PARALLEL WITH THE LOT vs. SQUARE TO CENTRAL STREET",
           "Only the 40' x 45' main body is shown. Blue = rotated 6.3 deg to match the side lot lines (fits). Red dashed = square to the street at its best, balanced position (does not fit). Red = square-to-street distances, blue = parallel distances.")
    legend(page, [("poly", BLUE, BLUE_FILL, None, "Main body parallel with side lot lines - fits, ~1.0' spare/side"),
                  ("poly", RED, PINK, "[6 3] 0", "Main body square to Central St - ~1.1' over each side line"),
                  ("line", ORANGE, None, "[7 4] 0", "Setback envelope per ECP"),
                  ("poly", GRAY, WHITE, "[4 3] 0", "Existing dwelling to be removed")])
    notes3 = [
      "**WHY THE HOUSE SHOULD BE PARALLEL WITH THE SIDE LOT LINES",
      "The side lot lines are not square to Central Street: on the ECP they lean 6.7 deg (west) and 5.9 deg (east) toward the east as they run away from the street, while the street line runs straight across the sheet. The buildable envelope between the two 15' side setback lines is therefore a slanted strip: 42.9' wide along the front setback line and 42.1' along the rear one, i.e. about 42.4' measured square to the side lines.",
      "",
      "A 40'-wide house set SQUARE TO THE STREET needs 40' + 45' x tan(6.3 deg) = 45.0' of that strip over its 45' depth, so it cannot fit: at best it is ~1.1' over the west setback line at its rear-west corner and ~1.1' over the east line at its front-east corner (red). Add the 7'-6\" garage/porch projection and the shortfall grows to ~1.5' per side, before any eave overhang.",
      "",
      "The same house ROTATED 6.3 deg (parallel with the mean bearing of the side lines) fits the strip with ~1.0' to spare on each side (blue). It is the only orientation in which the 40' width clears both 15' side setbacks, so 'parallel with the lot' is the right call. (The existing house is square to the street, but it is only 27.5' wide.) Rotating exactly parallel also keeps the house visually consistent with the side fences/walls; the ~6 deg skew to the street is barely perceptible from the road.",
      "",
      "**WHAT PARALLEL COSTS: FRONT-TO-REAR DEPTH",
      "Because the front and rear setback lines are not square to the rotated house, the rotated rectangle loses depth at opposite corners: across the 40' width the front line sits 4.4' further 'back' at the east end than at the west end, and the rear line 3.1' further 'forward' at the west end than at the east. Net effect: a rotated 40'-wide rectangle can be at most ~46.3' deep on this lot. The 45' main body fits with 1.3' of slide; the 7'-6\" garage/porch projection (52'-6\" overall) cannot be held inside the envelope in any orientation.",
      "",
      "Rotating slightly less than parallel (about 5.5 deg) trades side clearance for ~0.5' more depth - not enough to matter. Exactly parallel is recommended.",
      "",
      "**EAVES: the spare side clearance is only ~1.0' per side, so a typical 12\"-16\" roof overhang lands on or just over the 15' line. Confirm with the Building Commissioner whether eaves count (Sec. 6.2.7 also contains a 3' side-yard exception for low, <= 15'-high portions of the principal structure in Res. C - get the exact text).",
    ]
    textbox(page, (972, 700, 1240, 1228), notes3, title="NOTES - ORIENTATION STUDY", title_size=8.5)

    # ---------------- Sheet 4: modified footprint that fits ----------------
    page = sheet_base(doc, src); mirror = True
    pmax = max_projection(mirror, theta); pmax_e = max_projection(False, theta); p_use = math.floor(pmax*2)/2.0
    garage4 = Polygon([(16, -p_use), (40, -p_use), (40, 0), (16, 0)])
    # max porch (roof) projection on the other side, with the garage fixed at p_use
    lo, hi = 0.0, 7.5
    for _ in range(30):
        mid = 0.5*(lo+hi); tst = unary_union([G.MAIN, garage4, Polygon([(0, -mid), (16, -mid), (16, 0), (0, 0)])])
        if feasible_T(tst, mirror, theta).is_empty: hi = mid
        else: lo = mid
    porch_max = lo; pp_use = math.floor(porch_max*4)/4.0
    porch4 = Polygon([(0, -pp_use), (16, -pp_use), (16, 0), (0, 0)])
    enclosed4_local = unary_union([G.MAIN, garage4, porch4]); T4 = feasible_T(enclosed4_local, mirror, theta)
    tx4, ty4 = pick_translation(T4, mirror, theta, enclosed4_local, "rear")
    parts4 = G.placed_parts(mirror, theta, tx4, ty4)
    parts4["garage"] = G.place(garage4, mirror, theta, tx4, ty4); parts4["porch"] = G.place(porch4, mirror, theta, tx4, ty4)
    enclosed4 = G.place(unary_union([G.MAIN, garage4]), mirror, theta, tx4, ty4); rep4 = part_report(parts4)
    drive4 = driveway_polygon(mirror, theta, tx4, ty4, p_use)
    fade_existing(page); draw_envelope(page)
    sh = page.new_shape(); draw_poly(sh, drive4, color=GRAY, fill=DRIVE_FILL, width=0.8, fill_opacity=0.5); sh.commit()
    ghost = G.place(unary_union([G.GARAGE_PROJ, G.PORCH]), mirror, theta, tx4, ty4)
    sh = page.new_shape(); draw_poly(sh, ghost, color=RED, width=0.9, dashes="[3 3] 0"); sh.commit()
    draw_house(page, parts4, enclosed4, mirror, theta, tx4, ty4, garage_proj=p_use, porch_proj=pp_use)
    c = drive4.centroid; text(page, c.x, c.y - 1, "PROPOSED DRIVE", size=6, color=DGRAY, align="center")
    footprint4 = unary_union([parts4[k] for k in ("main", "garage", "porch", "deck", "bulkhead")])
    conf4 = tree_conflicts(footprint4, drive4); mark_trees(page, conf4)
    d4 = dims_for(page, parts4)
    gar_clear = 23.31 - (G.PROJ - p_use)
    banner(page, "OPTION 3 - AS OPTION 1 BUT WITH THE FRONT PROJECTIONS CUT BACK (GARAGE %s, PORCH ROOF %s): THE ENCLOSED HOUSE FITS THE SETBACK ENVELOPE" % (fmt_ftin(p_use), fmt_ftin(pp_use)),
           "Garage bay projects %s and the porch roof %s instead of 7'-6\" (red dashed = original 7'-6\" line). Main body, garage and porch roof comply; the rear deck and bulkhead still sit inside the rear setback - see notes." % (fmt_ftin(p_use), fmt_ftin(pp_use)))
    legend(page, STD_LEGEND + [("line", RED, None, "[3 3] 0", "Original 7'-6\" garage/porch projection (reference)")])
    notes4 = [
      "**WHAT CHANGED vs. OPTION 1",
      "The largest front projection that keeps the enclosed house inside the envelope, with the plan mirrored (garage on the west, where the skewed front setback line leaves the most room), is %.2f'; it is drawn here as %s. As drawn the projection is 7'-6\", i.e. %.1f' too much. With the garage on the EAST (plan as drawn) the limit is only %.2f'." % (pmax, fmt_ftin(p_use), G.PROJ - p_use, pmax_e),
      "",
      "**DESIGN IMPLICATIONS FOR AFAB",
      "- Garage bay clear depth drops from 23'-4\" to about %s. To keep a 20'+ bay, move the garage rear wall ~%s into the mudroom/bench zone, or shorten the main body by the same amount." % (fmt_ftin(gar_clear), fmt_ftin(max(0.0, 20.0 - gar_clear))),
      "- The porch side (east) has the least front-yard room: with the garage at %s the porch ROOF can project only %.2f' (drawn as %s), i.e. an entry canopy over the door. Concord measures the front yard to any structure except uncovered steps and ramps (Sec. 6.2.6), so the 7'-6\" covered porch cannot be kept without relief; an uncovered stoop and steps may still project." % (fmt_ftin(p_use), porch_max, fmt_ftin(pp_use)),
      "- Alternative with the same effect: keep the 7'-6\" front projection and shorten the main body from 45' to ~%s, or drop the projection and lengthen nothing (main body alone has 1.3' of slide)." % fmt_ftin(45.0 - (G.PROJ - p_use)),
      "",
      "**SETBACK CHECK  (front 20' / sides 15' / rear 23.2')",
      "Main body 40'x45': %.1f' street, %.1f' W, %.1f' E, %.1f' rear  -  COMPLIES." % (rep4["main"]["front"], rep4["main"]["west"], rep4["main"]["east"], rep4["main"]["rear_lower"]),
      "Garage bay (W): %.1f' to %.1f' from street  -  COMPLIES." % (min(d4["gar_e"], d4["gar_w"]), max(d4["gar_e"], d4["gar_w"])),
      "Porch canopy (E): %.1f' from street at its SE corner  -  COMPLIES." % min(d4["por_e"], d4["por_w"]),
      "Rear deck 16'x14': %.1f' to %.1f' from rear lot line  -  %.1f' INSIDE the rear setback." % (min(d4["deck_w"], d4["deck_e"]), max(d4["deck_w"], d4["deck_e"]), 23.2 - min(d4["deck_w"], d4["deck_e"])),
      "Bulkhead: %.1f' from rear lot line  -  %.1f' INSIDE the rear setback." % (d4["bh"], 23.2 - d4["bh"]),
      "",
      "**REAR DECK / BULKHEAD",
      "Because the main body's rear wall sits ON the rear setback line, any attached deck or bulkhead is inside the rear setback, and Sec. 6.2.8 measures the rear yard to any structure attached to the dwelling (only uncovered steps/ramps are exempt). Options: (a) replace the deck with an at-grade patio/terrace reached by uncovered steps; (b) shrink the deck to a landing + steps; (c) ask the ZBA for relief for the deck only; (d) drop the bulkhead: grade at the rear is ~4-5' below the street, so a walk-out basement door in the rear foundation wall (no projection) can replace it, or use an interior basement stair. A 14'-deep first-floor deck here would stand ~5-6' above grade at its rail - a walk-out lower level with a patio may suit the site better anyway.",
      "",
      "Trees within 3' of the footprint or drive (marked X): %s." % (", ".join("%d\"%s" % (t[2], t[3]) for t in conf4) if conf4 else "none"),
      "",
    ] + ZONING_PARAS
    textbox(page, (972, 700, 1240, 1228), notes4, title="NOTES - OPTION 3", title_size=8.5)
    results[4] = dict(pmax=pmax, pmax_e=pmax_e, p_use=p_use, porch_max=porch_max, pp_use=pp_use, rep=rep4, d=d4, conf=conf4)

    doc.save(OUT_PDF, garbage=3, deflate=True)
    for i, pg in enumerate(doc, start=1):
        pg.get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6)).save(os.path.join(OUT_DIR, "sheet%d.png" % i))
    print("wrote", OUT_PDF); return results

if __name__ == "__main__":
    import json
    res = make()
    def clean(o):
        if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [clean(v) for v in o]
        if isinstance(o, float): return round(o, 2)
        return o
    json.dump(clean(res), open(os.path.join(OUT_DIR, "results.json"), "w"), indent=1)
    print(json.dumps(clean(res), indent=1))
