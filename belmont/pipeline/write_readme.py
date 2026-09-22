#!/usr/bin/env python3
"""Regenerate ../README.md from ../output/summary.json so the numbers always match the data."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
s = json.load(open(os.path.join(ROOT, "output", "summary.json")))
occ, ls, ot, st = s["occupancy_breakdown"], s["list_sizes"], s["owner_type_breakdown_absentee"], s["top_mailing_states_absentee"]
oak = s["largest_absentee_owners"].get("OAK REALTY & SERVICE COMPANY LLC", 0)
pct = 100.0 * s["non_owner_occupied"] / s["improved_residential_excluding_institutional"]
owner_occ = occ.get("owner-occupied (tax bill goes to the property)", 0) + occ.get("owner-occupied (other unit number of same building)", 0)
people = ot.get("individual", 0) + ot.get("trust", 0) + ot.get("individual (life estate)", 0) + ot.get("estate / heirs", 0)
states = ", ".join(f"{k} {v}" for k, v in st.items() if k not in ("MA", "(blank)"))

readme = f"""# Belmont, MA: non-owner-occupied, absentee-owner and tax-delinquent property search

Built {s['built']} from the newest public assessor extract for Belmont (MassGIS Level 3 standardized
parcels, vintage **{s['data_vintage']}** = fiscal year 2024). Everything here is derived from public records.

## Start here

| File | What it is |
|---|---|
| `output/belmont_leads.html` | Phone-friendly browser for every lead: search, filter by class / owner type / property type, tap for map. Also published as a Claude artifact (link in the session). |
| `output/belmont_absentee_owner_lists.xlsx` | One workbook, 17 sheets (summary, every list below, data dictionary). Open on a phone or in Excel / Sheets. |
| `output/belmont_non_owner_occupied_all.csv` | Every improved residential property whose tax bill is mailed somewhere other than the property ({ls['Non-owner-occupied (all)']} rows). |
| `output/belmont_likely_inherited_absentee.csv` | Absentee properties with an estate / heirs / c-o / et-al / nominal-transfer signal ({ls['Likely inherited (absentee)']} rows). The "inherited house, family out of town" list. |
| `output/belmont_individuals_trusts_only.csv` | Non-owner-occupied excluding LLC / corporate landlords ({ls['Individuals & trusts only']} rows). |
| `output/belmont_out_of_state.csv` / `belmont_out_of_country.csv` | Tax bill goes out of Massachusetts ({ls['Out of state']}) or abroad ({ls['Out of country']}). |
| `output/belmont_elsewhere_in_ma.csv` / `belmont_elsewhere_in_belmont.csv` | Owner lives in another MA town ({ls['Elsewhere in MA']}) or elsewhere in Belmont ({ls['Elsewhere in Belmont']}, of which {oak} are condo units held by one LLC). |
| `output/belmont_estate_heirs_owned.csv` | Owner of record is an estate, heirs, executor / administrator, or the bill goes c/o someone ({ls['Estate & heirs owned']} rows). |
| `output/belmont_life_estate_watchlist.csv` | Owners holding a life estate ({ls['Life-estate watchlist']}): mostly owner-occupied today, pass to heirs at death. |
| `output/belmont_llc_corporate_owned.csv`, `belmont_trust_owned_absentee.csv` | Investor / trust ownership views. |
| `output/belmont_tax_delinquent_known.csv` | Parcels with a published tax taking on record ({ls['Tax delinquent (known)']} so far, see below). |
| `output/belmont_all_residential_scored.csv` | Master table: all {s['residential_records_total']} residential-class records with every flag, for your own filtering. |
| `templates/records_request_treasurer.md` | Ready-to-send public records request for the full tax-title / delinquent list, plus Registry of Deeds search steps. |
| `campaigns/life_estate/` | Outreach campaign for the {ls['Life-estate watchlist']} life-estate records: `mailing_list.csv` / `.xlsx` (one row per household), `skip_trace_export.csv` (to append phones and emails), `letters_life_estate.docx` (letter 1 merged, one page per household). |
| `campaigns/likely_inherited/`, `campaigns/estate_heirs/` | The same package for the likely-inherited and estate-owned lists. |
| `campaigns/templates/`, `campaigns/README.md` | Editable letter, postcard, email and phone-script copy, sender settings, mailing sequence, and the Massachusetts rules that apply. |

