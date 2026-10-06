"""The repository publishes only what the site and the README use."""
from __future__ import annotations

import re
import subprocess
import unittest

from harness import ROOT, archetypes, slide_number

DERIVED = {'assets/demo.gif', 'reports/combined_report.html', 'reports/merged_report.html',
           'reports/final_report.pdf'}
REFERRERS = ['README.md', 'index.html', 'archetypes/index.html']


def tracked_files() -> list[str] | None:
    """Files under version control, or None when ROOT is not a git checkout (a test copy)."""
    if not (ROOT / '.git').exists():
        return None
    out = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return out.splitlines()


class RepositoryTests(unittest.TestCase):
    def test_no_finder_metadata_is_tracked(self):
        files = tracked_files()
        if files is None:
            self.skipTest('not a git checkout')
        self.assertEqual([f for f in files if f.split('/')[-1] == '.DS_Store'], [])

    def test_every_asset_and_report_is_derived_or_linked(self):
        files = tracked_files()
        if files is None:
            files = [str(p.relative_to(ROOT)) for d in ('assets', 'reports') for p in (ROOT / d).rglob('*') if p.is_file()]
        derived = DERIVED | {f'assets/slide_{slide_number(p)}.png' for p in archetypes()}
        text = ' '.join((ROOT / page).read_text(encoding='utf-8') for page in REFERRERS)
        for path in files:
            if not re.match(r'(assets|reports)/', path) or path in derived:
                continue
            with self.subTest(file=path):
                name = path.split('/')[-1]
                self.assertTrue(name in text, f'{path} is neither generated nor linked from {", ".join(REFERRERS)}')


if __name__ == '__main__':
    unittest.main()
