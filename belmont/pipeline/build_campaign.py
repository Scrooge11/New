#!/usr/bin/env python3
"""Build outreach campaigns (mailing lists, skip-trace exports, merged letters) from the lead lists.

Campaigns:
  life_estate       owners holding a life estate (elderly owners who have already deeded the house to family)
  likely_inherited  absentee properties with an estate / heirs / c-o / et-al / nominal-transfer signal
  estate_heirs      properties owned by an estate or heirs, or billed c/o someone

Outputs ../campaigns/<id>/{mailing_list.csv, mailing_list.xlsx, skip_trace_export.csv, letters_<id>.docx}
and ../output/campaigns.json for the dashboard.
"""
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys

from docx import Document
from docx.shared import Inches, Pt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from names import parse_owner, tc  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "output")
CAMP = os.path.join(ROOT, "campaigns")
TPL = os.path.join(CAMP, "templates")
TODAY = dt.date.today()
LAND_TYPES = {"Accessory land with improvement", "Developable residential land", "Potentially developable residential land",
              "Undevelopable residential land"}

CAMPAIGNS = [
    {"id": "life_estate", "label": "Life-estate holders",
     "description": "Owners who keep a life estate after deeding the home to family. Owner and remaindermen must both sign a sale.",
     "select": lambda r: r["life_estate"] == "YES"},
    {"id": "likely_inherited", "label": "Likely inherited (absentee)",
     "description": "Non-owner-occupied properties with an estate, heirs, c/o, et-al or nominal-transfer signal.",
     "select": lambda r: r["likely_inherited"] == "YES" and (r["occupancy"].startswith("absentee") or r["estate_or_heirs"] == "YES")},
    {"id": "estate_heirs", "label": "Estate & heirs owned",
     "description": "Owner of record is an estate, heirs, executor or administrator, or the bill goes c/o someone.",
     "select": lambda r: r["estate_or_heirs"] == "YES" or r["care_of_mailing"] == "YES"},
]
STATUSES = ["Not contacted", "Letter 1 sent", "Letter 2 sent", "Postcard sent", "Replied", "Interested", "Appointment set",
            "Offer made", "Not interested", "Do not contact", "Sold / closed"]
SUFFIX_UPPER = {"NE", "NW", "SE", "SW", "N", "S", "E", "W", "PO", "II", "III"}


def pretty_addr(a):
    """'40 MAPLE ST' -> '40 Maple St'; keeps unit tokens and directionals readable."""
    out = []
    for t in (a or "").split():
        if t.upper() in SUFFIX_UPPER or re.fullmatch(r"[A-Z]?\d+[A-Z]?", t.upper()) or re.fullmatch(r"U\d+[A-Z]?", t.upper()):
            out.append(t.upper())
        elif t.upper() in {"BOX"}:
            out.append("Box")
        else:
            out.append(tc(t))
    return " ".join(out).replace("Po Box", "PO Box")