Every row carries a `priority_score` (higher = better lead), the owner mailing address (where the tax
bill goes), the deed book / page, assessed values, and a Google Maps link to the parcel.

## Headline numbers (fiscal 2024 extract)

| Measure | Count |
|---|---|
| Residential-class assessor records | {s['residential_records_total']} |
| Improved residential (houses, condos, 2-3 families, small apartments, mixed use), excluding town / church / institutional owners | {s['improved_residential_excluding_institutional']} |
| **Non-owner-occupied (tax bill mailed away from the property)** | **{s['non_owner_occupied']} ({pct:.1f}%)** |
| ... owner elsewhere in Belmont | {ls['Elsewhere in Belmont']} |
| ... owner elsewhere in Massachusetts (incl. PO boxes) | {ls['Elsewhere in MA']} |
| ... owner out of state (incl. PO boxes) | {ls['Out of state']} |
| ... owner out of the country | {ls['Out of country']} |
| Owner-occupied (bill goes to the property, incl. the other unit of the same 2-family) | {owner_occ} |
| Owner lives in the same condo building, different unit | {occ.get('owner in same building (different unit)', 0)} |
| PO Box in Belmont (occupancy unknown) | {occ.get('unknown - PO Box in Belmont', 0)} |
| Absentee owners that are individuals / trusts / life estates / estates (not LLCs) | {people} |
| Absentee owners that are LLCs / corporations | {ot.get('LLC / corporate', 0)} |
| Likely inherited or family-transferred, absentee | {ls['Likely inherited (absentee)']} |

Out-of-state mailing states among absentee owners: {states}.

## How "non-owner-occupied" is decided

Belmont has no residential exemption, so the assessor keeps no owner-occupancy flag. The industry
proxy, and the one used here, is **where the tax bill is mailed**: the owner's mailing address
(`OWN_ADDR / OWN_CITY / OWN_STATE / OWN_ZIP`) is parsed and compared with the property address.

