"""The landing page: its own HTML, CSS and script, wording for every kind of report, a slideshow of
the archetypes in the hero, the template download, and a sound layout at every review size."""
from __future__ import annotations

import re
import unittest

from harness import ROOT, Chromium, archetypes
from test_links import references

REVIEW_SIZES = [(1440, 900), (1280, 800), (390, 844)]
# The template serves any report or presentation; the sample content is a security assessment.
NARROW_WORDS = re.compile(r'cyber|pentest|penetration', re.I)
TEMPLATE_ZIP = 'reports/medet-ink-template.zip'

PAGE_STATE = r"""async () => {
  // Lazy images load when scrolled to: scroll through the page, then wait for every image.
  for (let y = 0; y < document.documentElement.scrollHeight; y += 400) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 30));
  }
  window.scrollTo(0, 0);
  await Promise.all([...document.images].filter(i => i.getAttribute('src'))
    .map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  return {
    overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    brokenImages: [...document.images].filter(i => i.getAttribute('src') && !i.naturalWidth).map(i => i.getAttribute('src')),
  };
}"""

# What the slideshow shows: the page indicator, the active slide and tick, and whether it plays.
SHOW_STATE = r"""async () => {
  const show = document.querySelector('[data-slideshow]');
  const slides = [...show.querySelectorAll('[data-slide]')];
  const active = slides.filter(s => s.classList.contains('is-active'));
  const img = active[0] && active[0].querySelector('img');
  if (img && img.getAttribute('src') && !img.complete) await new Promise(r => { img.onload = img.onerror = r; });
  const box = img ? img.getBoundingClientRect() : {width: 0, height: 0};
  return {
    page: show.querySelector('[data-page]').textContent.trim(),
    total: show.querySelector('[data-total]').textContent.trim(),
    name: show.querySelector('[data-name]').textContent.trim(),
    state: show.dataset.state,
    active: active.map(s => s.getAttribute('href')),
    hiddenFromReaders: slides.filter(s => s.getAttribute('aria-hidden') === 'true').length,
    currentTicks: [...show.querySelectorAll('[data-go]')].filter(t => t.getAttribute('aria-current') === 'true')
      .map(t => t.dataset.go),
    imageShown: !!img && img.naturalWidth > 0 && box.width > 200 && box.height > 150,
  };
}"""


def slideshow_entries(source: str) -> list[tuple[str, str]]:
    """(archetype file, thumbnail number) for each slide of the hero slideshow, in markup order."""
    block = re.search(r'<div[^>]*data-slideshow[^>]*>(.*?)<!-- /slideshow -->', source, re.S)
    if not block:
        return []
    return re.findall(r'<a href="archetypes/([^"]+)"[^>]*data-slide[^>]*>\s*<img (?:src|data-src)="assets/slide_(\d{2})\.png"',
                      block.group(1))


class LandingPageTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'index.html').read_text(encoding='utf-8')

    def test_landing_page_loads_no_external_script(self):
        self.assertEqual(re.findall(r'<script\b[^>]*\bsrc=[^>]*>', self.source), [],
                         'no framework or CDN script: the page carries its own')

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

    def test_the_hero_shows_every_archetype_in_report_order_instead_of_a_gif(self):
        expected = [(path.name, path.name[:2]) for path in archetypes()]
        self.assertEqual(slideshow_entries(self.source), expected)
        self.assertNotIn('demo.gif', self.source)

    def test_the_slideshow_pages_with_its_controls(self):
        chromium = Chromium()
        try:
            # Reduced motion: the slideshow waits for the visitor, so only the controls move it.
            opened = chromium.open('index.html', viewport=(1440, 900),
                                   before_load=lambda page: page.emulate_media(reduced_motion='reduce'))
            page, state = opened.page, lambda: opened.page.evaluate(SHOW_STATE)
            first = state()
            self.assertEqual((first['page'], first['total'], first['state']), ('01', '16', 'paused'))
            self.assertEqual(first['active'], ['archetypes/01-Slide-Cover.html'])
            self.assertEqual((first['currentTicks'], first['hiddenFromReaders']), (['1'], 15))
            self.assertTrue(first['imageShown'])
            page.click('[data-next]')
            self.assertEqual(state()['page'], '02')
            page.click('[data-prev]')
            page.click('[data-prev]')
            wrapped = state()
            self.assertEqual((wrapped['page'], wrapped['active']), ('16', ['archetypes/16-Slide-Company-Overview.html']))
            page.click('[data-go="8"]')
            jumped = state()
            self.assertEqual((jumped['page'], jumped['name'], jumped['currentTicks']), ('08', 'Findings Overview', ['8']))
            page.keyboard.press('ArrowRight')
            moved = state()
            self.assertEqual((moved['page'], moved['active']), ('09', ['archetypes/09-Slide-Technical-Details.html']))
            self.assertTrue(moved['imageShown'], 'the slide image is fetched before it is shown')
            self.assertEqual(opened.errors, [])
            opened.close()
        finally:
            chromium.close()

    def test_the_slideshow_plays_by_itself_and_pauses_for_the_visitor(self):
        chromium = Chromium()
        try:
            opened = chromium.open('index.html', viewport=(1440, 900), before_load=lambda page: page.clock.install())
            page, state = opened.page, lambda: opened.page.evaluate(SHOW_STATE)
            interval = int(page.get_attribute('[data-slideshow]', 'data-interval'))
            self.assertEqual((state()['page'], state()['state']), ('01', 'playing'))
            page.clock.run_for(interval + 300)
            self.assertEqual(state()['page'], '02', 'advances after one interval')
            page.hover('[data-slideshow] .stage')
            page.clock.run_for(interval * 3)
            self.assertEqual((state()['page'], state()['state']), ('02', 'paused'), 'holds while pointed at')
            page.mouse.move(5, 5)
            page.clock.run_for(interval + 300)
            self.assertEqual((state()['page'], state()['state']), ('03', 'playing'), 'resumes when the pointer leaves')
            page.click('[data-toggle]')
            page.mouse.move(5, 5)
            page.clock.run_for(interval * 3)
            self.assertEqual((state()['page'], state()['state']), ('03', 'paused'), 'the pause key holds it')
            self.assertEqual(opened.errors, [])
            opened.close()
        finally:
            chromium.close()

    def test_the_html_template_can_be_downloaded(self):
        links = re.findall(r'<a\b[^>]*href="' + re.escape(TEMPLATE_ZIP) + r'"[^>]*>(.*?)</a>', self.source, re.S)
        self.assertEqual(len(links), 1, f'one link to {TEMPLATE_ZIP}')
        self.assertIn('HTML', links[0])
        self.assertRegex(re.search(r'<a\b[^>]*href="' + re.escape(TEMPLATE_ZIP) + r'"[^>]*>', self.source).group(0),
                         r'\bdownload\b')

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
