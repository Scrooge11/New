#!/usr/bin/env python3
"""Build absentee-owner (non-owner-occupied) property lists for Belmont, MA.

Input : MassGIS Level 3 standardized assessor extract (M026Assess_*.dbf) plus the
        TaxPar shapefile for parcel centroids, in ../data/raw/ (see fetch_massgis.py),
        and ../data/tax_delinquent_known.csv (hand-maintained delinquency records).
Output: CSV lists + one multi-sheet Excel workbook in ../output/.

Owner-occupancy is inferred the way the industry does it: the assessor's owner mailing
address (where the tax bill is sent) is compared with the property's situs address.
"""
import argparse
import collections
import csv
import datetime as dt
import difflib
import glob
import json
import os
import re

import shapefile
from dbfread import DBF
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
RAW = os.path.join(ROOT, "data", "raw")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
TODAY = dt.date.today()

RES_TYPES = {
    "101": "Single family",
    "102": "Condominium",
    "104": "Two-family",
    "105": "Three-family",
    "109": "Multiple houses on one parcel",
    "111": "Apartments (4-8 units)",
    "112": "Apartments (8+ units)",
    "013": "Mixed use, mostly residential",
    "031": "Mixed use, mostly commercial",
}
LAND_TYPES = {
    "106": "Accessory land with improvement",
    "130": "Developable residential land",
    "131": "Potentially developable residential land",
    "132": "Undevelopable residential land",
}
US_STATES = set(
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY "
    "NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR VI GU AS MP AA AE AP".split()
)
COUNTRY_WORDS = [
    "CANADA", "ONTARIO", "QUEBEC", "BRITISH COLUMBIA", "ALBERTA", "AUSTRALIA", "VICTORIA AUSTRALIA",
    "NEW ZEALAND", "UNITED KINGDOM", "ENGLAND", "SCOTLAND", "WALES", " UK", "IRELAND", "FRANCE", "GERMANY",
    "ITALY", "SPAIN", "PORTUGAL", "NETHERLANDS", "BELGIUM", "SWITZERLAND", "AUSTRIA", "SWEDEN", "NORWAY",
    "DENMARK", "FINLAND", "GREECE", "CZECH", "POLAND", "HUNGARY", "ISRAEL", "TURKEY", "CHINA", "HONG KONG",
    "TAIWAN", "JAPAN", "KOREA", "SINGAPORE", "MALAYSIA", "THAILAND", "VIETNAM", "INDIA", "PAKISTAN",
    "PHILIPPINES", "INDONESIA", "MEXICO", "BRAZIL", "ARGENTINA", "CHILE", "COLOMBIA", "PERU", "ARMENIA",
    "LEBANON", "EGYPT", "SAUDI", "UAE", "DUBAI", "QATAR", "SOUTH AFRICA", "NIGERIA", "KENYA", "RUSSIA",
    "UKRAINE", "IRAN", "IRAQ", "JORDAN", "CYPRUS", "MALTA", "BERMUDA", "BAHAMAS", "CAYMAN", "PANAMA",
    "COSTA RICA", "DOMINICAN", "JAMAICA", "HAITI", "PUERTO RICO",
]
BELMONT_ZIPS = {"02478", "02479"}
SUFFIX_MAP = {
    "ROAD": "RD", "RD": "RD", "STREET": "ST", "ST": "ST", "AVENUE": "AVE", "AVE": "AVE", "AV": "AVE",
    "TERRACE": "TERR", "TERR": "TERR", "TER": "TERR", "LANE": "LN", "LN": "LN", "LA": "LN", "DRIVE": "DR",
    "DR": "DR", "PLACE": "PL", "PL": "PL", "CIRCLE": "CIR", "CIR": "CIR", "COURT": "CT", "CT": "CT",
    "PARKWAY": "PKWY", "PKWY": "PKWY", "BOULEVARD": "BLVD", "BLVD": "BLVD", "HIGHWAY": "HWY", "HWY": "HWY",
    "SQUARE": "SQ", "SQ": "SQ", "EXTENSION": "EXT", "EXT": "EXT", "TRAIL": "TRL", "TRL": "TRL",
    "PLAZA": "PLZ", "PLZ": "PLZ", "POINT": "PT", "PT": "PT", "PATH": "PATH", "WAY": "WAY", "PARK": "PARK",
    "HILL": "HILL", "ROW": "ROW", "WALK": "WALK", "GREEN": "GREEN", "COMMON": "COMMON",
}
NUMBER_WORDS = {"ONE": "1", "TWO": "2", "THREE": "3", "FOUR": "4", "FIVE": "5", "SIX": "6", "SEVEN": "7",
                "EIGHT": "8", "NINE": "9", "TEN": "10"}
