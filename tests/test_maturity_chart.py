"""Slide 04: the maturity chart's stacked bands, read from the drawn SVG.

The order was flipped four times in a row by reasoning about the series array (Highcharts, which
drew the chart then, put the first series of a stack on top); this test settles it from the
rendered geometry: each band is a polygon whose first points trace its upper edge.
"""
from __future__ import annotations

import unittest

from harness import Chromium

BOTTOM_TO_TOP = ['Poor', 'Below Avg', 'Average', 'Good', 'Excellent']

# For every band, where its upper edge sits at each category (pixels, y down).
STACK_PROBE = """() => {
  const bands = [...document.querySelectorAll('[data-chart="maturity"] polygon[data-series]')];
  return bands.map(b => {
    const points = b.getAttribute('points').trim().split(/\\s+/).map(p => +p.split(',')[1]);
    return { name: b.dataset.series, tops: points.slice(0, points.length / 2) };
  });
}"""


class MaturityChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()
        cls.opened = cls.chromium.open('archetypes/04-Slide-Cybersecurity-Maturity.html')

    @classmethod
    def tearDownClass(cls):
        cls.opened.close()
        cls.chromium.close()

    def test_bands_stack_poor_at_the_bottom_up_to_excellent_on_top(self):
        series = {s['name']: s['tops'] for s in self.opened.page.evaluate(STACK_PROBE)}
        self.assertEqual(sorted(series), sorted(BOTTOM_TO_TOP))
        categories = len(next(iter(series.values())))
        for i in range(categories):
            with self.subTest(category=i):
                tops = [series[name][i] for name in BOTTOM_TO_TOP]
                # Each band's top edge is at or above (smaller y) the band beneath it.
                self.assertEqual(tops, sorted(tops, reverse=True), f'band tops bottom-to-top: {tops}')
        # At the first category every band has height, so the order there is strict.
        first = [series[name][0] for name in BOTTOM_TO_TOP]
        self.assertEqual(len(set(first)), len(first))


if __name__ == '__main__':
    unittest.main()
