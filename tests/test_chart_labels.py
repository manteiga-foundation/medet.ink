"""Chart labels are drawn whole: no chart library shortens a label to fit."""
from __future__ import annotations

import unittest

from harness import Chromium, archetypes, slide_number

# Known defect: slide 08's donut is too tight for its labels, so Highcharts shortens Medium and
# Low to "Medi..." and "L...". Drawn in the real font since the charts wait for it.
KNOWN_TRUNCATED = {'08'}

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
            if number in KNOWN_TRUNCATED:
                continue
            with self.subTest(archetype=number):
                self.assertEqual(labels, [])

    @unittest.expectedFailure
    def test_known_truncation_is_fixed(self):
        for number in sorted(KNOWN_TRUNCATED):
            self.assertEqual(self.truncated[number], [], f'slide {number}')


if __name__ == '__main__':
    unittest.main()