* Street names are normalized (ROAD = RD, AVENUE = AVE, typos tolerated), unit designators are
  parsed (UNIT 2, APT 3, #1, U1, B5, STE 200), and house numbers are matched against the property's
  number range (owner at "18 Crescent Road" matches property "16-18 Crescent Rd").
* A two-family or condo listed under one number whose owner uses the other unit's number
  (48 vs 50 Grant Ave) counts as owner-occupied. An owner on the same street within a few numbers is
  still absentee but flagged `owner_next_door` (softer lead).
* Mailing city Belmont / Waverley or ZIP 02478-02479 = "elsewhere in Belmont"; other MA cities =
  "elsewhere in MA"; another US state = "out of state"; no US state and a country or province in the
  address = "out of country" (a valid US state always wins, so Jamaica Plain MA is not Jamaica).
* PO boxes cannot be resolved to a residence; Belmont PO boxes are "unknown", others are absentee.

## Inherited-property signals

The owner-name field uses Patriot-style codes after the surname, which are decoded into flags:

* `estate_or_heirs`: ESTATE OF, EST OF, HEIRS, DEVISEES, EXECUTOR, ADMINISTRATOR.
* `life_estate`: LE after the surname (owner keeps a life estate; heirs are the remaindermen).
* `trust`: TR, TRS, TRUSTEE, TRUST, NOMINEE (family estate planning or investor).
* `et_al_multiple_owners`: ET AL (several co-owners of record, often siblings).
* `care_of_mailing`: bill goes c/o a third party (executor, relative, manager).
* `last_sale_type` = nominal transfer when the last recorded price is $0-$100: a deed between family,
  into a trust, or out of an estate rather than a market sale. Combined with an absentee mailing
  address this is the best available proxy for "inherited and the family moved away".

`likely_inherited = YES` when a property is absentee (or estate-owned) and shows any of those signals.

## Tax delinquency: what is public and what is not

* Belmont **does not publish** a delinquent or tax-title list online. Its FAQ says to email the
  Treasurer / Collector for the list: treasurers@belmont-ma.gov, 617-993-2770, 19 Moore St.
  `templates/records_request_treasurer.md` is a ready-to-send Public Records Law request.
* What is published: the **Notice of Tax Taking** (https://www.belmont-ma.gov/2040/Notice-of-Tax-Taking).
  The most recent one covers a taking on **February 27, 2025** for **12 Midland St (parcel 30-15)**,
  owned by the *Estate of Helen P. Grant* (last transfer 1952, FY2024 assessed $1,013,000). It is the
  one record in `data/tax_delinquent_known.csv` and gets +10 priority in every list.
* Every completed taking is recorded at the Middlesex South Registry of Deeds
  (https://www.masslandrecords.com/MiddlesexSouth/) as an Instrument of Taking with the Town of
  Belmont as grantee. The template file explains how to search it; that search could not be run from
  this environment (the Registry site is not reachable from it).
* When the Treasurer's list arrives, drop it into `data/tax_delinquent_known.csv` (same columns) and
  re-run the pipeline; matching parcels are flagged and float to the top.

## Outreach campaigns (Campaign tab in the dashboard)

Owners at the same mailing address are combined into one household, names are parsed from the
assessor's coded format into a mailing name and salutation ("VASTIS LE NICHOLAS P & MARTHA" becomes
"Nicholas P. & Martha Vastis" / "Dear Nicholas and Martha Vastis,"), and unit numbers move to a second
address line for USPS. The dashboard's Campaign tab shows each household with a status (not contacted,
letter 1 sent, replied, interested, do not contact...), notes, a mailing-list export, and print-ready
letters merged from editable sender settings; statuses live in the artifact's shared database so phone
and desktop stay in sync. The assessor data carries no phone numbers or emails: run
`skip_trace_export.csv` through a skip-tracing service before any call or email campaign, and read
`campaigns/README.md` for the sequence and the rules (M.G.L. c. 93A, 254 CMR 3, TCPA / Do Not Call,
CAN-SPAM, elder-protection). A life-estate holder cannot sell without the remaindermen, so every
template invites the family in.

## Data vintage and verification

* MassGIS's Belmont file is fiscal 2024 (uploaded February 2024). MassGIS has FY2025-26 data for
  most towns, but Belmont has not submitted newer data; the pipeline picks up a newer vintage
  automatically when one appears.
* Ownership changes since then (sales, deaths, new trusts) are not reflected. Before outreach, check
  the parcel in Belmont's Real Estate Database (https://www.belmont-ma.gov/229/Real-Estate-Database)
  or the town's FY2025 public-disclosure listing, and pull the current deed with the book / page given.
* Assessed values are FY2024 (valuation date January 1, 2023).

## Re-running / refreshing

```bash
pip install -r belmont/pipeline/requirements.txt
python belmont/pipeline/fetch_massgis.py     # downloads the newest Belmont package from MassGIS
python belmont/pipeline/build_lists.py       # rebuilds every CSV, the workbook and summary.json
python belmont/pipeline/build_campaign.py    # rebuilds campaigns/ (mailing lists, letters) and output/campaigns.json
python belmont/pipeline/build_page.py        # rebuilds output/belmont_leads.html (leads + campaign tab)
python belmont/pipeline/write_readme.py      # refreshes the numbers in this README
```

`fetch_massgis.py --vintage CY23_FY23` pulls an older vintage out of the statewide aggregate with
HTTP range requests (no 6 GB download). Change `--town-id` / `--town` to run the same search for any
other Massachusetts municipality (MassGIS town IDs: Arlington 10, Watertown 314, Waltham 308,
Lexington 155, Cambridge 49).

## Sources

* MassGIS Level 3 standardized assessors' parcels, town 026: `https://s3.amazonaws.com/download.massgis.digital.mass.gov/shapefiles/l3parcels/L3_SHP_M026_BELMONT.zip`
* Town of Belmont: Notice of Tax Taking, Tax Bills & Collections FAQ, Treasurer / Collector, Assessor's Office, Real Estate Database (belmont-ma.gov).
* Massachusetts General Laws c. 60 (tax collection, takings), c. 66 s. 10 (public records).
"""
open(os.path.join(ROOT, "README.md"), "w").write(readme)
print("README.md written")
