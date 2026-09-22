"""Parse Patriot-style assessor owner names into people, a mailing name and a salutation.

Format seen in Belmont: 'SURNAME [codes] FIRST M [SUFFIX] & FIRST2 M2 [SURNAME2] [SUFFIX2]'
where codes are ownership abbreviations (LE life estate, TE tenants by entirety, JT joint tenants,
TC tenants in common, TR/TRS trustee(s), ETAL). Estates read 'SURNAME ESTATE OF FIRST' or
'SURNAME FIRST M EST OF'. Trusts, LLCs and institutions are returned as organizations.
"""
import re

CODES = {"LE", "TE", "JT", "TC", "TR", "TRS", "TTEE", "TTEES", "ETAL", "ETALS", "ET", "AL", "L/E", "TRUSTEE",
         "TRUSTEES", "TEN", "COM", "ENT", "JTS", "TIC", "JTWROS", "TBE"}
SUFFIXES = {"JR", "SR", "II", "III", "IV", "MD", "DDS", "ESQ", "PHD"}
ESTATE_MARKERS = {"ESTATE", "EST", "HEIRS", "DEVISEES", "DEVISEE"}
ORG_WORDS = {"LLC", "INC", "CORP", "CORPORATION", "LP", "LLP", "LTD", "PTY", "COMPANY", "CO", "PARTNERSHIP",
             "PARTNERS", "ASSOCIATES", "REALTY", "PROPERTIES", "HOLDINGS", "INVESTMENTS", "TRUST", "TRUSTS", "NOMINEE",
             "BANK", "NA", "CHURCH", "PARISH", "AUTHORITY", "TOWN", "CITY", "COMMONWEALTH", "SCHOOL", "COLLEGE",
             "UNIVERSITY", "FOUNDATION", "ASSOCIATION", "ASSN", "SOCIETY", "GROUP", "FUND", "CAPITAL", "DEVELOPMENT",
             "ENTERPRISES", "VENTURES", "MANAGEMENT", "MGMT", "REALESTATE", "CONDOMINIUM", "CONDO"}
PARTICLES = {"DE", "DI", "DA", "DEL", "DELLA", "VAN", "VON", "DER", "LA", "MC", "O", "ST", "SAN", "SANTA", "DU", "LO"}


def tc(word):
    """Title-case a name token, keeping hyphens, apostrophes and Mc/Mac/O' prefixes readable."""
    w = word.lower()
    parts = re.split(r"([-'])", w)
    out = "".join(p.capitalize() if p not in "-'" else p for p in parts)
    if re.match(r"^mc[a-z]", w):
        out = "Mc" + out[2:].capitalize()
    if re.match(r"^o'[a-z]", w):
        out = "O'" + out[2:].capitalize()
    return out


def _person(tokens, default_surname):
    toks = [t for t in tokens if t not in CODES]
    suffix = [t for t in toks if t in SUFFIXES]
    toks = [t for t in toks if t not in SUFFIXES]
    if not toks:
        return None
    surname = default_surname
    # first token repeating the surname ('MIKAELIAN SONIA'), or a trailing own surname ('WILFRED F BIELITZ')
    if len(toks) >= 2 and toks[0] == default_surname:
        toks = toks[1:]
    elif len(toks) >= 2 and toks[-1] == default_surname:
        toks = toks[:-1]
    elif len(toks) >= 3 and len(toks[-1]) >= 3 and not re.fullmatch(r"[A-Z]\.?", toks[-1]):
        surname = toks[-1]
        toks = toks[:-1]
    first = toks[0]
    middle = toks[1] if len(toks) > 1 else ""
    return {"first": tc(first), "middle": (middle[0] + "." if middle else ""), "surname": tc(surname),
            "suffix": tc(suffix[0]) if suffix else ""}