UNIT_WORDS = {"UNIT", "APT", "APARTMENT", "STE", "SUITE", "FL", "FLR", "FLOOR", "RM", "ROOM", "PMB", "BLDG"}

OWNER_TOKENS = {
    "corporate": r"\b(LLC|L L C|INC|INCORPORATED|CORP|CORPORATION|LP|LLP|LTD|PTY|PLC|COMPANY|PARTNERSHIP|"
                 r"PARTNERS|ASSOCIATES|ENTERPRISES|HOLDINGS|INVESTMENTS|VENTURES|DEVELOPMENT|DEVELOPERS|"
                 r"PROPERTIES|REALTY|MANAGEMENT|MGMT|CAPITAL|GROUP|FUND|BANK|MORTGAGE|BUILDERS|CONSTRUCTION)\b",
    "institutional": r"\b(TOWN OF|CITY OF|COMMONWEALTH|COMM OF MASS|UNITED STATES|USA|U S A|CHURCH|PARISH|"
                     r"TEMPLE|SYNAGOGUE|CONGREGATION|DIOCESE|ARCHDIOCESE|ARCHBISHOP|SCHOOL|SCHOOLS|COLLEGE|"
                     r"UNIVERSITY|ACADEMY|HOUSING AUTHORITY|MBTA|MWRA|HOSPITAL|HABITAT|CEMETERY|CLUB|"
                     r"ASSOCIATION|ASSN|FOUNDATION|SOCIETY|MINISTRIES|MASONIC|LODGE|VETERANS|LIBRARY|"
                     r"HISTORICAL|CONSERVATION|LAND TRUST INC|COOPERATIVE|CO-OP|CONDOMINIUM TRUST|CONDO TRUST)\b",
    "estate": r"\b(ESTATE OF|EST OF|HEIRS?|HEIRS OF|DEVISEES?|EXECUTOR|EXECUTRIX|EXEC|EXECS|ADMINISTRATOR|"
              r"ADMINISTRATRIX|ADMX|ADMR|PERS REP|PERSONAL REP|SURVIVING|DECEASED|DEC'D|DECD)\b",
    "trust": r"\b(TR|TRS|TRUST|TRUSTS|TRUSTEE|TRUSTEES|TTEE|TTEES|NOMINEE|REVOCABLE|IRREVOCABLE|RLT|FAMILY TR)\b",
}
CARE_OF_RE = re.compile(r"\bC/O\b|\bC O\b|\bIN CARE OF\b|\bATTN\b|\bATTENTION\b")
PO_BOX_RE = re.compile(r"\bP\s?O\s?BOX\b|\bPOB\b|\bPO BX\b|\bBOX\s+\d+\b|\bP\s?O\s?B\s+\d+")


def clean(s):
    s = (s or "") if isinstance(s, str) else ("" if s is None else str(s))
    s = s.upper().replace(".", " ").replace(",", " ")
    return re.sub(r"\s+", " ", s).strip()


def parse_number_token(tok):
    """'16-18' -> [16, 18]; '1100R' -> [1100]; '12' -> [12]; else None."""
    m = re.fullmatch(r"(\d+)[A-Z]?(?:\s*[-&/]\s*(\d+)[A-Z]?)?", tok)
    if not m:
        return None
    nums = [int(m.group(1))]
    if m.group(2):
        nums.append(int(m.group(2)))
    return nums


UNIT_CODE_RE = re.compile(r"U(\d{1,3}[A-Z]?|[A-Z]\d{0,2})")


def norm_unit(u):
    """'U201' -> '201', '#B5' -> 'B5', 'UNIT 02' -> '2', 'UB' -> 'B'."""
    u = re.sub(r"[^A-Z0-9]", "", (u or "").upper())
    if re.fullmatch(r"U(\d+[A-Z]?|[A-Z]\d*)", u):
        u = u[1:]
    return u.lstrip("0") or u or None


def split_street_unit(tokens):
    """Return (street_tokens, unit) - cuts at the first unit designator (UNIT 2, APT 3, #1, U1, STE 200...)."""
    unit = None
    cut = len(tokens)
    for k, t in enumerate(tokens):
        if k == 0:
            continue
        prev = tokens[k - 1] if k >= 1 else None
        # a short alphanumeric code right after the street suffix is a unit ("100 LEXINGTON ST B5", "19 BURNHAM ST A2", "RIPLEY RD REAR")
        if prev in SUFFIX_MAP and k >= 2 and (re.fullmatch(r"[A-Z]?\d{1,4}[A-Z]?", t) or t in {"REAR", "FRONT", "R", "FRT", "BSMT", "LOWER", "UPPER"}):
            cut = k
            unit = norm_unit(t) if re.search(r"\d", t) else None
            break
        if t in UNIT_WORDS or (t.startswith("#") and len(t) > 1) or UNIT_CODE_RE.fullmatch(t):
            cut = k
            if t.startswith("#"):
                unit = norm_unit(t[1:])
            elif UNIT_CODE_RE.fullmatch(t):
                unit = norm_unit(t[1:])
            elif k + 1 < len(tokens):
                unit = norm_unit(tokens[k + 1])
            break
    return tokens[:cut], unit


