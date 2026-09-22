"""Geometry model for placing the AFAB 'New Single Family Residence' (Carter.pdf)
on the 199 Central Street, Concord MA lot (PLACES Associates ECP, plan 5827-ECP).

Coordinate frame ("page-feet"): the ECP sheet frame, converted to feet.
  x = east-ish along Central Street (page right), y = north-ish (page up).
  Origin = SW lot corner (drill hole found 0.51' into Central St).
  True north is 11.41 deg clockwise from +y (street bearing S 78-35-22 W).
Scale of the ECP: 1 in = 10 ft  ->  7.2 PDF points per foot.
"""
import math
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import rotate, translate, scale
from shapely.ops import unary_union

PT_PER_FT = 7.2
PAGE_ORIGIN_PT = (353.9, 1035.1)   # SW lot corner in ECP PDF points (y down)

def pt2ft(x, y):
    return ((x - PAGE_ORIGIN_PT[0]) / PT_PER_FT, (PAGE_ORIGIN_PT[1] - y) / PT_PER_FT)

def ft2pt(x, y):
    return (PAGE_ORIGIN_PT[0] + x * PT_PER_FT, PAGE_ORIGIN_PT[1] - y * PT_PER_FT)

# ---- Lot corners (from ECP vector data; lengths check against the deed/measured calls) ----
SW   = pt2ft(353.9, 1035.1)   # drill hole, Central St
SE   = pt2ft(882.4, 1035.1)   # stone bound, Central St
NE   = pt2ft(974.9, 142.6)    # stone bound
PIN  = pt2ft(798.1, 143.0)    # iron pin (NW corner of the rear notch)
PIPE = pt2ft(793.8, 368.0)    # iron pipe (inside corner of the jog)
NW   = pt2ft(433.4, 356.0)    # drill hole (NW corner)
LOT = Polygon([SW, SE, NE, PIN, PIPE, NW])

# Lot lines as (name, p, q, required setback ft, type)
FRONT_SB, SIDE_SB = 20.0, 15.0
REAR_SB_LABEL = 23.2          # value printed on the ECP
REAR_SB = 23.5                # offset that reproduces the dashed line actually drawn on the ECP (0.3' tighter than the label)
LOT_LINES = [
    ("front", SW, SE, FRONT_SB),
    ("east",  SE, NE, SIDE_SB),
    ("rear_upper", NE, PIN, REAR_SB),
    ("jog",   PIN, PIPE, SIDE_SB),
    ("rear_lower", PIPE, NW, REAR_SB),
    ("west",  NW, SW, SIDE_SB),
]

def envelope(front=FRONT_SB, side=SIDE_SB, rear=REAR_SB):
    """Buildable envelope = lot minus every lot line buffered by its required setback.
    (Correct for the non-convex rear notch: a point must be >= d from each lot line.)"""
    sb = {"front": front, "east": side, "west": side, "jog": side, "rear_upper": rear, "rear_lower": rear}
    buf = unary_union([LineString([p, q]).buffer(sb[name], quad_segs=32) for name, p, q, _ in LOT_LINES])
    env = LOT.difference(buf)
    if env.geom_type != "Polygon":
        env = max(env.geoms, key=lambda g: g.area)
    return env

ENVELOPE = envelope()

def _shift_inward(p, q, d):
    dx, dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L
    return (p[0]+nx*d, p[1]+ny*d), (q[0]+nx*d, q[1]+ny*d)

# Reference lines for reported distances. The dashed rear setback line on the ECP is labelled 23.2' but sits
# 23.5' from the centre of the heavy lot-line stroke as extracted, so the rear reference is shifted 0.3' inward
# to make distances consistent with the surveyor's label (all other lines match the extracted linework exactly).
DIM_LINES = {name: (p, q) for name, p, q, _ in LOT_LINES}
DIM_LINES["rear_lower"] = _shift_inward(PIPE, NW, REAR_SB - REAR_SB_LABEL)
DIM_LINES["rear_upper"] = _shift_inward(NE, PIN, REAR_SB - REAR_SB_LABEL)

def bearing_deg(p, q):
    """Page-frame angle (deg CCW from +x) of p->q."""
    return math.degrees(math.atan2(q[1]-p[1], q[0]-p[0]))

WEST_TILT = bearing_deg(SW, NW) - 90.0   # deg, negative = leans east going north (clockwise from +y)
EAST_TILT = bearing_deg(SE, NE) - 90.0
LOT_TILT = 0.5*(WEST_TILT + EAST_TILT)   # ~ -6.3 deg

# ---- Existing house #199 (ECP vectors, width 1.44 pt) ----
EXISTING_MAIN = Polygon([pt2ft(*p) for p in [(588.0,858.5),(588.0,660.5),(708.1,660.5),(708.1,624.7),(800.9,624.7),
                        (800.9,660.5),(778.8,660.5),(778.7,813.4),(736.7,813.4),(736.7,858.6),(730.2,858.6),
                        (730.2,909.0),(594.7,908.9),(594.7,858.5)]])
