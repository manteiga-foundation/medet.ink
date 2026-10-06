"""Slide 04: the maturity chart's stacked bands, read from the chart Highcharts drew.

Highcharts draws the FIRST series of a stacked chart on TOP (yAxis.reversedStacks defaults to
true), the opposite of what the array order suggests. The order was flipped four times in a row by
reasoning about the array; this test settles it from the rendered geometry.
"""
from __future__ import annotations

import unittest

from harness import Chromium

BOTTOM_TO_TOP = ['Poor', 'Below Avg', 'Average', 'Good', 'Excellent']

# For every series, where its band's upper edge sits at each category (plot pixels, y down).
STACK_PROBE = """() => {
  const chart = Highcharts.charts.find(Boolean);
  return chart.series.map(s => ({ name: s.name, tops: s.points.map(p => p.plotY) }));
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
