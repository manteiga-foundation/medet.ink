"""Charts are laid out with the template's web fonts, however late the fonts arrive.

A chart measures its text when it draws: Chart.js paints it once on a canvas, the inline SVG
charts size their legends, label boxes and rings from measured text. A chart drawn before Montserrat has loaded keeps a
fallback font's layout on screen and in print, and a first visit then differs from the gallery.
The test holds the web fonts back until the page's scripts have run, then redraws every chart
with the fonts loaded: nothing may move.
"""
from __future__ import annotations

import unittest

from harness import TOLERANCE_IMAGE, Chromium, archetypes, chart_calls, image_difference

# Where each chart sits on the page: inline SVG containers and Chart.js canvases.
CHART_AREAS = """() => [...document.querySelectorAll('[data-chart], canvas')].map(el => {
  const r = el.getBoundingClientRect();
  return { x: r.x, y: r.y, width: r.width, height: r.height };
})"""

# Redraws every chart now that the fonts have loaded.
REDRAW = """async () => {
  await document.fonts.ready;
  let charts = 0;
  // Inline SVG charts: empty each container and run its script again (it keeps its variables in a
  // function, so it can run twice); the script draws once the fonts are ready.
  const svgScripts = [...document.querySelectorAll('script:not([src])')].filter(s => s.textContent.includes('[data-chart='));
  if (svgScripts.length) {
    document.querySelectorAll('[data-chart]').forEach(el => el.replaceChildren());
    for (const original of svgScripts) {
      const again = document.createElement('script');
      again.textContent = original.textContent;
      document.body.appendChild(again);
    }
    await document.fonts.ready;
    await new Promise(r => setTimeout(r, 50));
    charts += [...document.querySelectorAll('[data-chart]')].filter(el => el.querySelector('svg')).length;
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
            # Compare each chart's own area: a chart is a fraction of the slide, and a whole-slide
            # comparison dilutes a moved label below the tolerance.
            areas = opened.page.evaluate(CHART_AREAS)
            first = [opened.page.screenshot(clip=area) for area in areas]
            redrawn = opened.page.evaluate(REDRAW)
            differences = [image_difference(before, opened.page.screenshot(clip=area)) for before, area in zip(first, areas)]
            opened.close()
            with self.subTest(archetype=path.name[:2]):
                self.assertEqual(redrawn, expected, 'charts found on the page')
                self.assertEqual(len(areas), expected, 'chart areas found on the page')
                for difference in differences:
                    self.assertLessEqual(difference, TOLERANCE_IMAGE,
                                         f'{difference:.2f}% of a chart moved when redrawn with the fonts loaded: '
                                         'the chart was laid out before the web fonts arrived')
            checked += 1
        self.assertGreater(checked, 0, 'no archetype draws a chart')


if __name__ == '__main__':
    unittest.main()
