#!/usr/bin/env python3
"""Download the MassGIS Level 3 standardized assessor parcel package for a Massachusetts town.

Default: Belmont (MassGIS town id 26). The per-town zip is served from MassGIS's public
S3 bucket. `--vintage` pulls a specific fiscal-year folder (e.g. CY24_FY24) out of the
statewide aggregate using HTTP range requests instead of downloading 6+ GB.

Usage:
    python fetch_massgis.py                      # newest per-town zip -> ../data/raw/
    python fetch_massgis.py --vintage CY23_FY23  # older vintage from the aggregate
"""
import argparse
import os
import ssl
import sys
import urllib.request
import zipfile

BUCKET = "https://s3.amazonaws.com/download.massgis.digital.mass.gov"
TOWN_ZIP = BUCKET + "/shapefiles/l3parcels/L3_SHP_M{town_id:03d}_{town}.zip"
AGGREGATE = BUCKET + "/shapefiles/l3parcels/L3_AGGREGATE_SHP_20250101.zip"

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "..", "data", "raw")


def download(url, dest):
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("CURL_CA_BUNDLE")
    ctx = ssl.create_default_context(cafile=cafile)
    print(f"downloading {url}")
    with urllib.request.urlopen(url, timeout=600, context=ctx) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(4 << 20)
            if not chunk:
                break
            f.write(chunk)
    print(f"saved {dest} ({os.path.getsize(dest)/1e6:.1f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--town-id", type=int, default=26)
    ap.add_argument("--town", default="BELMONT")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--vintage", help="e.g. CY24_FY24: pull that vintage from the statewide aggregate")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    if args.vintage:
        sys.path.insert(0, HERE)
        from remote_zip import extract_matching

        folder = f"L3_SHP_M{args.town_id:03d}_{args.town.title()}_{args.vintage}"
        dest = os.path.join(args.out, folder)
        files, n = extract_matching(AGGREGATE, folder + "/", dest)
        print(f"extracted {len(files)} files to {dest} using {n} range requests")
        return

    url = TOWN_ZIP.format(town_id=args.town_id, town=args.town.upper())
    zpath = os.path.join(args.out, os.path.basename(url))
    download(url, zpath)
    with zipfile.ZipFile(zpath) as zf:
        zf.extractall(args.out)
        names = [n for n in zf.namelist() if n.lower().endswith("assess") or "Assess" in n]
    print("assessor tables:", [n for n in names if n.endswith(".dbf")])


if __name__ == "__main__":
    main()
