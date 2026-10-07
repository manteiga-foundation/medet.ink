"""The build scripts work on the folder they run in: the repository, or a report laid out like it.

A report folder holds archetypes/ (its slides), reports/ and assets/. Run from it, merge_slides.py,
make_pdf.py and make_images.py build that report and nothing else; run from the repository root,
they build the sample report.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from harness import ROOT

SCRIPTS = Path(__file__).resolve().parent.parent / 'scripts'


class ScriptsTests(unittest.TestCase):
    def test_a_report_folder_builds_its_own_pdf_and_thumbnails(self):
        before = {p: p.stat().st_mtime for p in [ROOT / 'reports' / 'final_report.pdf', ROOT / 'assets' / 'slide_01.png']}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for sub in ('archetypes', 'reports', 'assets'):
                (folder / sub).mkdir()
            shutil.copy(ROOT / 'archetypes' / '01-Slide-Cover.html', folder / 'archetypes' / '01-Slide-Cover.html')
            for script in ('merge_slides.py', 'make_pdf.py', 'make_images.py'):
                subprocess.run([sys.executable, str(SCRIPTS / script)], cwd=folder, check=True, capture_output=True)
            self.assertEqual(len(PdfReader(folder / 'reports' / 'final_report.pdf').pages), 1, 'the folder\'s one slide')
            self.assertEqual(Image.open(folder / 'assets' / 'slide_01.png').size, (1056, 816))
        after = {p: p.stat().st_mtime for p in before}
        self.assertEqual(after, before, 'the repository\'s own report is left alone')


if __name__ == '__main__':
    unittest.main()