def normalize_street_tokens(tokens):
    toks = [t for t in tokens if t and t not in {"-", "&"}]
    toks = [t for i, t in enumerate(toks) if i == 0 or not re.fullmatch(r"\d+(ST|ND|RD|TH)", t)]  # drop '12TH' floor ordinals
    if not toks:
        return "", ""
    if len(toks) >= 2 and toks[-1] in SUFFIX_MAP:
        toks[-1] = SUFFIX_MAP[toks[-1]]
        core = " ".join(toks[:-1])
    else:
        core = " ".join(toks)
    return " ".join(toks), core


def parse_site(row):
    nums = parse_number_token(clean(row["ADDR_NUM"])) or []
    toks, unit_in_street = split_street_unit(clean(row["FULL_STR"]).split())
    street, core = normalize_street_tokens(toks)
    unit = norm_unit(clean(row["LOCATION"])) or unit_in_street or None
    return {"numbers": nums, "street": street, "core": core, "unit": unit}


def parse_owner_addr(addr):
    a = clean(addr)
    info = {"po_box": bool(PO_BOX_RE.search(a)), "care_of": bool(CARE_OF_RE.search(a)),
            "numbers": [], "street": "", "core": "", "unit": None, "raw": (addr or "").strip()}
    if not a or info["po_box"]:
        return info
    toks = a.split()
    toks = [NUMBER_WORDS.get(t, t) for t in toks]
    start = None
    for i, t in enumerate(toks):
        if parse_number_token(t) or re.fullmatch(r"\d+[A-Z]?-?", t):
            start = i
            break
    if start is None:
        info["street"], info["core"] = normalize_street_tokens(toks)
        return info
    numtok = toks[start].rstrip("-")
    j = start + 1
    if j < len(toks) and re.fullmatch(r"\d+[A-Z]?", toks[j]) and toks[start].endswith("-"):
        numtok = numtok + "-" + toks[j]
        j += 1
    elif j + 1 < len(toks) and toks[j] in {"-", "&"} and re.fullmatch(r"\d+[A-Z]?", toks[j + 1]):
        numtok = numtok + "-" + toks[j + 1]
        j += 2
    info["numbers"] = parse_number_token(numtok) or []
    rest = toks[j:]
    street_toks, unit = split_street_unit([None] + rest)  # leading placeholder so index 0 (the number) is skipped
    info["unit"] = unit
    info["street"], info["core"] = normalize_street_tokens(street_toks[1:])
    return info


def street_match(site, owner):
    if not site["core"] or not owner["core"]:
        return False
    if site["street"] == owner["street"] or site["core"] == owner["core"]:
        return True
    a, b = site["core"], owner["core"]
    if a[0] != b[0]:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.85


def number_match(site_nums, owner_nums):
    if not site_nums or not owner_nums:
        return False
    lo, hi = min(site_nums), max(site_nums)
    return any(lo <= n <= hi for n in owner_nums) or any(min(owner_nums) <= n <= max(owner_nums) for n in site_nums)


def owner_flags(name):
    n = clean(name)
    n_wo_real_estate = re.sub(r"\bREAL ESTATE\b", "REALESTATE", n)
    toks = n.split()
    flags = {
        "corporate": bool(re.search(OWNER_TOKENS["corporate"], n)),
        "institutional": bool(re.search(OWNER_TOKENS["institutional"], n)),
        "estate": bool(re.search(OWNER_TOKENS["estate"], n_wo_real_estate)),
        "trust": bool(re.search(OWNER_TOKENS["trust"], n)),
        # Patriot-style ownership codes follow the surname: LE = life estate, TE/JT/TC = co-tenancy codes.
        "life_estate": any(t in {"LE", "L/E"} for t in toks[1:]) or bool(re.search(r"\bLIFE (ESTATE|EST|TENANT|TENANCY)\b", n)),
        "et_al": bool(re.search(r"\bET ?ALS?\b|\bETALS?\b", n)),
    }
    if re.search(r"\bEST\b", n_wo_real_estate) and not flags["corporate"]:
        flags["estate"] = True
    if flags["institutional"]:
        kind = "institutional / government / nonprofit"
    elif flags["corporate"]:
        kind = "LLC / corporate"
    elif flags["estate"]:
        kind = "estate / heirs"
    elif flags["trust"]:
        kind = "trust"
    elif flags["life_estate"]:
        kind = "individual (life estate)"
    else:
        kind = "individual"
    flags["owner_type"] = kind
    return flags