EXISTING_BH = Polygon([pt2ft(*p) for p in [(628.3,621.6),(676.1,621.7),(676.1,660.5),(628.3,660.5)]])

# ---- Trees (from ECP): (x, y, dbh inches, type) ----
TREES = [(pt2ft(915,651)+(50,"D")), (pt2ft(773,998)+(24,"E")), (pt2ft(635,1003)+(18,"E")), (pt2ft(575,927)+(18,"E")),
         (pt2ft(783,861)+(6,"E")), (pt2ft(535,499)+(18,"E")), (pt2ft(890,472)+(24,"E")), (pt2ft(511,619)+(10,"D")),
         (pt2ft(480,718)+(8,"D")), (pt2ft(750,401)+(18,"E")), (pt2ft(710,404)+(12,"E"))]

# ---- New house footprint, local frame: u = across (0..40, garage side at +u as drawn), v = front->rear.
#      v = 0 at the MAIN BODY FRONT WALL (living/dining), v = 45 at the rear wall; garage/porch project to v = -7.5.
W = 40.0; D_MAIN = 45.0; PROJ = 7.5
MAIN   = Polygon([(0,0),(W,0),(W,D_MAIN),(0,D_MAIN)])
GARAGE_PROJ = Polygon([(16,-PROJ),(40,-PROJ),(40,0),(16,0)])       # enclosed, 24' wide
PORCH  = Polygon([(0,-PROJ),(16,-PROJ),(16,0),(0,0)])              # covered, open porch (roof extent)
PORCH_FLOOR = Polygon([(0,-6.0),(16,-6.0),(16,0),(0,0)])
DECK   = Polygon([(13.5,D_MAIN),(29.5,D_MAIN),(29.5,D_MAIN+14.0),(13.5,D_MAIN+14.0)])   # 16' x 14' (13'-6" to beam + overhang)
DECK_STAIR = Polygon([(29.5,D_MAIN),(32.5,D_MAIN),(32.5,D_MAIN+7.0),(29.5,D_MAIN+7.0)])
BULKHEAD = Polygon([(5.833,D_MAIN),(11.167,D_MAIN),(11.167,D_MAIN+6.167),(5.833,D_MAIN+6.167)])
GARAGE_DOORS = [(18.0,27.0),(28.0,37.0)]   # u-ranges of the two 9' doors on the garage front (v=-7.5)
FRONT_DOOR_U = 14.6                        # approx centre of front door on porch
ENCLOSED = unary_union([MAIN, GARAGE_PROJ])
ROOFED = unary_union([MAIN, GARAGE_PROJ, PORCH])
ALL_PARTS = {"main": MAIN, "garage": GARAGE_PROJ, "porch": PORCH, "deck": DECK, "stair": DECK_STAIR, "bulkhead": BULKHEAD}

def place(geom, mirror, theta_deg, tx, ty):
    """Mirror (u -> W-u) optionally, rotate by theta (deg, CCW positive) about local origin, then translate.
    Local frame before placement: +u = east, +v = north (house faces south/street)."""
    g = geom
    if mirror:
        g = scale(g, xfact=-1, yfact=1, origin=(W/2.0, 0))
    g = rotate(g, theta_deg, origin=(0,0), use_radians=False)
    return translate(g, tx, ty)

def placed_parts(mirror, theta, tx, ty):
    return {k: place(v, mirror, theta, tx, ty) for k, v in ALL_PARTS.items()}

def signed_clearance(poly, env):
    """Min distance from poly to envelope boundary; negative = poly extends outside by that much."""
    outside = poly.difference(env)
    if outside.is_empty or outside.area < 1e-6:
        return poly.exterior.distance(env.exterior) if env.contains(poly) else 0.0
    # how far outside: max distance of outside part from the envelope
    return -max(Point(c).distance(env) for c in outside.exterior.coords) if outside.geom_type=="Polygon" else \
           -max(Point(c).distance(env) for g in outside.geoms for c in g.exterior.coords)

def dist_to_line(pt, name):
    for n, p, q, _ in LOT_LINES:
        if n == name:
            return Point(pt).distance(LineString([p, q]))
    raise KeyError(name)

if __name__ == "__main__":
    print("Lot area (sf):", round(LOT.area, 1))
    print("West tilt %.2f  East tilt %.2f  -> house rotation %.2f deg (clockwise from page-up)" % (WEST_TILT, EAST_TILT, LOT_TILT))
    env = ENVELOPE
    print("Envelope area:", round(env.area,1))
    for c in env.exterior.coords: print("  env corner %.2f, %.2f" % c)
    cs = list(env.exterior.coords)
    for i in range(len(cs)-1):
        print("  edge %d len %.2f" % (i, math.dist(cs[i], cs[i+1])))
