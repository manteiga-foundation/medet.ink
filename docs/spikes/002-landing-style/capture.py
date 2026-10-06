"""Captures the spike 002 options at the landing page's review sizes and checks them.

Run from the repository root after build.py: python3 docs/spikes/002-landing-style/capture.py
Writes shot-<option>-1440.png and shot-<option>-390.png (the first screen) for index.html.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tests'))
from harness import Chromium  # noqa: E402

SIZES = [(1440, 900), (1280, 800), (390, 844)]
CHECK = """() => ({
  overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  brokenImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src')),
  fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v, i, a) => a.indexOf(v) === i),
  height: document.documentElement.scrollHeight,
})"""

chromium = Chromium()
report = {}
for option in ('option-a', 'option-b', 'option-c'):
    path = f'docs/spikes/002-landing-style/{option}.html'
    for width, height in SIZES:
        opened = chromium.open(path, viewport=(width, height))
        page = opened.page
        # Lazy images load when scrolled to: scroll through the page, then wait for every image.
        page.evaluate("async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 30)); } window.scrollTo(0, 0); }")
        page.evaluate("() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })))")
        page.wait_for_timeout(400)
        result = page.evaluate(CHECK)
        result['errors'] = opened.errors
        report[f'{option} {width}'] = result
        if width != 1280:  # the comparison page shows 1440 and 390; 1280 is checked, not pictured
            page.screenshot(path=str(HERE / f'shot-{option}-{width}.png'))
        opened.close()
chromium.close()
print(json.dumps(report, indent=1))