def foreign_hint(row):
    blob = " ".join(clean(row[k]) for k in ("OWN_ADDR", "OWN_CITY", "OWN_CO"))
    state = clean(row["OWN_STATE"])
    co = clean(row["OWN_CO"])
    hits = [w.strip() for w in COUNTRY_WORDS if (" " + w.strip() + " ") in (" " + blob + " ") or blob.endswith(" " + w.strip())]
    if co and co not in {"USA", "US", "UNITED STATES", "U S A"}:
        hits.append(co)
    if state and state not in US_STATES:
        hits.append(f"state code '{state}'")
    return ", ".join(dict.fromkeys(hits))


MULTI_UNIT_CODES = {"102", "104", "105", "109", "111", "112", "013", "031"}
US_STATE_MISREADS = ("JAMAICA PLAIN", "WEST LEBANON", "LEBANON", "MEXICO", "PERU", "CANADA", "PARIS", "HOLLAND")


def classify_occupancy(row, site, own, fflags, use_code):
    """Return (occupancy label, absentee score, extras dict)."""
    city = clean(row["OWN_CITY"])
    state = clean(row["OWN_STATE"])
    zip5 = clean(row["OWN_ZIP"])[:5]
    extras = {"owner_next_door": ""}
    is_belmont = city.startswith("BELMONT") or city in {"WAVERLEY", "WAVERLY"} or (zip5 in BELMONT_ZIPS and state in {"MA", ""})
    # A valid US state code always wins over country-looking words (Jamaica Plain MA, West Lebanon NH, Mexico NY...).
    foreign = state not in US_STATES and bool(fflags)
    if own["po_box"]:
        if is_belmont:
            return "unknown - PO Box in Belmont", 1, extras
        loc = "out of country" if foreign else ("elsewhere in MA" if state == "MA" else ("out of state" if state in US_STATES else "location unclear"))
        return f"absentee - {loc} (PO Box)", {"out of country": 5, "elsewhere in MA": 3, "out of state": 4}.get(loc, 2), extras
    if is_belmont and not own["raw"]:
        return "unknown - no mailing street address", 1, extras
    if is_belmont and street_match(site, own) and site["numbers"] and own["numbers"]:
        if number_match(site["numbers"], own["numbers"]):
            if site["unit"] and own["unit"] and site["unit"] != own["unit"]:
                return "owner in same building (different unit)", 0, extras
            return "owner-occupied (tax bill goes to the property)", 0, extras
        diff = min(abs(a - b) for a in site["numbers"] for b in own["numbers"])
        if diff == 2 and use_code in MULTI_UNIT_CODES:
            # two-family / condo listed under one street number, owner uses the other unit's number (48 vs 50 Grant Ave)
            return "owner-occupied (other unit number of same building)", 0, extras
        if diff <= 6:
            extras["owner_next_door"] = "YES"
    if is_belmont:
        return "absentee - owner elsewhere in Belmont", 2, extras
    if foreign:
        return "absentee - out of country", 5, extras
    if state == "MA":
        return "absentee - elsewhere in MA", 3, extras
    if state in US_STATES:
        return "absentee - out of state", 4, extras
    return "absentee - location unclear", 3, extras


def parse_ls_date(s):
    s = clean(s)
    if re.fullmatch(r"\d{8}", s) and s[:4] != "0000":
        try:
            return dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        except ValueError:
            return None
    return None


def load_centroids(taxpar_base):
    """LOC_ID -> (lat, lon) from TaxPar polygon centroids (area-weighted over parts)."""
    tr = Transformer.from_crs("EPSG:26986", "EPSG:4326", always_xy=True)
    out = {}
    r = shapefile.Reader(taxpar_base)
    fields = [f[0] for f in r.fields[1:]]
    li = fields.index("LOC_ID")
    for sr in r.iterShapeRecords():
        loc = sr.record[li]
        pts = sr.shape.points
        parts = list(sr.shape.parts) + [len(pts)]
        best_area, cx, cy = 0.0, None, None
        for a, b in zip(parts[:-1], parts[1:]):
            ring = pts[a:b]
            area = 0.0
            sx = sy = 0.0
            for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
                cross = x1 * y2 - x2 * y1
                area += cross
                sx += (x1 + x2) * cross
                sy += (y1 + y2) * cross
            if abs(area) > best_area and area != 0:
                best_area = abs(area)
                cx, cy = sx / (3 * area), sy / (3 * area)
        if cx is None and pts:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
        if cx is not None:
            lon, lat = tr.transform(cx, cy)
            out[loc] = (round(lat, 6), round(lon, 6))
    return out


