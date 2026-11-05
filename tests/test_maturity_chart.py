"""Slide 04: the maturity scorecard, read from the drawn bars and the pills.
Each domain row states a score; the bar drawn for it must be that share of its track, the pill must
name the band the score falls in, and the bar must take the band's colour. The spiral chart this slide
carried before (stacked bands by company size) is retired: a polygon per series no longer exists.
"""
from __future__ import annotations
import unittest
from harness import Chromium

BANDS = [(0, 'poor', 'Poor', '#8B5CF6'), (20, 'below', 'Below Avg', '#EF4444'), (40, 'average', 'Average', '#F59E0B'),
         (60, 'good', 'Good', '#10B981'), (80, 'excellent', 'Excellent', '#3B82F6')]

ROWS = """() => [...document.querySelectorAll('tr[data-score]')].map(row => {
  const bars = [...row.querySelectorAll('rect[data-domain]')]; const cell = row.querySelector('td[data-chart="maturity"]');
  const track = row.querySelector('td.bar svg rect');
  const pill = row.querySelector('.pill');
  return { domain: cell.dataset.domain, score: +row.dataset.score, shown: row.querySelector('td.score').textContent.trim(),
           bars: bars.length, width: bars[0] ? +bars[0].getAttribute('width') : null, track: track ? +track.getAttribute('width') : null,
           fill: bars[0] ? bars[0].getAttribute('fill').toUpperCase() : null, pill: pill.textContent.trim(), pillClass: [...pill.classList].filter(c => c !== 'pill').join(' ') };
})"""


def band_of(score: int):
    return [b for b in BANDS if score >= b[0]][-1]


class MaturityScorecardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chromium = Chromium()
        cls.opened = cls.chromium.open('archetypes/04-Slide-Maturity-Scorecard.html')

    @classmethod
    def tearDownClass(cls):
        cls.opened.close()
        cls.chromium.close()

    def test_each_domain_bar_is_its_score_share_of_the_track_in_the_band_colour_the_pill_names(self):
        rows = self.opened.page.evaluate(ROWS)
        self.assertEqual(len(rows), 8)
        for row in rows:
            with self.subTest(domain=row['domain']):
                _, cls, label, colour = band_of(row['score'])
                self.assertEqual(row['bars'], 1)
                self.assertEqual(row['shown'], f"{row['score']}%")
                self.assertAlmostEqual(row['width'] / row['track'], row['score'] / 100, places=2)
                self.assertEqual((row['pill'], row['pillClass'], row['fill']), (label, cls, colour))

    def test_the_spiral_is_gone(self):
        self.assertEqual(self.opened.page.evaluate("document.querySelectorAll('polygon[data-series]').length"), 0)
        self.assertEqual(self.opened.errors, [])


if __name__ == '__main__':
    unittest.main()
