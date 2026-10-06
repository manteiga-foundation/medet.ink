"""The archetypes read as one report: one firm, one page count, a table of contents that matches."""
from __future__ import annotations

import html
import ipaddress
import re
import unittest

from harness import ROOT, archetypes, slide_number

BRAND_LINE = 'Property of ACME Consulting | acmecyber.com'
# RFC 5737: the only address ranges sample content may use.
DOCUMENTATION = [ipaddress.ip_network(n) for n in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24')]
# A dotted quad that is not part of a version string (Chrome/120.0.0.0) or a longer number.
ADDRESS = re.compile(r'(?<![\w./])(\d{1,3}(?:\.\d{1,3}){3})(?![\w.])')


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
                self.assertIsNone(re.search(r'\bISECI?\b|iseci\.us|\bBICSA\b', source),
                                  'an organisation other than the fictional ACME and its client is named')

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

    def test_sample_addresses_use_documentation_ranges(self):
        pages = {f'archetypes/{n}': s for n, s in self.sources.items()}
        pages.update({page: (ROOT / page).read_text(encoding='utf-8') for page in ('README.md', 'index.html')})
        for page, source in pages.items():
            for address in ADDRESS.findall(source):
                if any(int(octet) > 255 for octet in address.split('.')):
                    continue  # a coordinate or version, not an address
                with self.subTest(page=page, address=address):
                    ip = ipaddress.ip_address(address)
                    self.assertTrue(any(ip in net for net in DOCUMENTATION), 'use 192.0.2.0/24, 198.51.100.0/24 or 203.0.113.0/24')

    def test_public_pages_state_the_archetype_count(self):
        claims = 0
        for page in ('README.md', 'index.html'):
            text = (ROOT / page).read_text(encoding='utf-8')
            for match in re.finditer(r'\b(\d+)(?: pre-formatted layouts|-page\b| slides are included)', text):
                claims += 1
                with self.subTest(page=page, claim=match.group(0)):
                    self.assertEqual(int(match.group(1)), len(self.sources))
        self.assertGreater(claims, 0)


if __name__ == '__main__':
    unittest.main()
