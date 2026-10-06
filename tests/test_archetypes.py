"""Every archetype, rendered in Chromium: one landscape Letter page that holds its content."""
from __future__ import annotations

import unittest

from harness import (PAGE_PT, SLIDE_PX, TOLERANCE_IMAGE, TOLERANCE_PX, ROOT, Chromium, archetypes, chart_calls,
                     image_difference, pdf_pages, slide_number)

class ArchetypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()
        cls.rendered = {}
        for path in archetypes():
            opened = cls.chromium.open(f'archetypes/{path.name}')
            # Screen captures first: printing makes chart libraries reflow for the page.
            screenshot = opened.slide_screenshots()[0]
            slides = opened.slides()
            cls.rendered[slide_number(path)] = {
                'slides': slides,
                'screenshot': screenshot,
                'pages': pdf_pages(opened.pdf()),
                'errors': list(opened.errors),
                'charts': chart_calls(path),
            }
            opened.close()

    @classmethod
    def tearDownClass(cls):
        cls.chromium.close()

    def test_archetypes_are_numbered_from_01_without_gaps(self):
        numbers = list(self.rendered)
        self.assertGreater(len(numbers), 0, 'no archetypes found')
        self.assertEqual(numbers, [f'{n:02d}' for n in range(1, len(numbers) + 1)])

    def test_each_archetype_is_one_slide_of_11_by_8_5_inches(self):
        for number, r in self.rendered.items():
            with self.subTest(archetype=number):
                self.assertEqual(len(r['slides']), 1, 'expected exactly one .slide')
                slide = r['slides'][0]
                self.assertEqual((slide['width'], slide['height']), SLIDE_PX)

    def test_each_archetype_prints_to_exactly_one_landscape_letter_page(self):
        for number, r in self.rendered.items():
            with self.subTest(archetype=number):
                self.assertEqual(r['pages'], [PAGE_PT])

    def test_content_stays_inside_the_slide(self):
        for number, r in self.rendered.items():
            with self.subTest(archetype=number):
                self.assertLessEqual(r['slides'][0]['overflow'], TOLERANCE_PX,
                                     'content reaches past the page edge and is clipped')


    def test_no_archetype_throws_a_page_error(self):
        for number, r in self.rendered.items():
            with self.subTest(archetype=number):
                self.assertEqual(r['errors'], [])

    def test_every_chart_an_archetype_creates_is_drawn(self):
        for number, r in self.rendered.items():
            slide = r['slides'][0]
            drawn = (sum(1 for painted in slide['canvases'] if painted > 0)
                     + sum(1 for shapes in slide['svg'] if shapes > 0))
            with self.subTest(archetype=number):
                self.assertEqual(drawn, r['charts'], 'a chart was not drawn: did its library load?')
        # Slides 04 and 08 (inline SVG) and 09 (Chart.js radar) carry charts today.
        self.assertGreaterEqual(sum(r['charts'] for r in self.rendered.values()), 3)

    def test_each_gallery_thumbnail_is_a_render_of_its_archetype(self):
        for number, r in self.rendered.items():
            with self.subTest(archetype=number):
                thumbnail = ROOT / 'assets' / f'slide_{number}.png'
                self.assertTrue(thumbnail.is_file(), f'{thumbnail.name} is missing')
                difference = image_difference(r['screenshot'], thumbnail.read_bytes())
                self.assertLessEqual(difference, TOLERANCE_IMAGE,
                                     f'{thumbnail.name} differs from the archetype in {difference:.2f}% of '
                                     'its pixels: run python3 scripts/make_images.py')


if __name__ == '__main__':
    unittest.main()
