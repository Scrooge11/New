"""Fit analysis: where can the AFAB house go on the 199 Central St lot?
Uses the setback envelope exactly as drawn on the PLACES Associates ECP."""
import math
from shapely.geometry import Polygon, Point, LineString
from shapely.affinity import translate
from shapely.ops import unary_union
import geometry as G

ENV = G.ENVELOPE.convex_hull   # straight rear line across the jog, as drawn on the ECP (removes the tiny concave arc at the iron pipe)

def line_of(name):
    p, q = G.DIM_LINES[name]
    return LineString([p, q])

def feasible_T(body_local, mirror, theta):
    """Set of translations t such that place(body, mirror, theta, t) lies inside ENV (ENV convex)."""
    b = G.place(body_local, mirror, theta, 0, 0)
    T = ENV
    for (vx, vy) in b.exterior.coords[:-1]:
        T = T.intersection(translate(ENV, -vx, -vy))
        if T.is_empty: return T
    return T

def part_report(parts):
    out = {}
    for k, poly in parts.items():
        d = {n: poly.distance(line_of(n)) for n in ("front", "west", "east", "rear_lower")}
        outside = poly.difference(ENV)
        enc = 0.0
        if not outside.is_empty and outside.area > 1e-4:
            geoms = [outside] if outside.geom_type == "Polygon" else list(outside.geoms)
            enc = max(Point(c).distance(ENV) for g in geoms for c in g.exterior.coords)
        out[k] = dict(d, enc=enc, out_area=outside.area if not outside.is_empty else 0.0)
    return out

def fmt(rep, keys=("main","garage","porch","deck","bulkhead")):
    lines = ["    part      front   west   east   rear  | outside envelope by"]
    for k in keys:
        r = rep[k]
        lines.append("    %-8s %6.1f %6.1f %6.1f %6.1f  | %5.1f ft (%.0f sf)" % (k, r["front"], r["west"], r["east"], r["rear_lower"], r["enc"], r["out_area"]))
    return "\n".join(lines)

def pick_translation(T, mirror, theta, body_local, mode):
    """Sample T finely; choose t by mode:
       'rear'   : side-balanced, then max distance from front line (pushed to the rear line)
       'front'  : side-balanced, then pushed to the front line
       'balance': equalise garage-front encroachment and main-body rear encroachment is N/A here (main inside) -> same as 'rear'
    """
    minx, miny, maxx, maxy = T.bounds
    best = None
    n = 80
    for i in range(n+1):
        for j in range(n+1):
            tx = minx + (maxx-minx)*i/n; ty = miny + (maxy-miny)*j/n
            if not T.covers(Point(tx, ty)): continue
            p = G.place(body_local, mirror, theta, tx, ty)
            dw, de = p.distance(line_of("west")), p.distance(line_of("east"))
            df = p.distance(line_of("front"))
            bal = abs(dw-de)
            key = (bal > 0.08, -df if mode=="rear" else df)   # prefer balanced (within 1 inch), then slide
            if best is None or key < best[0]:
                best = (key, tx, ty)
    return best[1], best[2]

def option(label, mirror, theta, body="main"):
    print("="*90); print(label)
    body_local = G.MAIN if body=="main" else G.ENCLOSED
    T = feasible_T(body_local, mirror, theta)
    if T.is_empty:
        print("   -> the %s footprint does NOT fit inside the setback envelope at this rotation" % body); return None
    minx, miny, maxx, maxy = T.bounds
    print("   feasible translation set: %.2f ft (E-W) x %.2f ft (N-S), area %.2f sf" % (maxx-minx, maxy-miny, T.area))
    res = {}
    for mode in ("rear", "front"):
        tx, ty = pick_translation(T, mirror, theta, body_local, mode)
        parts = G.placed_parts(mirror, theta, tx, ty)
        rep = part_report(parts)
        print("   main body pushed to %s setback line  (tx=%.3f, ty=%.3f):" % (mode.upper(), tx, ty))
        print(fmt(rep))
        res[mode] = (tx, ty, rep)
    return res