def norm_key(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def split_unit(addr):
    """Return (line1, line2) with a unit designator moved to line 2 for USPS."""
    a = re.sub(r"\s+", " ", (addr or "").strip())
    m = re.search(r"\s(UNIT|APT|STE|SUITE|#|U)\s?([A-Z0-9-]+)$", a.upper())
    if m and not re.search(r"\b(PO|P O)\b", a.upper()):
        return a[: m.start()].strip(), (m.group(1).replace("U", "UNIT") if m.group(1) == "U" else m.group(1).replace("#", "UNIT")) + " " + m.group(2)
    return a, ""


def load_rows():
    rows = list(csv.DictReader(open(os.path.join(OUT, "belmont_all_residential_scored.csv"), encoding="utf-8")))
    return [r for r in rows if not r["owner_type"].startswith("institutional")]


def build_households(rows, camp_id):
    groups = {}
    for r in rows:
        p = parse_owner(r["owner_name"])
        key = norm_key(r["mailing_address"]) + "|" + norm_key(r["mailing_zip"][:5] or r["mailing_city"]) + "|" + norm_key(p["surname"] or p["mail_name"])
        g = groups.setdefault(key, {"parsed": [], "rows": []})
        g["parsed"].append(p)
        g["rows"].append(r)
    out = []
    for key, g in groups.items():
        # prefer the most complete name variant (most persons, then longest)
        best = max(g["parsed"], key=lambda p: (len(p["persons"]), len(p["mail_name"])))
        r0 = sorted(g["rows"], key=lambda r: (0 if r["occupancy"].startswith("owner") else 1, -float(r["assessed_total"] or 0)))[0]
        line1, line2 = split_unit(r0["mailing_address"])
        props = []
        for r in sorted(g["rows"], key=lambda r: (0 if r["occupancy"].startswith("owner") else 1, -float(r["assessed_total"] or 0))):
            props.append({
                "parcel_id": r["parcel_id"], "address": pretty_addr(r["property_address"]), "type": r["property_type"],
                "assessed": int(float(r["assessed_total"] or 0)), "occupancy": r["occupancy"],
                "is_home": r["occupancy"].startswith("owner-occupied"), "year_built": r["year_built"],
                "years_since_transfer": r["years_since_last_sale"], "last_sale_type": r["last_sale_type"],
                "score": int(r["priority_score"] or 0),
            })
        homes = [p for p in props if p["is_home"]]
        absentee = not homes
        addrs = [p["address"] for p in props]
        if len(props) == 1:
            phrase = ("your home at " if homes else "your property at ") + addrs[0]
        elif homes and len(props) == 2:
            phrase = f"your home at {homes[0]['address']} and your property at {[p for p in props if not p['is_home']][0]['address']}"
        else:
            phrase = "your properties at " + ", ".join(addrs[:-1]) + " and " + addrs[-1]
        hid = "hh_" + hashlib.sha1(key.encode()).hexdigest()[:10]
        out.append({
            "id": hid, "campaign": camp_id, "kind": best["kind"], "contact_name": best["mail_name"],
            "salutation": best["salutation"], "surname": best["surname"],
            "first_names": ", ".join(p["first"] for p in best["persons"]) if best["persons"] else "",
            "persons": [{"first": p["first"], "last": p["surname"]} for p in best["persons"]],
            "owner_names_raw": sorted({r["owner_name"] for r in g["rows"]}),
            "address_line_1": pretty_addr(line1), "address_line_2": pretty_addr(line2) if line2 else "",
            "city": " ".join(tc(t) for t in r0["mailing_city"].split()) if r0["mailing_city"] else "", "state": r0["mailing_state"], "zip": r0["mailing_zip"],
            "mailing_is_property": bool(homes), "absentee": absentee,
            "out_of_state": r0["mailing_state"] not in ("MA", ""), "et_al": any(p["et_al"] for p in g["parsed"]),
            "estate": any(p["estate"] for p in g["parsed"]), "life_estate": any(r["life_estate"] == "YES" for r in g["rows"]),
            "care_of": any(r["care_of_mailing"] == "YES" for r in g["rows"]),
            "properties": props, "property_phrase": phrase, "primary_property": props[0]["address"],
            "priority": max(p["score"] for p in props),
        })
    out.sort(key=lambda h: (-h["priority"], h["surname"], h["contact_name"]))
    return out


MAIL_COLS = ["contact_id", "full_name", "salutation", "first_names", "last_name", "address_line_1", "address_line_2", "city", "state",
             "zip", "property_address", "all_property_addresses", "property_count", "property_type", "mailing_is_property",
             "absentee", "out_of_state", "owner_kind", "life_estate", "estate", "et_al", "care_of", "priority_score",
             "assessed_total", "year_built", "years_since_last_transfer", "parcel_ids", "owner_names_on_record", "letter_property_phrase"]


def household_row(h):
    p0 = h["properties"][0]
    return {
        "contact_id": h["id"], "full_name": h["contact_name"], "salutation": h["salutation"], "first_names": h["first_names"],
        "last_name": h["surname"], "address_line_1": h["address_line_1"], "address_line_2": h["address_line_2"],
        "city": h["city"], "state": h["state"], "zip": h["zip"], "property_address": p0["address"],
        "all_property_addresses": "; ".join(p["address"] for p in h["properties"]), "property_count": len(h["properties"]),
        "property_type": p0["type"], "mailing_is_property": "YES" if h["mailing_is_property"] else "",
        "absentee": "YES" if h["absentee"] else "", "out_of_state": "YES" if h["out_of_state"] else "", "owner_kind": h["kind"],
        "life_estate": "YES" if h["life_estate"] else "", "estate": "YES" if h["estate"] else "", "et_al": "YES" if h["et_al"] else "",
        "care_of": "YES" if h["care_of"] else "", "priority_score": h["priority"], "assessed_total": p0["assessed"],
        "year_built": p0["year_built"], "years_since_last_transfer": p0["years_since_transfer"],
        "parcel_ids": "; ".join(p["parcel_id"] for p in h["properties"]), "owner_names_on_record": "; ".join(h["owner_names_raw"]),
        "letter_property_phrase": h["property_phrase"],
    }


SKIP_COLS = ["First Name", "Last Name", "Mailing Address", "Mailing Unit", "Mailing City", "Mailing State", "Mailing Zip",
             "Property Address", "Property City", "Property State", "Property Zip", "Owner Name On Record", "Parcel ID", "Contact ID"]


def skip_rows(h):
    p0 = h["properties"][0]
    persons = h["persons"] or [{"first": "", "last": h["contact_name"]}]
    out = []
    for p in persons[:3]:
        out.append({"First Name": p["first"], "Last Name": p["last"], "Mailing Address": h["address_line_1"],
                    "Mailing Unit": h["address_line_2"], "Mailing City": h["city"], "Mailing State": h["state"], "Mailing Zip": h["zip"],
                    "Property Address": p0["address"], "Property City": "Belmont", "Property State": "MA", "Property Zip": "02478",
                    "Owner Name On Record": h["owner_names_raw"][0], "Parcel ID": p0["parcel_id"], "Contact ID": h["id"]})
    return out


def load_settings():
    s = json.load(open(os.path.join(TPL, "campaign_settings.json")))
    if not s.get("letter_date"):
        s["letter_date"] = TODAY.strftime("%B %-d, %Y")
    return s


def merge(text, h, s):
    fields = {
        "salutation": h["salutation"], "contact_name": h["contact_name"], "first_names": h["first_names"] or h["contact_name"],
        "property_phrase": h["property_phrase"], "property_address": h["primary_property"], "address_line_1": h["address_line_1"],
        "address_line_2": h["address_line_2"], "city": h["city"], "state": h["state"], "zip": h["zip"], "date": s["letter_date"],
    }
    fields.update({k: v for k, v in s.items() if isinstance(v, str)})
    return re.sub(r"\{\{(\w+)\}\}", lambda m: fields.get(m.group(1), m.group(0)), text)


def write_letters_docx(path, households, s, body_tpl):
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = Inches(1)
        sec.left_margin = sec.right_margin = Inches(1.1)
    st = doc.styles["Normal"]
    st.font.name = "Georgia"
    st.font.size = Pt(11)
    for i, h in enumerate(households):
        if i:
            doc.add_page_break()
        head = doc.add_paragraph()
        head.add_run("\n".join(x for x in [s["sender_name"], s["company"], s["return_address_1"], s["return_address_2"],
                                            s["phone"] + "  |  " + s["email"]] if x and not x.startswith("[Your company"))).font.size = Pt(9.5)
        head.paragraph_format.space_after = Pt(14)
        doc.add_paragraph(s["letter_date"]).paragraph_format.space_after = Pt(14)
        addr = doc.add_paragraph()
        addr.add_run("\n".join(x for x in [h["contact_name"], h["address_line_1"], h["address_line_2"],
                                            f"{h['city']}, {h['state']} {h['zip']}"] if x))
        addr.paragraph_format.space_after = Pt(16)
        for block in merge(body_tpl, h, s).strip().split("\n\n"):
            lines = block.split("\n")
            if all(l.startswith("- ") for l in lines):
                for l in lines:
                    p = doc.add_paragraph(l[2:], style="List Bullet")
                    p.paragraph_format.space_after = Pt(3)
            else:
                p = doc.add_paragraph()
                for j, l in enumerate(lines):
                    if j:
                        p.add_run().add_break()
                    p.add_run(l)
                p.paragraph_format.space_after = Pt(10)
    doc.save(path)


def write_xlsx(path, households, camp):
    wb = Workbook()
    ws = wb.active
    ws.title = "Households"
    ws.append([f"{camp['label']} - Belmont, MA mailing list ({len(households)} households, built {TODAY.isoformat()})"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append([camp["description"]])
    ws.append([])
    ws.append(MAIL_COLS)
    for c in range(1, len(MAIL_COLS) + 1):
        cell = ws.cell(row=4, column=c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F3A5F")
    for h in households:
        r = household_row(h)
        ws.append([r[c] for c in MAIL_COLS])
    widths = {"full_name": 34, "salutation": 36, "address_line_1": 30, "property_address": 28, "all_property_addresses": 40,
              "owner_names_on_record": 44, "letter_property_phrase": 48, "city": 16}
    for c, name in enumerate(MAIL_COLS, 1):
        ws.column_dimensions[get_column_letter(c)].width = widths.get(name, max(10, min(16, len(name) + 2)))
    ws.freeze_panes = "C5"
    ws.auto_filter.ref = f"A4:{get_column_letter(len(MAIL_COLS))}{4 + len(households)}"
    ws2 = wb.create_sheet("Skip trace export")
    ws2.append(SKIP_COLS)
    for h in households:
        for r in skip_rows(h):
            ws2.append([r[c] for c in SKIP_COLS])
    for c in range(1, len(SKIP_COLS) + 1):
        ws2.cell(row=1, column=c).font = Font(bold=True)
        ws2.column_dimensions[get_column_letter(c)].width = 20
    ws3 = wb.create_sheet("Tracking")
    ws3.append(["contact_id", "full_name", "status", "letter_1_date", "letter_2_date", "postcard_date", "reply_date", "notes"])
    for h in households:
        ws3.append([h["id"], h["contact_name"], "Not contacted", "", "", "", "", ""])
    ws3.column_dimensions["B"].width = 34
    ws3.column_dimensions["H"].width = 60
    wb.save(path)


def main():
    rows = load_rows()
    s = load_settings()
    body = open(os.path.join(TPL, "letter1.md"), encoding="utf-8").read()
    defaults = {k: open(os.path.join(TPL, f), encoding="utf-8").read() for k, f in
                [("letter1", "letter1.md"), ("letter2", "letter2_followup.md"), ("postcard", "postcard.md"), ("email", "email.md")]}
    dashboard = {"built": TODAY.isoformat(), "statuses": STATUSES, "settings_default": s, "templates": defaults, "campaigns": []}
    for camp in CAMPAIGNS:
        sel = [r for r in rows if camp["select"](r)]
        hh = build_households(sel, camp["id"])
        d = os.path.join(CAMP, camp["id"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "mailing_list.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=MAIL_COLS)
            w.writeheader()
            for h in hh:
                w.writerow(household_row(h))
        with open(os.path.join(d, "skip_trace_export.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SKIP_COLS)
            w.writeheader()
            for h in hh:
                w.writerows(skip_rows(h))
        write_xlsx(os.path.join(d, "mailing_list.xlsx"), hh, camp)
        write_letters_docx(os.path.join(d, f"letters_{camp['id']}.docx"), hh, s, body)
        dashboard["campaigns"].append({"id": camp["id"], "label": camp["label"], "description": camp["description"],
                                       "records": len(sel), "households": hh})
        print(f"{camp['id']:18} records={len(sel):4}  households={len(hh):4}  absentee={sum(1 for h in hh if h['absentee']):4}  "
              f"out_of_state={sum(1 for h in hh if h['out_of_state']):3}  people={sum(1 for h in hh if h['kind']=='people'):4}")
    with open(os.path.join(OUT, "campaigns.json"), "w", encoding="utf-8") as f:
        json.dump(dashboard, f, separators=(",", ":"))
    print("wrote", os.path.join(OUT, "campaigns.json"), f"{os.path.getsize(os.path.join(OUT, 'campaigns.json'))/1e6:.2f} MB")


if __name__ == "__main__":
    main()
