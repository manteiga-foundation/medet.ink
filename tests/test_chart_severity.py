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

# Each severity's palette hue, which is what a chart of that severity must be drawn in:
# #EF4444 red, #F97316 orange, #F59E0B amber, #10B981 green, #0EA5E9 blue.
PALETTE_HUES = {'critical': 0.0, 'high': 25.0, 'medium': 38.0, 'low': 160.0, 'info': 199.0}
# Violet only appears on a chart of a slide that states no risk level (the template's maturity
# chart); kept in the wheel so every coloured pixel has a nearest family and none is dropped.
EXTRA_HUE = 313.0
ALIASES = {'med': 'medium', 'informational': 'info'}
# How far a chart's hue may sit from its palette hue and still read as that severity. Measured:
# the report's five pages sit at 3.2 degrees or less (antialiasing blends edges), while the older
# browner shade #9A3412 lands at 6.7 and 8.6. Five separates the two with room on both sides.
MAX_DRIFT = 5.0


def circular_distance(a: float, b: float) -> float:
    """The smaller angle between two hues, in degrees."""
    return min((a - b) % 360, (b - a) % 360)


def nearest_family(hue: float) -> str:
    """The palette colour a hue is closest to. Contiguous by construction, so no pixel is dropped."""
    candidates = dict(PALETTE_HUES)
    candidates['violet'] = EXTRA_HUE
    return min(candidates, key=lambda name: circular_distance(hue, candidates[name]))


def drift_from_palette(hue: float, family: str) -> float:
    return circular_distance(hue, PALETTE_HUES.get(family, EXTRA_HUE))


# Kept for the docstring test below: the families a slide may state.
SEVERITY_FAMILIES = tuple(PALETTE_HUES)
# A chart must be dominated by its family this strongly, or the colours are mixed enough to read
# as another risk: one stray band in a stack or legend must not decide the answer.
MAJORITY = 0.6


def measure_chart(png: bytes) -> dict:
    """What a chart's colours look like: the family most pixels land in, the counts, and how far,
    on average, those pixels sit from that family's palette hue.
    """
    image = Image.open(io.BytesIO(png)).convert('RGB')
    counts: dict[str, int] = {}
    drift = 0.0
    for red, green, blue in image.getdata():
        hue, saturation, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
        if saturation < SATURATION or value < VALUE:
            continue
        degrees = hue * 360
        name = nearest_family(degrees)
        counts[name] = counts.get(name, 0) + 1
        drift += drift_from_palette(degrees, name)
    total = sum(counts.values())
    if not total:
        return {'family': None, 'counts': counts, 'share': 0.0, 'drift': 0.0, 'coloured': 0}
    family = max(counts, key=counts.get)
    return {'family': family, 'counts': counts, 'share': counts[family] / total,
            'drift': drift / total, 'coloured': total,
            'enough': total >= MIN_SHARE * image.width * image.height}


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
                    chart = measure_chart(charts.nth(index).screenshot())
                    with self.subTest(archetype=slide_number(path), chart=index, level=level):
                        self.assertTrue(
                            chart['enough'],
                            f"chart {index} shows almost no colour ({chart['counts']})")
                        self.assertEqual(
                            chart['family'], level,
                            f"chart {index} reads as {chart['family']} ({chart['counts']}) but the "
                            f"slide states {level}: use the {level} palette colours")
                        self.assertGreaterEqual(
                            chart['share'], MAJORITY,
                            f"chart {index} is only {chart['share']:.0%} {chart['family']} "
                            f"({chart['counts']}): its colours are mixed enough to read as another "
                            f'risk level')
                        self.assertLessEqual(
                            chart['drift'], MAX_DRIFT,
                            f"chart {index} sits {chart['drift']:.0f} degrees off {level}'s palette "
                            f"hue: a darker shade must keep the hue (darken the palette colour, do "
                            f"not pick a browner one)")
                    checked += 1
            finally:
                opened.close()
        if not REPORT_FOLDER:  # proves the probe found a slide that states a risk level
            self.assertGreater(checked, 0, 'no slide states a risk level and draws a chart')


if __name__ == '__main__':
    unittest.main()