def load_delinquent():
    path = os.path.join(DATA, "tax_delinquent_known.csv")
    out = {}
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                out[r["parcel_id"].strip()] = r
    return out


COLUMNS = [
    "priority_score", "tax_delinquent", "occupancy", "property_address", "unit", "property_type", "owner_name",
    "owner_type", "mailing_address", "mailing_city", "mailing_state", "mailing_zip", "foreign_address_hint",
    "estate_or_heirs", "life_estate", "trust", "corporate", "care_of_mailing", "et_al_multiple_owners",
    "owner_next_door", "likely_inherited", "last_sale_date",
    "last_sale_price", "last_sale_type", "years_since_last_sale", "deed_book", "deed_page", "assessed_total",
    "assessed_land", "assessed_building", "year_built", "style", "units", "living_area_sqft", "lot_size_sqft",
    "zoning", "parcel_id", "use_code", "use_description", "tax_delinquent_detail", "tax_delinquent_source",
    "lat", "lon", "map_link", "loc_id", "data_vintage",
]


def build(assess_dbf, taxpar_base, vintage):
    delinquent = load_delinquent()
    centroids = load_centroids(taxpar_base) if taxpar_base else {}
    lut = {}
    for p in glob.glob(os.path.join(os.path.dirname(assess_dbf), "*UC_LUT*.dbf")):
        for r in DBF(p, encoding="cp1252"):
            code = r["USE_CODE"].strip()
            if r["TOWN_ID"] == 0:
                lut.setdefault(code, r["USE_DESC"].strip())
            else:
                lut[code] = r["USE_DESC"].strip()
    rows = []
    for r in DBF(assess_dbf, encoding="cp1252"):
        code = clean(r["USE_CODE"])
        ptype = RES_TYPES.get(code) or LAND_TYPES.get(code)
        if not ptype:
            continue
        site = parse_site(r)
        own = parse_owner_addr(r["OWN_ADDR"])
        of = owner_flags(r["OWNER1"])
        fhint = foreign_hint(r)
        occ, occ_score, extras = classify_occupancy(r, site, own, fhint, code)
        ls_date = parse_ls_date(r["LS_DATE"])
        price = r["LS_PRICE"] or 0
        nominal = price <= 100
        years = (TODAY.year - ls_date.year) if ls_date else None
        inherit = 0
        if of["estate"]:
            inherit += 5
        if own["care_of"]:
            inherit += 2
        if nominal and ls_date and ls_date.year >= 1990:
            inherit += 2
        if years is not None and years >= 30:
            inherit += 1
        if of["life_estate"]:
            inherit += 2
        if of["trust"]:
            inherit += 1
        if of["et_al"]:
            inherit += 1
        if extras["owner_next_door"]:
            inherit -= 1
        pid = clean(r["PROP_ID"])
        dq = delinquent.get(pid)
        score = occ_score + inherit + (10 if dq else 0)
        if of["institutional"]:
            score = 0
        lat, lon = centroids.get(r["LOC_ID"], (None, None))
        rows.append({
            "priority_score": score,
            "tax_delinquent": "YES" if dq else "",
            "occupancy": occ,
            "property_address": clean(r["SITE_ADDR"]),
            "unit": site["unit"] or "",
            "property_type": ptype,
            "owner_name": re.sub(r"\s+", " ", (r["OWNER1"] or "").strip()),
            "owner_type": of["owner_type"],
            "mailing_address": re.sub(r"\s+", " ", (r["OWN_ADDR"] or "").strip()),
            "mailing_city": (r["OWN_CITY"] or "").strip(),
            "mailing_state": (r["OWN_STATE"] or "").strip(),
            "mailing_zip": (r["OWN_ZIP"] or "").strip(),
            "foreign_address_hint": fhint,
            "estate_or_heirs": "YES" if of["estate"] else "",
            "life_estate": "YES" if of["life_estate"] else "",
            "trust": "YES" if of["trust"] else "",
            "corporate": "YES" if of["corporate"] else "",
            "care_of_mailing": "YES" if own["care_of"] else "",
            "et_al_multiple_owners": "YES" if of["et_al"] else "",
            "owner_next_door": extras["owner_next_door"],
            "likely_inherited": "",
            "last_sale_date": ls_date.isoformat() if ls_date else "",
            "last_sale_price": price,
            "last_sale_type": ("nominal / non-arms-length transfer" if nominal else "market sale") if ls_date else "",
            "years_since_last_sale": years if years is not None else "",
            "deed_book": (r["LS_BOOK"] or "").strip(),
            "deed_page": (r["LS_PAGE"] or "").strip(),
            "assessed_total": r["TOTAL_VAL"],
            "assessed_land": r["LAND_VAL"],
            "assessed_building": r["BLDG_VAL"],
            "year_built": r["YEAR_BUILT"] or "",
            "style": (r["STYLE"] or "").strip(),
            "units": r["UNITS"] or "",
            "living_area_sqft": r["RES_AREA"] or "",
            "lot_size_sqft": int(r["LOT_SIZE"]) if r["LOT_SIZE"] else "",
            "zoning": (r["ZONING"] or "").strip(),
            "parcel_id": pid,
            "use_code": code,
            "use_description": lut.get(code, ""),
            "tax_delinquent_detail": dq["status"] if dq else "",
            "tax_delinquent_source": dq["source_url"] if dq else "",
            "lat": lat if lat is not None else "",
            "lon": lon if lon is not None else "",
            "map_link": f"https://maps.google.com/?q={lat},{lon}" if lat is not None else "",
            "loc_id": (r["LOC_ID"] or "").strip(),
            "data_vintage": vintage,
        })
    for x in rows:
        family_signal = (x["estate_or_heirs"] == "YES" or x["care_of_mailing"] == "YES" or x["et_al_multiple_owners"] == "YES"
                         or (x["last_sale_type"].startswith("nominal") and x["owner_type"] not in {"LLC / corporate", "institutional / government / nonprofit"}))
        if family_signal and (x["occupancy"].startswith("absentee") or x["estate_or_heirs"] == "YES"):
            x["likely_inherited"] = "YES"
    rows.sort(key=lambda x: (-x["priority_score"], x["property_address"]))
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


