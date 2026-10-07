"""Chart colours follow the slide's risk level: one colour family per severity.

A finding page states its risk level as a class on its meta value (`critical`, `high`, `medium`,
`low`, `info`), which tests/test_severity_palette.py keeps on the palette. The charts on that same
page must agree: the radar fill and the risk-score bar sit in the family of the risk level the page
declares, so a page cannot say High and draw a green chart.

Measured from the rendered pixels, which covers a Chart.js canvas and inline SVG alike. The slide's
risk level is read from its own markup, so the check follows a page that changes severity.
"""
from __future__ import annotations

import colorsys
import io

import unittest

from PIL import Image

from harness import REPORT_FOLDER, Chromium, archetypes, slide_number

# The chart elements of a finding page: a radar canvas, an inline SVG container, the score bar.
CHART_SELECTOR = 'canvas, [data-chart], .score-bar-fill'

# The risk level the slide declares, and how many chart elements it draws.
RISK_LEVEL = r"""() => {
  const slide = document.querySelector('.slide');
  if (!slide) return null;
  const pattern = /^(?:sev-|color-|rsk-)?(critical|high|medium|med|low|info|informational)$/;
  let level = null;
  for (const item of slide.querySelectorAll('.meta-item')) {
    const label = item.querySelector('.meta-label');
    if (!label || !/risk\s*level/i.test(label.textContent)) continue;
    const value = item.querySelector('.meta-value');
    if (!value) continue;
    level = [...value.classList].map(c => (c.match(pattern) || [])[1]).find(Boolean) || null;
  }
  return { level, charts: document.querySelectorAll('canvas, [data-chart], .score-bar-fill').length };
}"""

# A pixel counts as coloured when it is neither washed out nor dark brand navy (#0A2540, value
# 0.25) used for labels: the chart's fill is what this measures.
SATURATION = 0.25
VALUE = 0.35
# At least this share of the chart must be coloured, or there is nothing to judge.
MIN_SHARE = 0.004

# Hue bands, in order. Red wraps through 0, so it is tested as a range at both ends.
FAMILIES = (
    ('critical', lambda hue: hue >= 345 or hue < 12),
    ('high', lambda hue: 12 <= hue < 25),
    ('medium', lambda hue: 25 <= hue < 58),
    ('low', lambda hue: 58 <= hue < 180),
    ('info', lambda hue: 180 <= hue < 260),
)
ALIASES = {'med': 'medium', 'informational': 'info'}


def family_of(hue: float) -> str | None:
    for name, within in FAMILIES:
        if within(hue):
            return name
    return None


def dominant_family(png: bytes) -> tuple[str | None, dict[str, int]]:
    """The colour family most of a chart's coloured pixels belong to, and the counts per family.

    Counted per family rather than averaged: a Chart.js canvas paints its label text on the same
    pixels as its fill, and an average of red fill and blue-grey text lands on neither.
    """
    image = Image.open(io.BytesIO(png)).convert('RGB')
    counts: dict[str, int] = {}
    for red, green, blue in image.getdata():
        hue, saturation, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
        if saturation < SATURATION or value < VALUE:
            continue
        name = family_of(hue * 360)
        if name:
            counts[name] = counts.get(name, 0) + 1
    total = sum(counts.values())
    if total < MIN_SHARE * image.width * image.height:
        return None, counts
    return max(counts, key=counts.get), counts


class ChartSeverityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()

    @classmethod
    def tearDownClass(cls):
        cls.chromium.close()

    def test_every_chart_uses_the_colour_family_of_the_risk_level_it_states(self):
        checked = 0
        for path in archetypes():
            opened = self.chromium.open(f'archetypes/{path.name}')
            try:
                stated = opened.page.evaluate(RISK_LEVEL)
                if not stated or not stated['level']:
                    continue  # a slide without a risk level states nothing to match
                level = ALIASES.get(stated['level'], stated['level'])
                charts = opened.page.locator(CHART_SELECTOR)
                for index in range(charts.count()):
                    family, counts = dominant_family(charts.nth(index).screenshot())
                    with self.subTest(archetype=slide_number(path), chart=index, level=level):
                        self.assertIsNotNone(
                            family, f'chart {index} shows no coloured pixels ({counts})')
                        self.assertEqual(
                            family, level,
                            f'chart {index} reads as {family} ({counts}) but the slide states '
                            f'{level}: use the {level} palette colours')
                    checked += 1
            finally:
                opened.close()
        if not REPORT_FOLDER:  # proves the probe found a slide that states a risk level
            self.assertGreater(checked, 0, 'no slide states a risk level and draws a chart')


if __name__ == '__main__':
    unittest.main()
