"""Charts are laid out with the template's web fonts, however late the fonts arrive.

A chart measures its text when it draws: Chart.js paints it once on a canvas, Highcharts places
and truncates labels from the measured widths. A chart drawn before Montserrat has loaded keeps a
fallback font's layout on screen and in print, and a first visit then differs from the gallery.
The test holds the web fonts back until the page's scripts have run, then redraws every chart
with the fonts loaded: nothing may move.
"""
from __future__ import annotations

import unittest

from harness import TOLERANCE_IMAGE, Chromium, archetypes, chart_calls, image_difference

# Rebuilds every chart from its own options and callback, now that the fonts have loaded.
REDRAW = """async () => {
  await document.fonts.ready;
  let charts = 0;
  if (window.Highcharts) {
    for (const chart of Highcharts.charts.filter(Boolean)) {
      // destroy() clears the chart's own options: copy them first.
      const target = chart.renderTo, options = Highcharts.merge(chart.userOptions), callback = chart.callback;
      chart.destroy();
      Highcharts.chart(target, options, callback);
      charts++;
    }
  }
  if (window.Chart) {
    for (const canvas of document.querySelectorAll('canvas')) {
      const chart = Chart.getChart(canvas);
      if (chart) { chart.update('none'); charts++; }
    }
  }
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  return charts;
}"""


class ChartFontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()

    @classmethod
    def tearDownClass(cls):
        cls.chromium.close()

    def test_charts_are_laid_out_with_the_web_fonts_when_fonts_arrive_late(self):
        checked = 0
        for path in archetypes():
            expected = chart_calls(path)
            if not expected:
                continue
            opened = self.chromium.open(f'archetypes/{path.name}', hold_fonts=True)
            first = opened.screenshot()
            redrawn = opened.page.evaluate(REDRAW)
            difference = image_difference(first, opened.screenshot())
            opened.close()
            with self.subTest(archetype=path.name[:2]):
                self.assertEqual(redrawn, expected, 'charts found on the page')
                self.assertLessEqual(difference, TOLERANCE_IMAGE,
                                     f'{difference:.2f}% of the slide moved when redrawn with the fonts loaded: '
                                     'the chart was laid out before the web fonts arrived')
            checked += 1
        self.assertGreater(checked, 0, 'no archetype draws a chart')


if __name__ == '__main__':
    unittest.main()
