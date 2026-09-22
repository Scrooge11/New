"""Read members of a very large remote zip over HTTP range requests (no full download).

MassGIS publishes a 6+ GB statewide aggregate of every town's parcel data. Only the
central directory and the members you ask for are transferred.
"""
import io
import os
import ssl
import sys
import zipfile
import urllib.request


class HttpRangeFile(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos, self.nreq = url, 0, 0
        cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("CURL_CA_BUNDLE")
        self.ctx = ssl.create_default_context(cafile=cafile)
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=60, context=self.ctx) as r:
            self.size = int(r.headers["Content-Length"])

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n <= 0 or self.pos >= self.size:
            return b""
        end = min(self.size - 1, self.pos + n - 1)
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        with urllib.request.urlopen(req, timeout=300, context=self.ctx) as r:
            data = r.read()
        self.nreq += 1
        self.pos += len(data)
        return data

    def readinto(self, b):
        d = self.read(len(b))
        b[: len(d)] = d
        return len(d)


def open_remote_zip(url):
    f = HttpRangeFile(url)
    return zipfile.ZipFile(io.BufferedReader(f, buffer_size=1 << 20)), f


def extract_matching(url, pattern, outdir):
    """Extract every member whose path contains `pattern` (case-insensitive) into outdir."""
    zf, f = open_remote_zip(url)
    hits = [i for i in zf.infolist() if pattern.lower() in i.filename.lower() and not i.is_dir()]
    os.makedirs(outdir, exist_ok=True)
    out = []
    for i in hits:
        dest = os.path.join(outdir, os.path.basename(i.filename))
        with zf.open(i) as src, open(dest, "wb") as dst:
            while True:
                chunk = src.read(8 << 20)
                if not chunk:
                    break
                dst.write(chunk)
        out.append(dest)
    return out, f.nreq


if __name__ == "__main__":
    url, pattern = sys.argv[1], sys.argv[2]
    zf, f = open_remote_zip(url)
    print(f"remote size {f.size/1e9:.2f} GB; {len(zf.infolist())} members")
    for i in zf.infolist():
        if pattern.lower() in i.filename.lower():
            print(f"{i.date_time} {i.file_size/1e6:9.2f} MB  {i.filename}")
    if len(sys.argv) > 3:
        files, n = extract_matching(url, pattern, sys.argv[3])
        print(f"extracted {len(files)} files with {n} range requests")
