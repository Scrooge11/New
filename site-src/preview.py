"""Preview the JEMCO site on this computer.

    python3 site-src/preview.py            (Windows: py site-src\\preview.py)

Rebuilds the pages from gen_site.py, serves the site/ folder at http://localhost:8080 and
opens it in the browser. Leave it running while you work:

  - edit gen_site.py and the pages are rebuilt on the next page load
  - edit site/css/styles.css or site/js/*.js and a refresh shows the change

It behaves like the live host where that matters: the security headers from netlify.toml are
sent (so anything the live site would block is blocked here too), a wrong address gets
404.html, and a submitted quote form lands on thanks.html. Submissions go nowhere; the
fields are printed in this window instead.

Needs Python 3.9 or newer and nothing else. Options: --port 8081, --no-open.
"""
import argparse, fnmatch, os, subprocess, sys, threading, urllib.parse, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'site')
GENERATOR = os.path.join(HERE, 'gen_site.py')
NETLIFY = os.path.join(ROOT, 'netlify.toml')

_built_from = None
_build_lock = threading.Lock()

# Windows takes file types from its registry, where .js is sometimes "text/plain". With the
# nosniff header the browser would then refuse to run the scripts, so the types are fixed here.
TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
         '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2',
         '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8', '.webmanifest': 'application/manifest+json'}
# Sent by the live host but meaningless (HSTS) or unhelpful (long caching) on a local preview.
SKIP_HEADERS = {'cache-control', 'strict-transport-security'}


def say(text):
    print(text, flush=True)


def rebuild_if_changed():
    """Run the generator when gen_site.py is newer than the last build."""
    global _built_from
    with _build_lock:
        stamp = os.path.getmtime(GENERATOR)
        if stamp == _built_from:
            return
        _built_from = stamp
        result = subprocess.run([sys.executable, GENERATOR, SITE], capture_output=True, text=True)
        if result.returncode != 0:
            say('\ngen_site.py failed, so the pages were not rebuilt:\n' + result.stderr.strip() + '\n')
            return
        notes = result.stdout.split('\nNot ready to launch:')
        say('Pages rebuilt from gen_site.py.' + ('\nNot ready to launch:' + notes[1].rstrip() if len(notes) > 1 else ''))


def header_rules():
    """The [[headers]] blocks of netlify.toml as [(path pattern, {header: value})].
    Reads only the simple layout this project uses, so it works without a TOML library."""
    rules, current = [], None
    try:
        lines = open(NETLIFY, encoding='utf-8').read().splitlines()
    except OSError:
        return rules
    for line in lines:
        line = line.strip()
        if line == '[[headers]]':
            current = {'for': None, 'values': {}}
            rules.append(current)
        elif line.startswith('[') and line != '[headers.values]':
            current = None
        elif current is not None and '=' in line and not line.startswith('#'):
            key, value = [part.strip() for part in line.split('=', 1)]
            value = value.strip('"')
            if key == 'for':
                current['for'] = value
            else:
                current['values'][key] = value
    return [(r['for'], r['values']) for r in rules if r['for']]


class Handler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map, **TYPES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE, **kwargs)

    def end_headers(self):
        path = urllib.parse.urlsplit(self.path).path
        for pattern, values in header_rules():
            if fnmatch.fnmatch(path, pattern):
                for key, value in values.items():
                    if key.lower() not in SKIP_HEADERS:
                        self.send_header(key, value)
        # Never cache locally, so an edit always shows on refresh.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def is_page(self):
        path = urllib.parse.urlsplit(self.path).path
        return path.endswith('/') or path.endswith('.html')

    def do_GET(self):
        if self.is_page():
            rebuild_if_changed()
        super().do_GET()

    def send_page(self, name, status):
        with open(os.path.join(SITE, name), 'rb') as f:
            body = f.read()
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.isfile(os.path.join(SITE, '404.html')):
            self.send_page('404.html', 404)
        else:
            super().send_error(code, message, explain)

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        fields = urllib.parse.parse_qsl(self.rfile.read(length).decode('utf-8', 'replace'), keep_blank_values=True)
        say('\nQuote form submitted (preview only, nothing was sent):')
        for key, value in fields:
            say('  %-14s %s' % (key, value))
        self.send_page('thanks.html', 200)

    def log_message(self, fmt, *args):
        # Keep the window quiet: only problems are worth a line.
        if len(args) > 1 and str(args[1]).startswith(('4', '5')):
            super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser(description='Preview the JEMCO site locally.')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--no-open', action='store_true', help='do not open the browser')
    args = parser.parse_args()

    rebuild_if_changed()
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError:
        sys.exit('Port %d is already in use. Try: python3 site-src/preview.py --port %d' % (args.port, args.port + 1))
    url = 'http://localhost:%d/' % args.port
    say('\nJEMCO site preview: %s\nPress Ctrl+C to stop.\n' % url)
    if not args.no_open:
        threading.Timer(0.4, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        say('\nStopped.')


if __name__ == '__main__':
    main()
