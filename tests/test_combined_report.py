"""The combined report (reports/combined_report.html): generated from the archetypes, one page each."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness import (PAGE_PT, ROOT, TOLERANCE_PX, Chromium, archetypes, chart_calls, chart_signature,
                     pdf_pages, pdf_texts)

REPORT = 'reports/combined_report.html'

# Measured defects, open until fixed (docs/template.md, "Known defects"). A fix removes the slide
# numbers here; the expected-failure tests then report an unexpected success until removed.
#
# merge_slides.py copies every inline script twice: into <head>, before any slide exists, and
# again with each slide's body. The head copies fail (Highcharts error #13) after declaring
# `const chartData`, so slide 04's own copy throws and the maturity chart is never drawn; slide
# 08's chart then lands in the first id="chart-container", which is slide 04's. Chart.js is
# created twice on slide 09's canvas.
KNOWN_WRONG_CHARTS = {4, 8}
# The Risk Matrix card grows to 969 px on slide 06 (it fits in its archetype); slides 09 and 16
# clip their footers as their archetypes do.
KNOWN_OVERFLOW = {6, 9, 16}


class CombinedReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()
        cls.opened = cls.chromium.open(REPORT)
        cls.slides = cls.opened.slides()
        # How each archetype that creates charts draws them on its own.
        cls.own_charts = {}
        for number, path in enumerate(archetypes(), start=1):
            if chart_calls(path):
                own = cls.chromium.open(f'archetypes/{path.name}')
                cls.own_charts[number] = chart_signature(own.slides()[0])
                own.close()

    @classmethod
    def tearDownClass(cls):
        cls.opened.close()
        cls.chromium.close()

    def test_committed_report_is_what_merge_slides_produces(self):
        with tempfile.TemporaryDirectory() as scratch:
            shutil.copytree(ROOT / 'archetypes', Path(scratch) / 'archetypes')
            shutil.copytree(ROOT / 'scripts', Path(scratch) / 'scripts')
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
            if number in KNOWN_OVERFLOW:
                continue
            with self.subTest(slide=number):
                self.assertLessEqual(slide['overflow'], TOLERANCE_PX)

    @unittest.expectedFailure
    def test_known_overflow_is_fixed(self):
        for number in sorted(KNOWN_OVERFLOW):
            self.assertLessEqual(self.slides[number - 1]['overflow'], TOLERANCE_PX, number)

    def test_each_slide_draws_the_charts_its_archetype_draws(self):
        self.assertGreater(len(self.own_charts), 0, 'no archetype creates a chart')
        for number, expected in self.own_charts.items():
            if number in KNOWN_WRONG_CHARTS:
                continue
            with self.subTest(slide=number):
                self.assertEqual(chart_signature(self.slides[number - 1]), expected)

    @unittest.expectedFailure
    def test_known_wrong_charts_are_fixed(self):
        for number in sorted(KNOWN_WRONG_CHARTS):
            self.assertEqual(chart_signature(self.slides[number - 1]), self.own_charts[number], number)

    @unittest.expectedFailure
    def test_report_runs_without_page_errors(self):
        self.assertEqual(self.opened.errors, [])

    @unittest.expectedFailure
    def test_element_ids_are_unique_across_the_report(self):
        duplicates = self.opened.page.evaluate("""() => {
          const seen = {};
          document.querySelectorAll('[id]').forEach(e => { seen[e.id] = (seen[e.id] || 0) + 1; });
          return Object.keys(seen).filter(id => seen[id] > 1);
        }""")
        self.assertEqual(duplicates, [])


if __name__ == '__main__':
    unittest.main()
