# 001: chart-library

Question: can the template stop depending on Highcharts without its charts changing, starting with
the hardest one, the stacked area chart on slide 04?

Why: Highcharts is not open source. Its own file header reads "A commercial license may be required
depending on use", and the people this template is for (consultancies, red teams) produce client
reports commercially, so an MIT template that loads Highcharts can quietly put its users in need of
a licence. It is also the template's heaviest dependency, and code.highcharts.com refused headless
browsers (403) and rate-limited repeated runs (429) until the template moved to a pinned jsDelivr
copy.

## Approach

`build.py` writes three copies of slide 04 into this folder, replacing only the chart's library and
script; `measure.py` renders each in the test harness's Chromium next to the Highcharts original and
writes `contact-sheet.png`. Every candidate draws the same data with the same geometry rules, read
from what Highcharts actually renders (DOM probe): plot top 10 px and a 50 px band below it for
labels and legend, points at category centres (35.7 px in from each edge), straight segments, bands
stacked Poor at the bottom to Excellent on top at 0.95 opacity, a legend listing Excellent first as
16 x 4 px strips, and the position marker at category 3.5 inside the Average band with its two-line
label box.

- `04-echarts.html`: Apache ECharts 6.1.0 with its SVG renderer (Apache-2.0).
- `04-chartjs.html`: Chart.js 4.5.1, the library slide 09 already uses (MIT, canvas).
- `04-svg.html`: inline SVG drawn by 48 lines of the slide's own script, no library.

Run from the repository root: `python3 docs/spikes/001-chart-library/build.py`, then
`python3 docs/spikes/001-chart-library/measure.py`. Open the candidate files over HTTP
(`python3 -m http.server 8000`) to see them as slides; `index.html` in this folder shows the three
side by side (http://127.0.0.1:8000/docs/spikes/001-chart-library/).

## Results (Chromium 148, macOS arm64, 1056 x 816 slide, chart area 428 x 426 px)

| | Highcharts 13.1.1 (today) | ECharts 6.1.0, SVG | Chart.js 4.5.1, canvas | Inline SVG, no library |
| --- | --- | --- | --- | --- |
| Chart pixels differing from Highcharts | 0 | 0.55% | 4.81% | 0.02% |
| Slide pixels differing from Highcharts | 0 | 0.12% | 1.28% | 0.00% |
| Where the difference is | | legend text, sub-pixel | text rendering and layout throughout | 7 x 18 px inside one legend word |
| Chart in the PDF | vector, text selectable | vector, text selectable | bitmap, no text layer | vector, text selectable |
| Page errors | none | none | none | none |
| Download (gzip) | 123 KB (library and 3 modules) | 370 KB | 71 KB (already loaded on slide 09) | none; the drawing code is part of the slide |
| Works offline, opened from disk | no (CDN) | no (CDN) | no (CDN) | yes |
| Licence | commercial licence may be required | Apache-2.0 | MIT | the template's own (MIT) |

Tuning it took to get there, kept because it is what a replacement must get right:

- ECharts first measured 2.97%: it skips axis labels when it judges them crowded (`axisLabel.interval:
  0` keeps all six) and a graphic group's `z` does not pass to its children, so the bands covered the
  marker's label box until each child had its own `z`.
- Chart.js first measured 8.98%: its plot area was 355.6 px tall against Highcharts' 366 (legend and
  tick padding decide it; tuned to 368.6). What remains is canvas text rendering, which a canvas
  cannot match, and the chart prints as a bitmap.
- Inline SVG first measured 0.46%, all of it in the legend row: Highcharts rounds the legend's
  position to whole pixels and sets its text half a pixel higher.
- A vision model, shown the contact sheet, reported smooth curves in Highcharts and angular edges in
  the others; the DOM shows Highcharts drawing straight segments (`L` commands, type `area`) and the
  inline SVG bands differ from it in 0 pixels. Measure before believing a picture.

## Verdict: VALIDATED for slide 04; two candidates match

- Inline SVG reproduces the Highcharts chart to within 0.02% of its pixels, prints as vector with
  selectable text, needs no library, CDN or licence, and works from a file opened on disk, which
  fits the template's "pure HTML and CSS, nothing to install" promise. The cost: about 50 lines of
  drawing code per chart type that the template owns, and no interactive features (the charts have
  tooltips and hover disabled today, so nothing is lost).
- ECharts matches to 0.55% with vector output and an open licence, at three times Highcharts'
  download and still a CDN at view time. It is the choice if a maintained library matters more than
  weight and offline use.
- Chart.js does not match closely enough and prints the chart as a bitmap.

Not built in this spike: slide 08's donut (outside labels with connectors, a centred HTML title).
Whichever approach is picked, the donut is the next slice, measured the same way against the
Highcharts original, and Highcharts leaves the template only when both charts are replaced.

## Decision

The maintainer chose inline SVG. Slide 04 draws its chart in inline SVG; re-measured after the
logo moved to the footer (a taller chart area), it differs from the Highcharts original in 0.02% of
the chart's pixels (ECharts 0.51%, Chart.js 4.82%). The Highcharts original of slide 04 is kept in
this folder as `04-highcharts.html`, the reference `build.py` and `measure.py` read. Slide 08's
donut follows in the same way, and Highcharts then leaves the template.

