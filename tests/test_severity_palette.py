"""Severity colours: one palette, the same on every slide (the Tailwind 500 tier)."""
from __future__ import annotations

import re
import unittest

from harness import Chromium, archetypes, slide_number

PALETTE = {
    'critical': '#EF4444',
    'high': '#F97316',
    'medium': '#F59E0B',
    'low': '#10B981',
    'info': '#0EA5E9',
}
ALIASES = {'med': 'medium', 'informational': 'info'}
# The other red and amber that were in use. A slide that shows severities uses only the
# palette's red and amber (slide 10's status pill, not a severity, keeps the darker red for text).
RETIRED = {'#DC2626': r'#DC2626|220,\s*38,\s*38', '#FBBF24': r'#FBBF24|251,\s*191,\s*36'}

# Severity-coded elements carry the severity as a class: `critical`, `high`, `medium` (`med`),
# `low` or `info`, alone or prefixed `sev-`, `color-` or `rsk-` (`eff-low` is an effort level).
PROBE = r"""() => {
  const pattern = /^(?:sev-|color-|rsk-)?(critical|high|medium|med|low|info|informational)$/;
  const rgb = value => {
    const m = value && value.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    if (!m || (m[4] !== undefined && +m[4] === 0)) return null;
    const c = [+m[1], +m[2], +m[3]];
    return Math.max(...c) - Math.min(...c) < 64 ? null : c;   // white, ink and slate are neutral
  };
  const found = [], effort = [];
  for (const el of document.querySelectorAll('.slide [class*="eff-"]')) {
    const c = rgb(getComputedStyle(el).backgroundColor);
    if (c) effort.push({ what: `.${[...el.classList].join('.')}`, rgb: c });
  }
  for (const el of document.querySelectorAll('.slide [class]')) {
    const token = [...el.classList].map(c => c.match(pattern)).find(Boolean);
    if (!token) continue;
    const style = getComputedStyle(el);
    const props = { color: style.color, background: style.backgroundColor, fill: style.fill, stroke: style.stroke };
    if (parseFloat(style.borderLeftWidth) > 0) props['border-left'] = style.borderLeftColor;
    for (const [prop, value] of Object.entries(props)) {
      const c = rgb(value);
      if (c) found.push({ what: `.${[...el.classList].join('.')} ${prop}`, severity: token[1], rgb: c });
    }
  }
  for (const chart of (window.Highcharts ? Highcharts.charts.filter(Boolean) : [])) {
    for (const point of chart.series.flatMap(s => s.points)) {
      const name = String(point.name || '').toLowerCase();
      if (/^(critical|high|medium|low|info|informational)$/.test(name)) {
        const h = point.color;
        found.push({ what: `chart point ${point.name}`, severity: name,
                     rgb: [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)) });
      }
    }
  }
  return { found, effort };
}"""


def hex_of(rgb) -> str:
    return '#' + ''.join(f'{round(v):02X}' for v in rgb)


class SeverityPaletteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()

    @classmethod
    def tearDownClass(cls):
        cls.chromium.close()

    @classmethod
    def probe(cls) -> dict:
        if not hasattr(cls, '_probed'):
            cls._probed = {}
            for path in archetypes():
                opened = cls.chromium.open(f'archetypes/{path.name}')
                try:
                    cls._probed[path] = opened.page.evaluate(PROBE)
                finally:
                    opened.close()
        return cls._probed

    def test_severity_coded_elements_use_the_palette(self):
        seen = 0
        for path, result in self.probe().items():
            for item in result['found']:
                seen += 1
                severity = ALIASES.get(item['severity'], item['severity'])
                with self.subTest(archetype=slide_number(path), element=item['what']):
                    self.assertEqual(hex_of(item['rgb']), PALETTE[severity], f'{severity} is {PALETTE[severity]}')
        self.assertGreater(seen, 20, 'the probe found the severity-coded elements')

    def test_slides_that_show_severities_use_no_retired_colour(self):
        for path, result in self.probe().items():
            if not result['found']:
                continue
            source = path.read_text(encoding='utf-8')
            for colour, pattern in RETIRED.items():
                with self.subTest(archetype=slide_number(path), colour=colour):
                    self.assertIsNone(re.search(pattern, source, re.I),
                                      f'use {PALETTE["critical"]} or {PALETTE["medium"]} instead')

    def test_effort_levels_use_no_severity_colour(self):
        effort = [(slide_number(p), e) for p, r in self.probe().items() for e in r['effort']]
        self.assertGreater(len(effort), 0, 'the probe found the effort levels')
        for number, item in effort:
            with self.subTest(archetype=number, element=item['what']):
                self.assertNotIn(hex_of(item['rgb']), PALETTE.values())

if __name__ == '__main__':
    unittest.main()
