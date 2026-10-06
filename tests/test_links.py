"""The public pages link only to files that exist, and the social preview points at medet.ink."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from harness import ROOT, archetypes, slide_number

PUBLIC_PAGES = ['index.html', 'archetypes/index.html', 'reports/combined_report.html']
SITE = 'https://medet.ink/'


class _References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        values = {name: value or '' for name, value in attrs}
        for name in ('href', 'src'):
            if values.get(name):
                self.links.append(values[name])
        key = values.get('property') or values.get('name')
        if tag == 'meta' and key and 'content' in values:
            self.meta[key] = values['content']


def references(page: str) -> _References:
    parser = _References()
    parser.feed((ROOT / page).read_text(encoding='utf-8'))
    return parser


def is_local(link: str) -> bool:
    return not re.match(r'^([a-z][a-z0-9+.-]*:|//|#)', link, re.I) and link != '...'


class LinkTests(unittest.TestCase):
    def test_every_local_link_on_the_public_pages_resolves(self):
        for page in PUBLIC_PAGES:
            links = references(page).links
            if page == 'archetypes/index.html':
                # The viewer lists its slides in a script, not in markup.
                links += re.findall(r'"(\d\d-Slide-[^"]+\.html)"', (ROOT / page).read_text(encoding='utf-8'))
            for link in links:
                if not is_local(link):
                    continue
                path = unquote(urlparse(link).path)
                # A root-relative path is served from the site root, which is the repository.
                target = ROOT / path.lstrip('/') if path.startswith('/') else (ROOT / page).parent / path
                with self.subTest(page=page, link=link):
                    self.assertTrue(target.is_file(), f'{link} does not exist')

    def test_chart_libraries_load_from_jsdelivr_pinned_to_a_version(self):
        # code.highcharts.com refuses headless browsers (403) and rate-limits (429), which left the
        # generated PDF and thumbnails without charts; an unpinned "latest" can change every print.
        pinned = re.compile(r'^https://cdn\.jsdelivr\.net/npm/[a-z0-9.-]+@\d+\.\d+\.\d+/\S+\.js$')
        scripts = 0
        for path in archetypes():
            for src in re.findall(r'<script[^>]*\ssrc="([^"]+)"', path.read_text(encoding='utf-8')):
                scripts += 1
                with self.subTest(archetype=path.name[:2], src=src):
                    self.assertRegex(src, pinned)
        self.assertGreater(scripts, 0)

    def test_landing_page_links_every_archetype_with_its_thumbnail(self):
        links = set(references('index.html').links)
        for path in archetypes():
            with self.subTest(archetype=path.name):
                self.assertIn(f'archetypes/{path.name}', links)
                self.assertIn(f'assets/slide_{slide_number(path)}.png', links)

    def test_social_preview_points_at_files_published_on_medet_ink(self):
        self.assertEqual((ROOT / 'CNAME').read_text().strip(), urlparse(SITE).netloc)
        meta = references('index.html').meta
        for key in ('og:url', 'twitter:url'):
            with self.subTest(meta=key):
                self.assertEqual(meta.get(key), SITE)
        for key in ('og:image', 'twitter:image'):
            with self.subTest(meta=key):
                image = meta.get(key, '')
                self.assertTrue(image.startswith(SITE), f'{key} must be an absolute medet.ink URL')
                self.assertTrue((ROOT / image[len(SITE):]).is_file(), f'{image} is not in the repository')
        self.assertEqual(meta.get('twitter:card'), 'summary_large_image')

    def test_viewer_and_gallery_follow_the_archetypes(self):
        names = [p.name for p in archetypes()]
        viewer = (ROOT / 'archetypes' / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'"(\d{2}-Slide-[^"]+\.html)"', viewer), names, 'the viewer lists every archetype in order')
        landing = (ROOT / 'index.html').read_text(encoding='utf-8')
        cards = re.findall(r'<a href="archetypes/(\d{2}-Slide-[^"]+\.html)"[^>]*>\s*<div[^>]*>\s*<img src="assets/slide_(\d{2})\.png"', landing)
        self.assertEqual([href for href, _ in cards], names, 'the gallery shows every archetype in order')
        for href, thumbnail in cards:
            with self.subTest(card=href):
                self.assertEqual(thumbnail, href[:2], 'each card shows its own thumbnail')


if __name__ == '__main__':
    unittest.main()
