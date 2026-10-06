"""Shared harness for the template's tests.

The repository is served over HTTP on a free port, so relative links and CDN scripts behave as
they do on medet.ink, and it is driven by a real headless Chromium. Tests measure the rendered
DOM (geometry, chart state, print pagination) rather than judging screenshots.

MEDET_ROOT points the harness at another copy of the repository. That is how a test written for
behaviour that already exists is shown to fail against a deliberate break without touching the
working tree (see AGENTS.md, "How we work").
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import Page, Route, sync_playwright
from pypdf import PdfReader

# The browser setup the maintainer scripts use (user agent, animations off, the local server),
# taken from this checkout's scripts/ even when MEDET_ROOT points the tests at another copy.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from browser import CHROMIUM_ARGS, NO_ANIMATIONS, chrome_user_agent, serve  # noqa: E402

ROOT = Path(os.environ.get('MEDET_ROOT') or Path(__file__).resolve().parent.parent)

# Third-party files (chart libraries, fonts, placeholder images) are fetched once and served
# from here afterwards, so a run does not depend on a CDN's mood. Delete the folder to refresh.
CACHE = Path(__file__).resolve().parent / '.cache'

SLIDE_PX = (1056, 816)  # 11in x 8.5in at 96 CSS px per inch
PAGE_PT = (792, 612)    # the same page in PDF points (72 per inch)
TOLERANCE_PX = 2        # sub-pixel rounding allowed by the overflow probe
TOLERANCE_IMAGE = 0.1   # percent of pixels allowed to differ between two renders of one page

# Every slide in the document: its size, how far its content reaches past its own box, and its
# charts: painted pixels per canvas (a canvas keeps a 300x150 default when no library draws on it)
# and shapes per inline SVG chart (`data-chart` containers).
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
  svg: [...s.querySelectorAll('[data-chart]')].map(c => c.querySelectorAll('svg path, svg polygon, svg circle, svg rect').length)
}))"""


def archetypes() -> list[Path]:
    """The archetype files, in slide order (the pattern the build scripts glob)."""
    return sorted(ROOT.glob('archetypes/[0-9][0-9]-Slide-*.html'))


def chart_calls(path: Path) -> int:
    """How many charts an archetype's own script creates, counted in its source."""
    source = path.read_text(encoding='utf-8')
    containers = len(re.findall(r'<[a-z]+\b[^>]*\sdata-chart="', source))  # inline SVG charts
    return source.count('new Chart(') + containers


def chart_signature(slide: dict) -> tuple:
    """What a slide's charts look like once drawn: canvases painted, shapes per SVG chart."""
    return [painted > 0 for painted in slide['canvases']], slide['svg']


def slide_number(path: Path) -> str:
    return path.name[:2]


def pdf_pages(pdf: bytes) -> list[tuple[int, int]]:
    """Width and height in points of every page of a PDF."""
    reader = PdfReader(io.BytesIO(pdf))
    return [(round(float(p.mediabox.width)), round(float(p.mediabox.height))) for p in reader.pages]


def pdf_texts(pdf: bytes) -> list[str]:
    """The text layer of every page, whitespace collapsed (chart labels drawn as SVG are text)."""
    return [' '.join((p.extract_text() or '').split()) for p in PdfReader(io.BytesIO(pdf)).pages]


def image_difference(png_a: bytes, png_b: bytes) -> float:
    """Percent of pixels that differ visibly (a channel off by more than 32 of 255)."""
    a = Image.open(io.BytesIO(png_a)).convert('RGB')
    b = Image.open(io.BytesIO(png_b)).convert('RGB')
    if a.size != b.size:
        return 100.0
    histogram = ImageChops.difference(a, b).convert('L').histogram()
    return 100.0 * sum(histogram[33:]) / (a.size[0] * a.size[1])


def _serve_third_party(route: Route) -> None:
    """Answers a request for a file outside the repository from the cache, filling it once."""
    url = route.request.url
    key = hashlib.sha256(url.encode()).hexdigest()[:32]
    body_file, meta_file = CACHE / key, CACHE / f'{key}.json'
    if not meta_file.exists():
        try:
            response = route.fetch()
        except Exception:
            response = None
        if response is None or not response.ok:
            route.continue_()  # unreachable: let it fail as it would for a reader
            return
        CACHE.mkdir(exist_ok=True)
        body_file.write_bytes(response.body())
        meta_file.write_text(json.dumps({
            'url': url,
            'content-type': response.headers.get('content-type', 'application/octet-stream')}))
    meta = json.loads(meta_file.read_text())
    route.fulfill(status=200, body=body_file.read_bytes(), headers={
        'content-type': meta['content-type'], 'access-control-allow-origin': '*'})


class Opened:
    """A page loaded by Chromium, with the uncaught errors it threw."""

    def __init__(self, page: Page, errors: list[str]):
        self.page = page
        self.errors = errors

    def slides(self) -> list[dict]:
        return self.page.evaluate(SLIDE_PROBE)

    def pdf(self) -> bytes:
        return self.page.pdf(prefer_css_page_size=True, print_background=True)

    def screenshot(self) -> bytes:
        return self.page.screenshot()

    def slide_screenshots(self) -> list[bytes]:
        """Each .slide exactly, wherever the page places it on screen."""
        slides = self.page.locator('.slide')
        return [slides.nth(i).screenshot() for i in range(slides.count())]

    def close(self):
        self.page.context.close()


class Chromium:
    """The site served and a headless Chromium set up as the maintainer scripts set it up."""

    def __init__(self):
        self._resources = contextlib.ExitStack()
        self.url = self._resources.enter_context(serve(ROOT))
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        self.user_agent = chrome_user_agent(self.browser)

    def open(self, path: str, viewport: tuple[int, int] = SLIDE_PX, hold_fonts: bool = False,
             before_load=None) -> Opened:
        """Loads a page. With hold_fonts, web font files arrive only after the page's scripts ran.
        before_load(page) runs before navigation, e.g. page.clock.install() to drive timers."""
        context = self.browser.new_context(
            viewport={'width': viewport[0], 'height': viewport[1]}, user_agent=self.user_agent)
        local = self.url + '/'
        held: list[Route] = []
        context.route(lambda url: url.startswith('http') and not url.startswith(local), _serve_third_party)
        if hold_fonts:
            context.route('https://fonts.gstatic.com/**', lambda route: held.append(route))
        page = context.new_page()
        page.add_init_script(NO_ANIMATIONS)
        if before_load:
            before_load(page)
        errors: list[str] = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        if hold_fonts:
            # The load event would wait for the held fonts; the page's scripts have run by now.
            page.goto(f'{self.url}/{path}', wait_until='domcontentloaded')
            page.wait_for_timeout(300)
            for route in held:
                _serve_third_party(route)
            page.wait_for_load_state('networkidle')
        else:
            page.goto(f'{self.url}/{path}', wait_until='networkidle')
        # Web fonts change line breaks, and line breaks decide overflow: measure after they load.
        page.evaluate('document.fonts.ready.then(() => true)')
        return Opened(page, errors)

    def close(self):
        self.browser.close()
        self._playwright.stop()
        self._resources.close()
