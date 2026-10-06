"""Measures the spike candidates against the Highcharts original and builds contact-sheet.png.

Run from the repository root: python3 docs/spikes/001-chart-library/measure.py
"""
import io, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tests'))
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from harness import Chromium, image_difference

PAGES = {'highcharts': 'archetypes/04-Slide-Cybersecurity-Maturity.html'}
for n in ('echarts', 'chartjs', 'svg'):
    PAGES[n] = f'docs/spikes/001-chart-library/04-{n}.html'

c = Chromium()
shots, slides, results = {}, {}, {}
for name, path in PAGES.items():
    o = c.open(path)
    o.page.wait_for_timeout(300)
    shots[name] = o.page.locator('#chart-04').screenshot()
    slides[name] = o.slide_screenshots()[0]
    over = o.slides()[0]['overflow']
    pdf = o.pdf()
    text = ' '.join((PdfReader(io.BytesIO(pdf)).pages[0].extract_text() or '').split()).upper()
    results[name] = {'errors': o.errors, 'overflow': over,
                     'chart text in PDF text layer': all(w in text for w in ('STARTUPS', 'FORTUNE 500', 'EXCELLENT', 'GLOBAL FINANCE CORP'))}
    o.close()
c.close()
for name in PAGES:
    results[name]['chart pixels differing from Highcharts %'] = round(image_difference(shots[name], shots['highcharts']), 2)
    results[name]['slide pixels differing from Highcharts %'] = round(image_difference(slides[name], slides['highcharts']), 2)
print(json.dumps(results, indent=1))

# Contact sheet: the four charts side by side at 2x for legibility, labelled.
imgs = {k: Image.open(io.BytesIO(v)).convert('RGB') for k, v in shots.items()}
w, h = imgs['highcharts'].size
pad, head = 24, 40
sheet = Image.new('RGB', (pad + 4 * (w + pad), head + h + pad), 'white')
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)
except OSError:
    font = ImageFont.load_default()
titles = {'highcharts': 'Highcharts 13.1.1 (today)', 'echarts': 'Apache ECharts 6.1.0, SVG',
          'chartjs': 'Chart.js 4.5.1, canvas', 'svg': 'Inline SVG, no library'}
for i, name in enumerate(PAGES):
    x = pad + i * (w + pad)
    draw.text((x, 12), titles[name], fill=(10, 37, 64), font=font)
    sheet.paste(imgs[name].resize((w, h)), (x, head))
sheet.save(Path(__file__).with_name('contact-sheet.png'))
print('sheet', sheet.size)
