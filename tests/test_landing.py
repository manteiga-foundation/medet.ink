"""The landing page: plain HTML and CSS, wording for every kind of report, sound at every review size."""
from __future__ import annotations

import re
import unittest

from harness import ROOT, Chromium
from test_links import references

REVIEW_SIZES = [(1440, 900), (1280, 800), (390, 844)]
# The template serves any report or presentation; the sample content is a security assessment.
NARROW_WORDS = re.compile(r'cyber|pentest|penetration', re.I)

PAGE_STATE = r"""async () => {
  // Lazy images load when scrolled to: scroll through the page, then wait for every image.
  for (let y = 0; y < document.documentElement.scrollHeight; y += 400) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 30));
  }
  window.scrollTo(0, 0);
  await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  return {
    overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    brokenImages: [...document.images].filter(i => !i.naturalWidth).map(i => i.getAttribute('src')),
  };
}"""


class LandingPageTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'index.html').read_text(encoding='utf-8')

    def test_landing_page_loads_no_script(self):
        self.assertEqual(re.findall(r'<script\b[^>]*>', self.source), [], 'the page is plain HTML and CSS')

    def test_headline_and_titles_are_not_limited_to_cybersecurity(self):
        meta = references('index.html').meta
        texts = {
            'title': re.search(r'<title>(.*?)</title>', self.source, re.S).group(1),
            'h1': re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', self.source, re.S).group(1)),
            'og:title': meta.get('og:title', ''),
            'twitter:title': meta.get('twitter:title', ''),
        }
        for where, text in texts.items():
            with self.subTest(where=where):
                self.assertIsNone(NARROW_WORDS.search(text), text)

    def test_landing_page_holds_together_at_every_review_size(self):
        chromium = Chromium()
        try:
            for width, height in REVIEW_SIZES:
                opened = chromium.open('index.html', viewport=(width, height))
                state = opened.page.evaluate(PAGE_STATE)
                errors = opened.errors
                opened.close()
                with self.subTest(size=f'{width}x{height}'):
                    self.assertEqual(state['overflowX'], 0, 'the page scrolls sideways')
                    self.assertEqual(state['brokenImages'], [])
                    self.assertEqual(errors, [])
        finally:
            chromium.close()


if __name__ == '__main__':
    unittest.main()
