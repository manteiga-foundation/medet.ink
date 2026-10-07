"""Slide layout after the cover: the logo lives in the footer, titles start high."""
from __future__ import annotations

import unittest

from harness import REPORT_FOLDER, Chromium, TOLERANCE_PX, archetypes, slide_number

TITLE_TOP = 14.4  # 0.15in from the top of the slide, as slide 09's card
COVER = '01'

PROBE = r"""() => {
  const slide = document.querySelector('.slide').getBoundingClientRect();
  const box = el => { const r = el.getBoundingClientRect();
    return { top: r.top - slide.top, left: r.left - slide.left, middle: r.top - slide.top + r.height / 2 }; };
  const title = document.querySelector('.section-title');
  const footerLogos = [...document.querySelectorAll('.footer .footer-bottom-row > .footer-logo')];
  const line = document.querySelector('.footer .footer-line');
  const footerText = document.querySelector('.footer .confidential-block');
  const placeholders = [...document.querySelectorAll('.slide *')]
    .filter(el => el.children.length === 0 && el.textContent.includes('[ACME Logo]') && !el.closest('.footer'))
    .map(el => Math.round(box(el).top));
  return {
    title: title ? box(title).top : null,
    logos: footerLogos.map(box), line: line ? box(line) : null, footerText: footerText ? box(footerText) : null,
    placeholders,
  };
}"""


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chromium = Chromium()
        cls.layout = {}
        try:
            for path in archetypes():
                opened = chromium.open(f'archetypes/{path.name}')
                try:
                    cls.layout[slide_number(path)] = opened.page.evaluate(PROBE)
                finally:
                    opened.close()
        finally:
            chromium.close()

    def slides(self):
        return {n: v for n, v in self.layout.items() if n != COVER}

    def test_titles_start_at_the_same_height(self):
        titled = {n: v['title'] for n, v in self.slides().items() if v['title'] is not None}
        if not REPORT_FOLDER:  # proves the probe found the sample's content; a report may hold none
            self.assertGreater(len(titled), 10)
        for number, top in titled.items():
            with self.subTest(archetype=number):
                self.assertAlmostEqual(top, TITLE_TOP, delta=TOLERANCE_PX)

    def test_the_logo_sits_in_the_footer_beside_the_brand_line(self):
        for number, v in self.slides().items():
            with self.subTest(archetype=number):
                self.assertEqual(len(v['logos']), 1, 'one .footer-logo in the footer bottom row')
                logo = v['logos'][0]
                self.assertAlmostEqual(logo['middle'], v['line']['middle'], delta=1, msg='centred on the brand line')
                self.assertAlmostEqual(logo['left'], v['footerText']['left'], delta=1, msg='aligned with the footer text')

    def test_no_logo_above_the_footer(self):
        for number, v in self.slides().items():
            with self.subTest(archetype=number):
                self.assertEqual(v['placeholders'], [])


if __name__ == '__main__':
    unittest.main()
