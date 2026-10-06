"""The HTML template download: the archetypes, the viewer and the combined report, as they are."""
from __future__ import annotations

import re
import unittest
import zipfile

from harness import ROOT, archetypes

ZIP = ROOT / 'reports' / 'medet-ink-template.zip'
FOLDER = 'medet-ink-template/'


def expected_files() -> dict[str, str]:
    """Name inside the archive -> path in the repository."""
    files = {'README.md': 'README.md', 'LICENSE': 'LICENSE', 'combined_report.html': 'reports/combined_report.html',
             'archetypes/index.html': 'archetypes/index.html'}
    files.update({f'archetypes/{p.name}': f'archetypes/{p.name}' for p in archetypes()})
    return files


class TemplateDownloadTests(unittest.TestCase):
    def test_the_download_holds_the_template_as_it_is_in_the_repository(self):
        self.assertTrue(ZIP.exists(), 'run scripts/make_template.py')
        with zipfile.ZipFile(ZIP) as archive:
            names = sorted(archive.namelist())
            expected = expected_files()
            self.assertEqual(names, sorted(FOLDER + name for name in expected))
            for name, source in expected.items():
                with self.subTest(file=name):
                    self.assertEqual(archive.read(FOLDER + name), (ROOT / source).read_bytes(),
                                     'out of date: run scripts/make_template.py')

    def test_every_page_in_the_download_finds_what_it_links_to(self):
        self.assertTrue(ZIP.exists(), 'run scripts/make_template.py')
        with zipfile.ZipFile(ZIP) as archive:
            names = set(archive.namelist())
            for name in sorted(n for n in names if n.endswith('.html')):
                text = archive.read(name).decode('utf-8')
                folder = name.rsplit('/', 1)[0]
                for target in re.findall(r'(?:src|href)="([^"]+)"', text):
                    if re.match(r'(?:[a-z]+:|#|//|\.\.\.)', target):
                        continue
                    resolved = '/'.join(part for part in f'{folder}/{target.split("#")[0]}'.split('/') if part != '.')
                    while '/../' in resolved:
                        resolved = re.sub(r'[^/]+/\.\./', '', resolved, count=1)
                    with self.subTest(page=name, link=target):
                        self.assertIn(resolved, names)


if __name__ == '__main__':
    unittest.main()