def add_sheet(wb, title, rows, note=None):
    ws = wb.create_sheet(title=title[:31])
    header_fill = PatternFill("solid", fgColor="1F3A5F")
    start = 1
    if note:
        ws.cell(row=1, column=1, value=note).font = Font(italic=True, color="555555")
        start = 3
    for c, name in enumerate(COLUMNS, 1):
        cell = ws.cell(row=start, column=c, value=name)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for r_i, row in enumerate(rows, start + 1):
        for c, name in enumerate(COLUMNS, 1):
            v = row[name]
            cell = ws.cell(row=r_i, column=c, value=v)
            if name == "map_link" and v:
                cell.hyperlink = v
                cell.font = Font(color="0563C1", underline="single")
            if name in {"assessed_total", "assessed_land", "assessed_building", "last_sale_price"} and v != "":
                cell.number_format = "#,##0"
    widths = {"property_address": 28, "owner_name": 34, "mailing_address": 32, "mailing_city": 16, "occupancy": 40,
              "property_type": 18, "owner_type": 26, "foreign_address_hint": 22, "use_description": 30,
              "tax_delinquent_detail": 40, "tax_delinquent_source": 40, "map_link": 34, "last_sale_type": 30}
    for c, name in enumerate(COLUMNS, 1):
        ws.column_dimensions[get_column_letter(c)].width = widths.get(name, max(10, min(18, len(name) + 2)))
    ws.freeze_panes = ws.cell(row=start + 1, column=4)
    ws.auto_filter.ref = f"A{start}:{get_column_letter(len(COLUMNS))}{start + max(len(rows), 1)}"
    return ws


