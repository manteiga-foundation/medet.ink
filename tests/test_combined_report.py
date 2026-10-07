"""The combined report (reports/combined_report.html): generated from the archetypes, one page each."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness import (PAGE_PT, ROOT, TOLERANCE_IMAGE, TOLERANCE_PX, Chromium, archetypes, chart_calls,
                     chart_signature, image_difference, pdf_pages, pdf_texts)

REPORT = 'reports/combined_report.html'
CHECKOUT_SCRIPTS = Path(__file__).resolve().parent.parent / 'scripts'



class CombinedReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()
        cls.opened = cls.chromium.open(REPORT)
        # Screen captures first: printing makes chart libraries reflow for the page.
        cls.screens = cls.opened.slide_screenshots()
        cls.slides = cls.opened.slides()
        # Each archetype on its own: how it looks, and how it draws its charts.
        cls.own_screens, cls.own_charts = {}, {}
        for number, path in enumerate(archetypes(), start=1):
            own = cls.chromium.open(f'archetypes/{path.name}')
            cls.own_screens[number] = own.slide_screenshots()[0]
            if chart_calls(path):
                cls.own_charts[number] = chart_signature(own.slides()[0])
            own.close()

    @classmethod
    def tearDownClass(cls):
        cls.opened.close()
        cls.chromium.close()

    def test_committed_report_is_what_merge_slides_produces(self):
        with tempfile.TemporaryDirectory() as scratch:
            shutil.copytree(ROOT / 'archetypes', Path(scratch) / 'archetypes')
            # The folder's own scripts (the repository, or a copy under test); a report folder has
            # none and is built with this checkout's.
            scripts = ROOT / 'scripts' if (ROOT / 'scripts').is_dir() else CHECKOUT_SCRIPTS
            shutil.copytree(scripts, Path(scratch) / 'scripts')
            subprocess.run([sys.executable, 'scripts/merge_slides.py'], cwd=scratch, check=True,
                           stdout=subprocess.DEVNULL)
            for name in ('combined_report.html', 'merged_report.html'):
                with self.subTest(report=name):
                    fresh = (Path(scratch) / 'reports' / name).read_bytes()
                    committed = (ROOT / 'reports' / name).read_bytes()
                    self.assertTrue(fresh == committed,
                                    f'reports/{name} is stale: run python3 scripts/merge_slides.py')

    def test_report_holds_one_slide_per_archetype(self):
        self.assertEqual(len(self.slides), len(archetypes()))

    def test_each_slide_looks_exactly_like_its_archetype(self):
        # One document shares one stylesheet, one id space and one script scope: any rule, id or
        # script of one archetype that reaches another slide shows up here.
        for number, own in self.own_screens.items():
            with self.subTest(slide=number):
                difference = image_difference(self.screens[number - 1], own)
                self.assertLessEqual(difference, TOLERANCE_IMAGE,
                                     f'{difference:.2f}% of the slide differs from its archetype')

    def test_report_prints_one_landscape_letter_page_per_slide(self):
        self.assertEqual(pdf_pages(self.opened.pdf()), [PAGE_PT] * len(archetypes()))

    def test_sample_pdf_is_a_print_of_the_combined_report(self):
        committed = (ROOT / 'reports' / 'final_report.pdf').read_bytes()
        fresh = self.opened.pdf()
        self.assertEqual(pdf_pages(committed), pdf_pages(fresh))
        for number, (old, new) in enumerate(zip(pdf_texts(committed), pdf_texts(fresh)), start=1):
            with self.subTest(page=number):
                self.assertEqual(old, new, 'reports/final_report.pdf is stale: run python3 scripts/make_pdf.py')

    def test_content_stays_inside_each_slide(self):
        for number, slide in enumerate(self.slides, start=1):
            with self.subTest(slide=number):
                self.assertLessEqual(slide['overflow'], TOLERANCE_PX)


    def test_each_slide_draws_the_charts_its_archetype_draws(self):
        self.assertGreater(len(self.own_charts), 0, 'no archetype creates a chart')
        for number, expected in self.own_charts.items():
            with self.subTest(slide=number):
                self.assertEqual(chart_signature(self.slides[number - 1]), expected)

    def test_report_runs_without_page_errors(self):
        self.assertEqual(self.opened.errors, [])

    def test_element_ids_are_unique_across_the_report(self):
        duplicates = self.opened.page.evaluate("""() => {
          const seen = {};
          document.querySelectorAll('[id]').forEach(e => { seen[e.id] = (seen[e.id] || 0) + 1; });
          return Object.keys(seen).filter(id => seen[id] > 1);
        }""")
        self.assertEqual(duplicates, [])


if __name__ == '__main__':
    unittest.main()