def max_projection(mirror, theta):
    """Largest front projection p (ft) of the 24'-wide garage bay (as drawn at local u=16..40; it lands on the
    EAST when mirror=False and on the WEST when mirror=True) so that main+garage fits inside ENV."""
    lo, hi = 0.0, 7.5
    for _ in range(30):
        mid = 0.5*(lo+hi)
        garage = Polygon([(16,-mid),(40,-mid),(40,0),(16,0)])
        enclosed = unary_union([G.MAIN, garage])
        T = feasible_T(enclosed, mirror, theta)
        if T.is_empty: hi = mid
        else: lo = mid
    return lo

def max_width_with_eaves(theta, e=G.EAVE_SIDE, depth=G.D_MAIN):
    """Largest wall-to-wall width W such that a W+2e wide, `depth` deep rectangle fits inside ENV."""
    lo, hi = 30.0, 45.0
    for _ in range(30):
        mid = 0.5*(lo+hi)
        rect = Polygon([(-e, 0), (mid+e, 0), (mid+e, depth), (-e, depth)])
        if feasible_T(rect, False, theta).is_empty: hi = mid
        else: lo = mid
    return lo

def max_eave_for_width(theta, width=G.W, depth=G.D_MAIN):
    """Largest side allowance e such that the 40'-wide main body plus e on each side fits inside ENV."""
    lo, hi = 0.0, 3.0
    for _ in range(30):
        mid = 0.5*(lo+hi)
        rect = Polygon([(-mid, 0), (width+mid, 0), (width+mid, depth), (-mid, depth)])
        if feasible_T(rect, False, theta).is_empty: hi = mid
        else: lo = mid
    return lo

def eave_report(theta):
    print("="*90)
    print("SIDE ROOF OVERHANG CHECK: 12\" eave + 3\" margin = %.2f' each side (owner's rule)" % G.EAVE_SIDE)
    T = feasible_T(G.MAIN_EAVE, False, theta)
    print("  42'-6\" eave-to-eave rectangle fits inside the 15' side setback lines:", "YES" if not T.is_empty else "NO")
    print("  max wall-to-wall width with %.2f' each side, parallel to lot: %.2f ft (%s)" % (G.EAVE_SIDE, max_width_with_eaves(theta), "plan is 40'-0\""))
    print("  max side allowance for a 40'-0\" wide body, parallel to lot: %.2f ft = %.1f in" % (max_eave_for_width(theta), 12*max_eave_for_width(theta)))
    for th in (-7.0, -6.5, -6.3, -6.0, -5.5, -5.0):
        print("    theta %.1f: max width w/ eaves %.2f ft, max eave for 40' body %.1f in" % (th, max_width_with_eaves(th), 12*max_eave_for_width(th)))

if __name__ == "__main__":
    theta = G.LOT_TILT
    print("Rotation for 'parallel with the lot' (mean of side lines): %.2f deg clockwise from the ECP sheet's vertical" % (-theta))
    print("  (west line leans %.2f deg, east line %.2f deg)" % (-G.WEST_TILT, -G.EAST_TILT))
    A = option("A: as drawn (garage EAST), parallel to lot", False, theta)
    B = option("B: mirrored (garage WEST), parallel to lot", True, theta)
    option("C: as drawn, square to street (theta=0)", False, 0.0)
    option("D: mirrored, square to street (theta=0)", True, 0.0)
    eave_report(theta)
    print("="*90)
    print("Rotation scan (main body 40x45 must fit; report N-S slide available):")
    for th10 in range(-90, -30, 5):
        th = th10/10.0
        T = feasible_T(G.MAIN, False, th)
        if T.is_empty: print("   theta %.1f: no fit" % th); continue
        minx, miny, maxx, maxy = T.bounds
        print("   theta %.1f: feasible set %.2f x %.2f ft, area %.2f" % (th, maxx-minx, maxy-miny, T.area))
    print("="*90)
    print("Max compliant front projection of the 24'-wide garage bay (main body 40x45 kept inside envelope):")
    for lab, mir in [("garage EAST (as drawn)", False), ("garage WEST (mirrored)", True)]:
        print("   %-24s p_max = %.2f ft  (plan shows 7.50 ft)" % (lab, max_projection(mir, theta)))
    print("   (same test at theta = -5.5 deg):")
    for lab, mir in [("garage EAST (as drawn)", False), ("garage WEST (mirrored)", True)]:
        print("   %-24s p_max = %.2f ft" % (lab, max_projection(mir, -5.5)))
