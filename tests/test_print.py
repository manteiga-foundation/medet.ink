"""What prints is what the screen shows: no shadows that a PDF viewer turns into grey boxes.

Chromium writes a blurred CSS box shadow into a PDF in a form that macOS's PDF engine (Preview,
Quick Look) draws as a hard-edged grey box behind the card, button or panel that casts it. Slides
cast no box shadows in print; cards keep their 1 px borders.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageStat

from harness import ROOT, Chromium, archetypes, slide_number

# Every element of the slide (and the slide itself), with its pseudo-elements.
SHADOWS_IN_PRINT = r"""() => {
  const slide = document.querySelector('.slide');
  const found = [];
  for (const el of [slide, ...slide.querySelectorAll('*')]) {
    for (const pseudo of [null, '::before', '::after']) {
      const shadow = getComputedStyle(el, pseudo).boxShadow;
      if (shadow && shadow !== 'none') {
        found.push(`${el.tagName.toLowerCase()}.${[...el.classList].join('.')}${pseudo || ''}: ${shadow}`);
      }
    }
  }
  return found;
}"""

BLOCK = 12  # px; a block flat in both renders and darker in print is a box the screen does not show


def flat_darker_blocks(screen: Image.Image, printed: Image.Image) -> list[tuple[int, int, float]]:
    hits = []
    for by in range(0, screen.height - BLOCK, BLOCK):
        for bx in range(0, screen.width - BLOCK, BLOCK):
            box = (bx, by, bx + BLOCK, by + BLOCK)
            s, p = ImageStat.Stat(screen.crop(box)), ImageStat.Stat(printed.crop(box))
            if s.stddev[0] < 1.5 and p.stddev[0] < 1.5 and s.mean[0] - p.mean[0] > 3:
                hits.append((bx, by, round(s.mean[0] - p.mean[0], 1)))
    return hits


class PrintTests(unittest.TestCase):
    def test_nothing_in_a_slide_casts_a_shadow_in_print(self):
        chromium = Chromium()
        try:
            for path in archetypes():
                opened = chromium.open(f'archetypes/{path.name}')
                opened.page.emulate_media(media='print')
                shadows = opened.page.evaluate(SHADOWS_IN_PRINT)
                opened.close()
                with self.subTest(archetype=slide_number(path)):
                    self.assertEqual(shadows, [], 'a box shadow prints as a grey box in macOS viewers')
        finally:
            chromium.close()

    @unittest.skipUnless(shutil.which('sips'), 'needs macOS sips (CoreGraphics) to draw the PDF as Preview does')
    def test_the_sample_pdf_draws_no_box_the_screen_does_not(self):
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(ROOT / 'reports' / 'final_report.pdf')
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            for number, page in enumerate(reader.pages, 1):
                writer = PdfWriter()
                writer.add_page(page)
                single = tmp / f'page-{number:02d}.pdf'
                writer.write(single)
                png = single.with_suffix('.png')
                subprocess.run(['sips', '-s', 'format', 'png', '--resampleWidth', '2112', str(single), '--out', str(png)],
                               check=True, capture_output=True)
                printed = Image.open(png).convert('L').resize((1056, 816), Image.LANCZOS)
                screen = Image.open(ROOT / 'assets' / f'slide_{number:02d}.png').convert('L')
                hits = flat_darker_blocks(screen, printed)
                with self.subTest(page=number):
                    self.assertEqual(len(hits), 0, f'{len(hits)} flat areas print darker than on screen, e.g. {hits[:3]}')


if __name__ == '__main__':
    unittest.main()
