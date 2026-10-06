"""The archetypes read as one report: one firm, one page count, a table of contents that matches."""
from __future__ import annotations

import html
import re
import unittest

from harness import archetypes, slide_number

BRAND_LINE = 'Property of ACME Consulting | acmecyber.com'


def text_of(fragment: str) -> str:
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', fragment)).replace('\xa0', ' ').split())


def first(pattern: str, source: str) -> str:
    match = re.search(pattern, source, re.S)
    return text_of(match.group(1)) if match else ''


def title_of(source: str) -> str:
    """The section name of an archetype: its <title> without the firm prefix."""
    return first(r'<title>(.*?)</title>', source).split(' - ', 1)[-1]


class ConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {slide_number(p): p.read_text(encoding='utf-8') for p in archetypes()}

    def test_every_footer_carries_the_same_brand_line(self):
        for number, source in self.sources.items():
            with self.subTest(archetype=number):
                self.assertEqual(first(r'<div class="footer-line">(.*?)</div>', source), BRAND_LINE)

    def test_the_report_names_no_other_firm(self):
        for number, source in self.sources.items():
            with self.subTest(archetype=number):
                self.assertIsNone(re.search(r'\bISECI?\b|iseci\.us', source), 'a firm other than ACME is named')

    def test_each_page_number_is_the_slide_number_out_of_the_archetype_count(self):
        total = f'/ {len(self.sources):02d}'
        for number, source in self.sources.items():
            with self.subTest(archetype=number):
                self.assertEqual(first(r'<span class="page-indicator">(.*?)</span>', source), number)
                self.assertEqual(first(r'<span class="page-total">(.*?)</span>', source), total)

    def test_table_of_contents_lists_every_page_after_the_cover(self):
        toc = self.sources['02']
        rows = re.findall(r'<div class="toc-page">(.*?)</div>\s*<div class="toc-section">(.*?)</div>', toc, re.S)
        listed = [(text_of(page), text_of(section)) for page, section in rows]
        expected = [(number, title_of(source)) for number, source in self.sources.items() if number != '01']
        self.assertEqual(listed, expected)


if __name__ == '__main__':
    unittest.main()