def parse_owner(name):
    raw = re.sub(r"\s+", " ", (name or "").strip().upper())
    raw = raw.replace(",", " ")
    raw = re.sub(r"\bAND\b", "&", raw)
    raw = re.sub(r"\bL L C\b", "LLC", raw)
    toks = [t for t in raw.split() if t]
    while toks and toks[-1] == "&":
        toks.pop()
    res = {"raw": (name or "").strip(), "kind": "people", "persons": [], "surname": "", "mail_name": "",
           "salutation": "", "et_al": any(t in {"ETAL", "ETALS"} for t in toks) or "ET AL" in raw, "estate": False}
    if not toks:
        res.update(kind="unknown", mail_name="Property Owner", salutation="Dear Property Owner,")
        return res
    words = set(toks)
    # organizations: LLCs, trusts written as names, banks, churches
    if (words & ORG_WORDS) and not (toks[1:2] and toks[1] in CODES) and not (toks[1:2] and toks[1] in ESTATE_MARKERS):
        pretty = " ".join(tc(t) if t not in {"LLC", "LP", "LLP", "INC", "NA", "II", "III"} else t for t in toks)
        pretty = re.sub(r"\bTrs?\b", "", pretty).strip()
        sal = "Dear Trustee," if "TRUST" in raw or "TRS" in words or "TR" in words else "Dear Property Owner,"
        res.update(kind="organization", mail_name=pretty, salutation=sal)
        return res
    # estates: 'GRANT ESTATE OF HELEN P', 'HAASE FLORENCE W ESTATE OF', 'SOLIMINE EST CORRADINO', 'CONMAY MARY EST OF'
    if words & ESTATE_MARKERS:
        surname = toks[0]
        body = [t for t in toks[1:] if t not in ESTATE_MARKERS and t != "OF" and t not in CODES]
        p = _person(body, surname) if body else None
        pname = (f"{p['first']} {p['middle']} {p['surname']}".replace("  ", " ").strip()) if p else tc(surname)
        res.update(kind="estate", estate=True, surname=tc(surname), persons=[p] if p else [],
                   mail_name=f"Estate of {pname}", salutation=f"To the family of {pname},")
        return res
    surname = toks[0]
    i = 1
    if i < len(toks) and toks[i] in PARTICLES and i + 1 < len(toks) and toks[i + 1] not in CODES:
        surname = toks[0] + " " + toks[1]
        i = 2
    # suffix right after the surname belongs to the first person ('DAUNT JR LE TRS CHARLES A')
    lead_suffix = ""
    while i < len(toks) and (toks[i] in CODES or toks[i] in SUFFIXES):
        if toks[i] in SUFFIXES:
            lead_suffix = toks[i]
        i += 1
    rest = toks[i:]
    groups, cur = [], []
    for t in rest:
        if t == "&":
            groups.append(cur)
            cur = []
        else:
            cur.append(t)
    groups.append(cur)
    persons = []
    for gi, g in enumerate(groups):
        p = _person(g, surname)
        if p:
            if gi == 0 and lead_suffix and not p["suffix"]:
                p["suffix"] = tc(lead_suffix)
            persons.append(p)
    if not persons:
        res.update(kind="unknown", surname=tc(surname), mail_name=tc(surname) + " Family",
                   salutation=f"Dear {tc(surname)} Family,")
        return res
    res["surname"] = tc(surname)
    res["persons"] = persons

    def full(p):
        return " ".join(x for x in [p["first"], p["middle"], p["surname"], p["suffix"]] if x)

    def first_last(p):
        return " ".join(x for x in [p["first"], p["surname"]] if x)

    same = all(p["surname"] == persons[0]["surname"] for p in persons)
    if len(persons) == 1:
        mail = full(persons[0])
        sal = f"Dear {first_last(persons[0])},"
    elif same and len(persons) == 2:
        a, b = persons
        mail = f"{a['first']} {a['middle']} & {b['first']} {b['middle']} {a['surname']}".replace("  ", " ")
        mail = re.sub(r" +", " ", mail)
        sal = f"Dear {a['first']} and {b['first']} {a['surname']},"
    elif same:
        firsts = [p["first"] for p in persons]
        mail = ", ".join(firsts[:-1]) + " & " + firsts[-1] + " " + persons[0]["surname"]
        sal = "Dear " + ", ".join(firsts[:-1]) + " and " + firsts[-1] + " " + persons[0]["surname"] + ","
    else:
        mail = " & ".join(full(p) for p in persons)
        sal = "Dear " + " and ".join(first_last(p) for p in persons) + ","
    res["mail_name"] = mail
    res["salutation"] = sal
    return res


if __name__ == "__main__":
    import sys
    for line in sys.stdin:
        r = parse_owner(line.strip())
        print(f"{r['raw']!r:58} -> [{r['kind']}] {r['mail_name']!r:42} | {r['salutation']}")
