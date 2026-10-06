"""Slide 08: the findings donut agrees with the counts under it and shows every label whole."""
from __future__ import annotations

import unittest

from harness import Chromium

# Read in the page: the stat boxes, the donut's labels (text and box), its centre total and area.
PROBE = r"""() => {
  const counts = [...document.querySelectorAll('.stat-item')].map(item => ({
    name: item.querySelector('.stat-label').textContent.trim(),
    count: +item.querySelector('.stat-number').textContent.trim() }));
  const chart = document.querySelector('[data-chart="findings"]');
  if (!chart) return { counts, chart: null };
  const area = chart.getBoundingClientRect();
  const labels = [...chart.querySelectorAll('[data-label]')].map(g => {
    const r = g.getBoundingClientRect();
    return { name: g.dataset.label, text: g.textContent.replace(/\s+/g, ' ').trim(),
             box: [r.left - area.left, r.top - area.top, r.right - area.left, r.bottom - area.top] };
  });
  const total = chart.querySelector('[data-total]');
  return { counts, chart: [area.width, area.height], labels, total: total ? total.textContent.trim() : null };
}"""


class FindingsChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chromium = Chromium()
        try:
            opened = chromium.open('archetypes/08-Slide-Findings-Overview.html')
            cls.found = opened.page.evaluate(PROBE)
            opened.close()
        finally:
            chromium.close()

    def setUp(self):
        self.assertIsNotNone(self.found['chart'], 'the donut is drawn in [data-chart="findings"]')

    def test_each_label_states_the_count_and_share_under_the_chart(self):
        counts = self.found['counts']
        total = sum(c['count'] for c in counts)
        expected = {c['name']: f"{c['name']} {c['count']} ({100 * c['count'] / total:.1f}%)" for c in counts}
        self.assertEqual({l['name']: l['text'] for l in self.found['labels']}, expected)

    def test_the_centre_shows_the_total(self):
        total = sum(c['count'] for c in self.found['counts'])
        self.assertEqual(self.found['total'], str(total))

    def test_labels_stay_inside_the_chart_and_apart(self):
        width, height = self.found['chart']
        labels = self.found['labels']
        for label in labels:
            left, top, right, bottom = label['box']
            with self.subTest(label=label['name']):
                self.assertGreaterEqual(left, -1)
                self.assertGreaterEqual(top, -1)
                self.assertLessEqual(right, width + 1)
                self.assertLessEqual(bottom, height + 1)
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                with self.subTest(labels=(a['name'], b['name'])):
                    apart = (a['box'][2] <= b['box'][0] or b['box'][2] <= a['box'][0]
                             or a['box'][3] <= b['box'][1] or b['box'][3] <= a['box'][1])
                    self.assertTrue(apart, 'labels overlap')


if __name__ == '__main__':
    unittest.main()
