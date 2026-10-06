"""Shared harness for the template's tests.

The repository is served over HTTP on a free port, so relative links and CDN scripts behave as
they do on medet.ink, and it is driven by a real headless Chromium. Tests measure the rendered
DOM (geometry, chart state, print pagination) rather than judging screenshots.

MEDET_ROOT points the harness at another copy of the repository. That is how a test written for
behaviour that already exists is shown to fail against a deliberate break without touching the
working tree (see AGENTS.md, "How we work").
"""
from __future__ import annotations

import hashlib
import http.server
import io
import json
import os
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import Page, Route, sync_playwright
from pypdf import PdfReader

ROOT = Path(os.environ.get('MEDET_ROOT') or Path(__file__).resolve().parent.parent)

# Third-party files (chart libraries, fonts, placeholder images) are fetched once and served
# from here afterwards, so a run does not depend on a CDN's mood. Delete the folder to refresh.
CACHE = Path(__file__).resolve().parent / '.cache'
# code.highcharts.com refuses headless browsers (403) and rate-limits repeated runs (429). The
# same release is published on npm, which jsDelivr mirrors under the same paths.
MIRRORS = {'https://code.highcharts.com/': 'https://cdn.jsdelivr.net/npm/highcharts/'}

SLIDE_PX = (1056, 816)  # 11in x 8.5in at 96 CSS px per inch
PAGE_PT = (792, 612)    # the same page in PDF points (72 per inch)
TOLERANCE_PX = 2        # sub-pixel rounding allowed by the overflow probe

# Every slide in the document: its size, how far its content reaches past its own box, and its
# charts: painted pixels per canvas (a canvas keeps a 300x150 default when no library draws on it)
# and series per Highcharts container.
SLIDE_PROBE = """() => [...document.querySelectorAll('.slide')].map(s => ({
  width: s.clientWidth,
  height: s.clientHeight,
  overflow: Math.max(s.scrollHeight - s.clientHeight, s.scrollWidth - s.clientWidth),
  canvases: [...s.querySelectorAll('canvas')].map(c => {
    const g = c.width && c.height && c.getContext('2d');
    if (!g) return 0;
    const px = g.getImageData(0, 0, c.width, c.height).data;
    let painted = 0;
    for (let i = 3; i < px.length; i += 16) if (px[i]) painted++;
    return painted;
  }),
  highcharts: [...s.querySelectorAll('.highcharts-container')].map(c => c.querySelectorAll('.highcharts-series').length)
}))"""


def archetypes() -> list[Path]:
    """The archetype files, in slide order (the pattern the build scripts glob)."""
    return sorted(ROOT.glob('archetypes/[0-9][0-9]-Slide-*.html'))


def chart_calls(path: Path) -> int:
    """How many charts an archetype's own script creates, counted in its source."""
    source = path.read_text(encoding='utf-8')
    return source.count('Highcharts.chart(') + source.count('new Chart(')


def chart_signature(slide: dict) -> tuple:
    """What a slide's charts look like once drawn: canvases painted, series per Highcharts chart."""
    return [painted > 0 for painted in slide['canvases']], slide['highcharts']


def slide_number(path: Path) -> str:
    return path.name[:2]


def pdf_pages(pdf: bytes) -> list[tuple[int, int]]:
    """Width and height in points of every page of a PDF."""
    reader = PdfReader(io.BytesIO(pdf))
    return [(round(float(p.mediabox.width)), round(float(p.mediabox.height))) for p in reader.pages]


def _serve_third_party(route: Route) -> None:
    """Answers a request for a file outside the repository from the cache, filling it once."""
    url = route.request.url
    key = hashlib.sha256(url.encode()).hexdigest()[:32]
    body_file, meta_file = CACHE / key, CACHE / f'{key}.json'
    if not meta_file.exists():
        candidates = [url] + [mirror + url[len(prefix):] for prefix, mirror in MIRRORS.items()
                              if url.startswith(prefix)]
        for candidate in candidates:
            try:
                response = route.fetch(url=candidate)
            except Exception:
                continue
            if response.ok:
                CACHE.mkdir(exist_ok=True)
                body_file.write_bytes(response.body())
                meta_file.write_text(json.dumps({
                    'url': url, 'from': candidate,
                    'content-type': response.headers.get('content-type', 'application/octet-stream')}))
                break
        else:
            route.continue_()  # unreachable everywhere: let it fail as it would for a reader
            return
    meta = json.loads(meta_file.read_text())
    route.fulfill(status=200, body=body_file.read_bytes(), headers={
        'content-type': meta['content-type'], 'access-control-allow-origin': '*'})


class _Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        pass


class Site:
    """The repository over HTTP on 127.0.0.1 and a free port."""

    def __init__(self):
        self._httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), _Handler)
        self._httpd.daemon_threads = True
        self.url = f'http://127.0.0.1:{self._httpd.server_address[1]}'
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()

    def close(self):
        self._httpd.shutdown()
        self._httpd.server_close()


class Opened:
    """A page loaded by Chromium, with the uncaught errors it threw."""

    def __init__(self, page: Page, errors: list[str]):
        self.page = page
        self.errors = errors

    def slides(self) -> list[dict]:
        return self.page.evaluate(SLIDE_PROBE)

    def pdf(self) -> bytes:
        return self.page.pdf(prefer_css_page_size=True, print_background=True)

    def close(self):
        self.page.context.close()


class Chromium:
    """The site served and a headless Chromium that presents a regular Chrome user agent."""

    def __init__(self):
        self.site = Site()
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(
            headless=True, args=['--use-gl=egl', '--ignore-gpu-blocklist'])
        # code.highcharts.com answers 403 to a HeadlessChrome user agent, which leaves every
        # Highcharts slide blank. Readers open the template in a regular Chrome; so do the tests.
        self.user_agent = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
            f'(KHTML, like Gecko) Chrome/{self.browser.version} Safari/537.36')

    def open(self, path: str, viewport: tuple[int, int] = SLIDE_PX) -> Opened:
        context = self.browser.new_context(
            viewport={'width': viewport[0], 'height': viewport[1]}, user_agent=self.user_agent)
        local = self.site.url + '/'
        context.route(lambda url: url.startswith('http') and not url.startswith(local), _serve_third_party)
        page = context.new_page()
        errors: list[str] = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(f'{self.site.url}/{path}', wait_until='networkidle')
        # Web fonts change line breaks, and line breaks decide overflow: measure after they load.
        page.evaluate('document.fonts.ready.then(() => true)')
        return Opened(page, errors)

    def close(self):
        self.browser.close()
        self._playwright.stop()
        self.site.close()