DATA_DICTIONARY = [
    ("priority_score", "Heuristic ranking: absentee distance (2-5) + inherited/estate signals (up to ~10) + 10 if a tax taking is on record. Higher = better lead. 0 for institutional owners."),
    ("tax_delinquent", "YES when the parcel appears in data/tax_delinquent_known.csv (published Notice of Tax Taking or Treasurer tax-title list)."),
    ("occupancy", "Inferred from the owner's tax-bill mailing address vs the property address. 'absentee - ...' = non-owner-occupied."),
    ("property_type", "From the state use code (101 single family, 102 condo, 104 two-family, 105 three-family, 111/112 apartments, 013/031 mixed use, 1xx land)."),
    ("owner_type", "Parsed from the owner name: individual, individual (life estate), trust, estate / heirs, LLC / corporate, institutional."),
    ("mailing_*", "Where the assessor mails the tax bill (OWN_ADDR / OWN_CITY / OWN_STATE / OWN_ZIP)."),
    ("foreign_address_hint", "Country or province words found in the mailing address, or a non-US state code."),
    ("estate_or_heirs", "Owner name contains ESTATE OF / EST OF / HEIRS / DEVISEES / EXECUTOR / ADMINISTRATOR etc. Strongest 'inherited' signal."),
    ("life_estate", "Owner holds a life estate (LE code after surname): elderly owner, remainder passes to heirs on death."),
    ("trust", "Owner is a trust or trustee (TR / TRS / TRUST / TRUSTEE / NOMINEE)."),
    ("corporate", "Owner is an LLC / corporation / partnership."),
    ("care_of_mailing", "Tax bill goes 'c/o' someone else - often an executor, relative or manager."),
    ("et_al_multiple_owners", "Owner name says ET AL: several co-owners of record, frequently siblings who inherited."),
    ("owner_next_door", "Owner's Belmont mailing address is on the same street within a few numbers - possibly a family compound or an adjacent lot; treat as a softer lead."),
    ("likely_inherited", "YES when an absentee (or estate-owned) property also shows a family-transfer signal: estate/heirs, c/o, et al, or last transfer at nominal price."),
    ("last_sale_date / last_sale_price / last_sale_type", "Last recorded transfer. Price of $0-$100 = nominal transfer (family, trust or estate deed rather than a market sale)."),
    ("years_since_last_sale", "Years since the last recorded transfer, as of the build date."),
    ("deed_book / deed_page", "Middlesex South Registry of Deeds book and page for the last transfer."),
    ("assessed_*", "FY2024 assessed values (land, building, total) in dollars."),
    ("lat / lon / map_link", "Parcel centroid from the MassGIS TaxPar polygon (condo units share the building centroid)."),
    ("parcel_id", "Assessor map-lot(-unit) identifier (PROP_ID). Use it in the Belmont Real Estate Database and in records requests."),
    ("data_vintage", "MassGIS Level 3 extract vintage. Belmont's newest published extract is fiscal year 2024; verify current ownership before outreach."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=RAW)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    assess = sorted(glob.glob(os.path.join(args.raw, "**", "*Assess*.dbf"), recursive=True))
    if not assess:
        raise SystemExit(f"no *Assess*.dbf under {args.raw}; run fetch_massgis.py first")
    assess_dbf = assess[-1]
    m = re.search(r"_(CY\d\d_FY\d\d)", os.path.basename(assess_dbf))
    vintage = m.group(1) if m else "unknown"
    taxpar = sorted(glob.glob(os.path.join(args.raw, "**", "*TaxPar*.shp"), recursive=True))
    taxpar_base = taxpar[-1][:-4] if taxpar else None
    print(f"assessor extract: {assess_dbf}\nvintage: {vintage}\ntaxpar: {taxpar_base}")
    rows = build(assess_dbf, taxpar_base, vintage)
    os.makedirs(args.out, exist_ok=True)

    improved = [r for r in rows if r["use_code"] in RES_TYPES]
    non_inst = [r for r in improved if r["owner_type"] != "institutional / government / nonprofit"]
    absentee = [r for r in non_inst if r["occupancy"].startswith("absentee")]
    lists = collections.OrderedDict()
    lists["Non-owner-occupied (all)"] = absentee
    lists["Likely inherited (absentee)"] = [r for r in absentee if r["likely_inherited"] == "YES"]
    lists["Individuals & trusts only"] = [r for r in absentee if r["owner_type"] != "LLC / corporate"]
    lists["Estate & heirs owned"] = [r for r in non_inst if r["estate_or_heirs"] == "YES" or r["care_of_mailing"] == "YES"]
    lists["Out of country"] = [r for r in absentee if "out of country" in r["occupancy"]]
    lists["Out of state"] = [r for r in absentee if "out of state" in r["occupancy"]]
    lists["Elsewhere in MA"] = [r for r in absentee if "elsewhere in MA" in r["occupancy"]]
    lists["Elsewhere in Belmont"] = [r for r in absentee if "elsewhere in Belmont" in r["occupancy"]]
    lists["LLC & corporate owned"] = [r for r in non_inst if r["corporate"] == "YES"]
    lists["Trust owned (absentee)"] = [r for r in absentee if r["owner_type"] == "trust"]
    lists["PO Box or unclear"] = [r for r in non_inst if r["occupancy"].startswith("unknown") or "unclear" in r["occupancy"]]
    lists["Life-estate watchlist"] = [r for r in non_inst if r["life_estate"] == "YES"]
    lists["Vacant residential land"] = [r for r in rows if r["use_code"] in LAND_TYPES and r["owner_type"] != "institutional / government / nonprofit"]
    lists["Tax delinquent (known)"] = [r for r in rows if r["tax_delinquent"] == "YES"]

    slug = lambda s: re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    write_csv(os.path.join(args.out, "belmont_all_residential_scored.csv"), rows)
    for name, lst in lists.items():
        write_csv(os.path.join(args.out, f"belmont_{slug(name)}.csv"), lst)

    occ_counts = collections.Counter(r["occupancy"] for r in non_inst)
    type_counts = collections.Counter((r["property_type"], r["occupancy"].startswith("absentee")) for r in non_inst)
    summary = {
        "built": TODAY.isoformat(),
        "data_vintage": vintage,
        "source": "MassGIS Level 3 standardized assessor parcels, town 026 Belmont",
        "residential_records_total": len(rows),
        "improved_residential_records": len(improved),
        "improved_residential_excluding_institutional": len(non_inst),
        "non_owner_occupied": len(absentee),
        "occupancy_breakdown": dict(occ_counts.most_common()),
        "absentee_by_property_type": {pt: {"absentee": type_counts[(pt, True)], "owner_or_unknown": type_counts[(pt, False)]}
                                      for pt in RES_TYPES.values() if type_counts[(pt, True)] or type_counts[(pt, False)]},
        "list_sizes": {k: len(v) for k, v in lists.items()},
        "owner_type_breakdown_absentee": dict(collections.Counter(r["owner_type"] for r in absentee).most_common()),
        "top_mailing_states_absentee": dict(collections.Counter(r["mailing_state"] or "(blank)" for r in absentee).most_common(15)),
        "largest_absentee_owners": dict(collections.Counter(r["owner_name"] for r in absentee).most_common(12)),
    }
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.column_dimensions["A"].width = 48
    ws.column_dimensions["B"].width = 16
    ws.append(["Belmont, MA - non-owner-occupied / absentee owner property lists"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append([f"Built {TODAY.isoformat()} from MassGIS Level 3 assessor extract, vintage {vintage} (Belmont's newest published extract)."])
    ws.append(["Owner-occupancy is inferred from where the tax bill is mailed vs. the property address. Verify current ownership before outreach."])
    ws.append([])
    ws.append(["Improved residential records (excl. institutional owners)", len(non_inst)])
    ws.append(["Non-owner-occupied (absentee) records", len(absentee)])
    ws.append([])
    ws.append(["Occupancy class", "Records"])
    ws["A8"].font = ws["B8"].font = Font(bold=True)
    for k, v in occ_counts.most_common():
        ws.append([k, v])
    ws.append([])
    ws.append(["Sheet", "Records"])
    for k, v in lists.items():
        ws.append([k, len(v)])
    ws.append([])
    ws.append(["Absentee by property type", "Absentee / total"])
    for pt, d in summary["absentee_by_property_type"].items():
        ws.append([pt, f"{d['absentee']} / {d['absentee'] + d['owner_or_unknown']}"])
    notes = {
        "Non-owner-occupied (all)": "Every improved residential property whose tax bill is mailed somewhere other than the property. Sorted by priority score.",
        "Likely inherited (absentee)": "Absentee properties with a family-transfer signal: estate/heirs, c/o mailing, 'et al' co-owners, or a last transfer at nominal price (no market sale) held by an individual or trust.",
        "Individuals & trusts only": "Non-owner-occupied properties excluding LLC / corporate owners - the mom-and-pop and inherited stock.",
        "Estate & heirs owned": "Owner is an estate, heirs, executor or administrator, or the bill goes c/o someone else - the clearest inherited-property signal, any occupancy.",
        "Life-estate watchlist": "Owner-occupied today in most cases; the owner holds a life estate and the property passes to the remaindermen (heirs) at death.",
        "Tax delinquent (known)": "Only parcels with a published tax taking / tax title record. Belmont does not publish a full delinquent list online - see templates/records_request_treasurer.md.",
        "PO Box or unclear": "Tax bill goes to a PO Box or the mailing address could not be parsed; occupancy cannot be inferred.",
        "Vacant residential land": "Land parcels (no house) - included because inherited lots are often absentee-owned.",
    }
    for name, lst in lists.items():
        add_sheet(wb, name, lst, notes.get(name))
    wd = wb.create_sheet("Data dictionary")
    wd.column_dimensions["A"].width = 40
    wd.column_dimensions["B"].width = 120
    wd.append(["Column", "Meaning"])
    wd["A1"].font = wd["B1"].font = Font(bold=True)
    for k, v in DATA_DICTIONARY:
        wd.append([k, v])
    wb.save(os.path.join(args.out, "belmont_absentee_owner_lists.xlsx"))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
