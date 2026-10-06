"""Chart labels are drawn whole: no chart library shortens a label to fit."""
from __future__ import annotations

import unittest

from harness import Chromium, archetypes, slide_number

# Highcharts shortened slide 08's labels ("Medi...", "L...") before the donut was inline SVG.

PROBE = r"""() => [...document.querySelectorAll('.slide svg text')]
  .map(t => t.textContent).filter(t => t.includes('\u2026'))"""


class ChartLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chromium = Chromium()
        cls.truncated = {}
        try:
            for path in archetypes():
                opened = chromium.open(f'archetypes/{path.name}')
                try:
                    cls.truncated[slide_number(path)] = opened.page.evaluate(PROBE)
                finally:
                    opened.close()
        finally:
            chromium.close()

    def test_no_chart_label_is_truncated(self):
        for number, labels in self.truncated.items():
            with self.subTest(archetype=number):
                self.assertEqual(labels, [])


if __name__ == '__main__':
    unittest.main()
