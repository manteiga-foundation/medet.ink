"""The README's demo GIF shows the current thumbnails, one frame per archetype."""
from __future__ import annotations

import unittest

from PIL import Image, ImageChops, ImageSequence, ImageStat

from harness import ROOT, archetypes, slide_number

# The GIF is a 128-colour dithered copy, so frames are compared small, by mean difference.
COMPARE_SIZE = (100, 77)
TOLERANCE_MEAN = 6.0  # mean absolute difference per channel, out of 255


def small(image: Image.Image) -> Image.Image:
    return image.convert('RGB').resize(COMPARE_SIZE, Image.LANCZOS)


class DemoGifTests(unittest.TestCase):
    def test_demo_gif_shows_each_thumbnail_in_order(self):
        frames = [small(frame) for frame in ImageSequence.Iterator(Image.open(ROOT / 'assets' / 'demo.gif'))]
        slides = archetypes()
        self.assertEqual(len(frames), len(slides), 'one frame per archetype')
        for frame, path in zip(frames, slides):
            number = slide_number(path)
            with self.subTest(archetype=number):
                thumbnail = small(Image.open(ROOT / 'assets' / f'slide_{number}.png'))
                difference = sum(ImageStat.Stat(ImageChops.difference(frame, thumbnail)).mean) / 3
                self.assertLessEqual(difference, TOLERANCE_MEAN,
                                     f'frame differs from slide_{number}.png by {difference:.1f}: '
                                     'regenerate assets/demo.gif (docs/template.md)')


if __name__ == '__main__':
    unittest.main()
