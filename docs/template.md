# medet.ink template notes

Working notes on the template as built: the archetypes, the design tokens, the print rules, the
build pipeline, the tests and the known defects. The README is for the template's users; the
working contract is `AGENTS.md`.

## Archetypes

| NN | File | Content | Charts |
| --- | --- | --- | --- |
| 01 | `01-Slide-Cover.html` | Cover | |
| 02 | `02-Slide-Table-of-Content.html` | Table of contents | |
| 03 | `03-Slide-Executive-Summary.html` | Executive summary | |
| 04 | `04-Slide-Cybersecurity-Maturity.html` | Maturity score against peers, position marker | inline SVG stacked area |
| 05 | `05-Slide-Scope.html` | Scope and methodology | |
| 06 | `06-Slide-Risk-Matrix.html` | Risk matrix | |
| 07 | `07-Slide-Testing-Phases.html` | Testing phases | |
| 08 | `08-Slide-Findings-Overview.html` | Findings by severity | inline SVG donut, read from the stat boxes |
| 09 | `09-Slide-Technical-Details.html` | One technical finding | Chart.js radar |
| 10 | `10-Slide-Proof-of-Concept.html` | Proof of concept | |
| 11 | `11-Slide-Team.html` | Engagement team | |
| 12 | `12-Slide-Capability-Statement.html` | Capability statement | |
| 13 | `13-Slide-Vulnerabilities-Overview.html` | Vulnerabilities overview | |
| 14 | `14-Slide-Exploitability-Overview.html` | Exploitability overview | |
| 15 | `15-Slide-Appendix-A.html` | Appendix A | |
| 16 | `16-Slide-Company-Overview.html` | Company overview | closing page |

Every archetype is a complete HTML document: `@page { size: 11in 8.5in; margin: 0 }`, a reset with
`print-color-adjust: exact`, one `.slide` (11in x 8.5in, `overflow: hidden`), a left accent bar
(`.slide::before`), a faint 48 px grid (`.slide::after`, no pointer events), then header, content
and footer (confidentiality block on the left, page indicator `NN / TOTAL` on the right).

### Page patterns

- Finding page: a floating ID tab, centred title, three columns (metadata, radar chart, vertical
  risk-score bar), then two columns (description, remediation).
- Replication page: numbered steps beside a dark raw request and response block, one per finding.
- Evidence page: one large screenshot per page, framed with browser chrome, captioned.

## Design tokens

Lift these from the archetypes; do not restyle.

| Token | Value |
| --- | --- |
| Text font | Montserrat (Google Fonts) |
| Code font | Fira Code |
| Ink | `#0A2540` |
| Accent | `#0A4B9F` |
| Brand red | `#D82018` (header gradient `#D82018` to `#0A4B9F`) |
| Left accent bar | `linear-gradient(180deg, #0A4B9F 0%, #4781C3 35%, #D82018 100%)`, 8 px |
| Slate text | `#64748B`, `#94A3B8` |
| Card | white, radius 12 px, border `#E2E8F0`, shadow `0 8px 30px rgba(0,0,0,0.04)` |
| Slide frame (after the cover) | no header; content padding `0.15in 0.8in 0`, so titles start at 0.15in (the letters about 20 px from the edge); the logo is a 90 x 24 px placeholder (`.footer-logo`, `#F1F5F9`, dashed `#94A3B8`) first in the footer's bottom row, beside the brand line |
| Maturity bands (slide 04) | Poor `#8B5CF6`, Below Avg `#EF4444`, Average `#F59E0B`, Good `#10B981`, Excellent `#3B82F6` |

Severity colours, one palette on every slide (the Tailwind 500 tier): Critical `#EF4444`, High
`#F97316`, Medium `#F59E0B`, Low `#10B981`, Informational `#0EA5E9`. A severity-coded element
carries its severity as a class (`critical`, `high`, `medium` or `med`, `low`, `info`, alone or
prefixed `sev-`, `color-`, `rsk-`). Amber text on white uses `#D97706` for legibility (slide 08's
pie label). The risk matrix's effort scale (slide 06) uses the blues `#4781C3`, `#0A4B9F` and ink
`#0A2540`, so no severity colour means anything else there.

## Landing page

`index.html`, design A of spike 002 (Terminal Paper): cream paper `#F2EFE6` with a faint 24 px
grid, ink `#2B2B2B`, soft ink `#5B5850`, accents sage `#8FB3A8` (primary button), peach `#D9A877`
(secondary), lavender `#A99BC2` (focus ring), status LED `#3E9B4F`; Space Grotesk for headings and
text, IBM Plex Mono for labels; 2 px ink borders with hard 4 px offset shadows. HTML and CSS with
Google Fonts and one inline script, no external script. The copy presents the template for any
report or presentation; the sample content is a fictional security assessment.

The navigation band carries the wordmark with a byline beside it on its baseline, "By Manteiga
Foundation" at 11 px in soft ink, sentence case (the wordmark is 14 px), shown at every size; the
status read-outs follow, then GitHub.

The hero plays the archetypes as a slideshow in the window frame: the title bar shows `NN / 16`, the
slide name and a PLAYING/PAUSED LED; slides wipe in (left to right forward, right to left back,
0.55 s); the pagination strip has prev and next keys, 16 ticks (past ones sage, the current one
filling over its 4.5 s) and a pause key. It holds while a mouse points at it or keyboard focus is
inside it, does not autoplay under reduced motion, and moves with the arrow keys. It shows the
gallery's own thumbnails, the first in the markup and each next one fetched a slide ahead; without
script the first slide shows alone. On phones the keys are 40 px and the ticks only indicate.
Buttons: View Full Report, Download PDF, Download HTML (`reports/medet-ink-template.zip`), GitHub,
in a 2 x 2 block.

## Print rules

- `@page { size: 11in 8.5in; margin: 0 }`; in print, `html, body` flow (`height: auto`,
  `overflow: visible`), never `height: 100%; overflow: hidden`, which truncates the print to the
  first page.
- Slides a hair under the page in print (8.49in) with `overflow: hidden` and
  `page-break-after: always`: an exact 8.5in rounds over the boundary and adds a blank page.
- Images in flex layouts need `flex: none`, a fixed height and `object-fit: contain`, or they
  stretch the page; long unbroken strings in flex children need `min-width: 0` and an overflow.
- No box shadows in print: every archetype's stylesheet ends with `@media print { * { box-shadow:
  none !important; filter: none !important; } }`. Chromium writes a blurred CSS shadow into the PDF
  in a form macOS's PDF engine (Preview, Quick Look) draws as a hard-edged grey box behind the card
  or badge; cards keep their 1 px borders. A hairline is an `outline` or a border, never an inset
  shadow, so it survives the print rule.
- On screen an archetype sits inside `body { padding: 0.5in }`: a capture of the slide is a capture
  of the `.slide` element, never of the viewport.

## Charts

- Slides 04 and 08 draw their charts in inline SVG with the slide's own script, no library (spike
  001); slide 08's donut reads its counts from the stat boxes under it, sizes its ring so every
  label fits, and draws a grey ring when every count is 0. An SVG chart's container carries `data-chart="name"` (unique across the report); its script
  finds the container by that attribute, keeps its variables inside a function, and draws inside
  `document.fonts.ready.then(...)`. Band polygons carry `data-series` with the band's name.
- Chart.js 4.5.1 (slide 09's radar) loads from jsDelivr pinned to a version, never an unpinned
  "latest". The template loads no Highcharts.
- Charts are created inside `document.fonts.ready.then(...)`. A chart measures its text when it
  draws; drawn before Montserrat loads, it keeps a fallback font's layout (canvas text, label
  placement and truncation) on screen and in print.
- Chart containers have ids unique across archetypes (`chart-04`, `chart-08`, `radarChart`).

## Build pipeline

1. Edit an archetype.
2. `python3 scripts/merge_slides.py`: one document from the archetypes. Each archetype's stylesheet
   is nested under a wrapper class for its slide (`.archetype-NN`, CSS nesting), so no rule reaches
   another slide; its `html`/`body` rules become the wrapper's inherited typography, and typography
   every archetype shares also goes on the document's `html, body` (chart libraries measure text in
   elements they attach to the body). `@import` is hoisted, `@page` declared once, external scripts
   load once in `<head>`, inline scripts stay with their slide. Writes
   `reports/combined_report.html` and the identical `reports/merged_report.html`.
3. `python3 scripts/make_pdf.py`: prints `reports/merged_report.html` to `reports/final_report.pdf`.
4. `python3 scripts/make_images.py`: captures each archetype's `.slide` into `assets/slide_NN.png`.
5. The README's demo GIF from the thumbnails, one second per slide:

```
ffmpeg -framerate 1 -i assets/slide_%02d.png \
  -vf "scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  -loop 0 assets/demo.gif
```

6. `python3 scripts/make_template.py`: zips the archetypes, the viewer, the combined report, README
   and LICENSE into `reports/medet-ink-template.zip` (the landing page's Download HTML). Run it after
   any change to those files; `tests/test_template_download.py` fails on a stale zip.
7. `python3 scripts/stamp_landing.py`: stamps the landing page's links to thumbnails, slides and
   reports with `?v=` and the first 8 hex of each file's SHA-256. GitHub Pages lets browsers keep a
   copy for four hours (`cache-control: max-age=14400`), so after the reorder a returning visitor saw
   the old `slide_13.png` (then the company overview) and the old 04 and 08 thumbnails without their
   charts. A changed file now gets a new address; run this last, after any step above.

Every script works on the folder it runs in: from the repository root it builds the sample report;
from a report folder laid out the same way (`archetypes/`, `reports/`, `assets/`) it builds that
report. Client reports live in `projects/<Client>/<Report>/`, which git ignores, and are built
with these scripts by path (`python3 ../../../scripts/merge_slides.py` from the report folder).
The tests that apply to any report run against one with `MEDET_ROOT`: `test_archetypes`,
`test_layout`, `test_print`, `test_chart_fonts`, `test_severity_palette`, `test_combined_report`
(30 checks passed against a copy of the sample laid out as a client report). A report folder has
no `scripts/` of its own (`REPORT_FOLDER` in the harness): there the checks that only prove a probe
found the sample's content (at least three charts, more than ten titles, more than twenty
severity-coded elements, the effort levels) do not apply, so a partial report is judged on what it
holds. In the repository and its copies they still apply (fails when the charts of 04, 08 and 09
are unmarked in a copy).

Steps 3 and 4 share `scripts/browser.py` with the tests: the repository served on a free port, a
regular Chrome user agent, chart animations off (each library is configured the moment its script
defines it), web fonts loaded before capture.

## Tests

`python3 -m unittest discover -s tests -v`; 60 tests, about 115 s once the third-party cache is
filled. The harness (`tests/harness.py`) serves the repository, drives Chromium through
`scripts/browser.py`, and answers third-party requests from `tests/.cache`. Each test was seen
failing for the right reason before it passed: against the defect it was written for, or against a
deliberate break applied to a copy of the repository (`MEDET_ROOT=<copy>`); noted after "fails
when".

- `tests/test_archetypes.py` - every archetype in Chromium:
  - numbered from 01 without gaps (fails when 17 is missing and 18 exists);
  - exactly one `.slide` of 1056 x 816 px (fails when a slide is 9.5in tall: 1056 x 912);
  - prints to exactly one 792 x 612 pt page (fails on the same break: two pages);
  - content stays inside the slide, within 2 px (failed on 09 and 16: 82 and 75 px; fails when a
    900 px block that does not shrink is added; a block that may shrink is absorbed by the flex
    column and proves nothing);
  - no uncaught page errors (fails when a script calls an undefined function or a library is
    missing);
  - every chart the archetype's script creates is drawn: painted canvas pixels, shapes in each SVG chart
    (fails when Chart.js is not loaded; a canvas keeps a 300 x 150 default, so size proves nothing);
  - each gallery thumbnail is the archetype's slide, within 0.1% of its pixels (failed on 04 and 08
    without charts, then on all 16 offset by the screen padding).
- `tests/test_chart_fonts.py` - with the web fonts held back until the page's scripts ran, every
  chart redrawn with the fonts loaded moves nothing, compared chart by chart (failed on 09 for
  Chart.js canvas text, then on 04 and 08 for Highcharts label layout: 0.13% and 0.30% of the
  slide; an SVG chart drawn before the fonts moves 0.51% of its area). SVG charts are redrawn by
  running their script again.
- `tests/test_maturity_chart.py` - slide 04's bands, read from the drawn SVG polygons: Poor at the
  bottom up to Excellent on top, at every category (fails when the bands array is reversed; failed
  before the chart was SVG: no polygons).
- `tests/test_combined_report.py` - the combined report:
  - the committed file is byte for byte what `merge_slides.py` produces (fails when an archetype is
    edited without regenerating);
  - one slide per archetype (fails when an archetype is added without regenerating);
  - every slide looks exactly like its archetype rendered alone, within 0.1% of its pixels (failed
    on all 16: 3 to 24%);
  - prints one 792 x 612 pt page per slide (fails when the last archetype's `.slide` is 9.5in tall);
  - the sample PDF has the text of a fresh print, page by page (failed on page 4);
  - content stays inside each slide (failed on 06, 09 and 16);
  - each slide draws the charts its archetype draws (failed on 04 and 08);
  - no page errors (failed: four), element ids unique (failed: `chart-container`).
- `tests/test_consistency.py` - no browser: every footer reads "Property of ACME Consulting |
  acmecyber.com" (failed on 09); no other firm is named (failed on 09); each page number is the
  slide number out of the archetype count (failed on all 16); the table of contents lists pages 02
  to 16 under each archetype's title (failed); the README and landing page state the archetype
  count (failed on the README's 13); the archetypes run in the agreed order, closing with the
  company overview (failed while it was 13). Every IPv4 address in the archetypes, README and landing page lies
  in an RFC 5737 documentation range (failed on 05 and 16: sixteen 10.0.x.x addresses); no other
  organisation is named (failed on 16: BICSA).
- `tests/test_links.py` - no browser: local links on the public pages resolve (fails when a
  thumbnail is deleted or a script points at a missing path); chart libraries load from jsDelivr
  pinned to a version (failed on code.highcharts.com and an unpinned Chart.js); the landing page
  links every archetype and thumbnail; the viewer and the gallery list the archetypes in order, each
  card with its own thumbnail (failed when 13 to 16 were renamed); the social preview points at committed files on medet.ink; no page loads or calls Highcharts (fails
  with the Highcharts slide 08 restored).
- `tests/test_repository.py` - no browser: no `.DS_Store` is tracked (failed: one at the root);
  every file under `assets/`, `reports/` and `img/` is generated or linked from the README, the
  landing page or the viewer (failed on `assets/sample-report.pdf` and `reports/data_uri.txt`, and
  on an unlinked image when `img/` joined the check); `projects/`
  is ignored and nothing under it is tracked, since client reports never enter this public
  repository (failed: not ignored).
- `tests/test_severity_palette.py` - every severity-coded element and chart point uses the palette
  colour of its severity (failed on 06 and 08: eleven elements); a slide that shows severities uses
  neither `#DC2626` nor `#FBBF24` (failed on 06, 08, 09); the effort levels use no severity colour
  (failed on 06's MEDIUM effort, `#10B981`, the colour of Low).
- `tests/test_chart_labels.py` - no chart label is shortened with an ellipsis (failed on 08 under
  Highcharts: "Medi..." and "L...").
- `tests/test_findings_chart.py` - slide 08's donut: each label reads the name, count and share of
  the stat boxes under it, the centre shows their total, and the labels stay inside the chart and
  apart (failed under Highcharts: Low's label empty, Medium shortened, Critical 3 px above the
  chart).
- `tests/test_layout.py` - every slide after the cover starts its title at 0.15in (failed on 02 to 08,
  11, 12 and 14 to 16: 75, 88 or 90 px; then on all thirteen at 0.4in), carries one logo in its footer's bottom row, centred on
  the brand line and aligned with the footer text (failed on all fifteen: none), and no logo above
  the footer (failed on eleven).
- `tests/test_print.py` - in print, nothing in a slide casts a box shadow (failed on 13 slides);
  the sample PDF drawn by CoreGraphics (`sips`, as Preview draws it) shows no flat area darker
  than the screen render, in 12 px blocks (failed on 12 pages, worst on 12: 44 levels darker behind
  the Past Performance badge and the cards; skipped where `sips` is missing).
- `tests/test_landing.py` - the landing page loads no external script (failed: the Tailwind CDN), its
  title, headline and social titles do not limit it to cybersecurity (failed: "Pentest",
  "Cybersecurity"), and at 1440 x 900, 1280 x 800 and 390 x 844 it has no sideways scroll, broken
  image or page error (fails when a 1600 px strip and a missing image are added). The hero shows
  every archetype in report order instead of the GIF (failed: the GIF); the slideshow pages with
  prev, next, the ticks and the arrow keys, wrapping from 01 to 16, and holds under reduced motion
  (fails when reduced motion is ignored); it advances after one interval on a fake clock, holds
  while pointed at and on the pause key (fails when the hover is ignored: it reached 05); one link
  downloads `reports/medet-ink-template.zip` (failed: absent). Every link to a file under
  `archetypes/`, `assets/` or `reports/` carries its content version (failed: 67 links without
  one); every gallery card and slideshow slide is named by its slide's title, the cover's card
  "Cover Page" (failed on 04, 05, 09 and 11: "Cybersecurity Maturity", "Scope", "Technical Details",
  "The Team"). The band credits the foundation as
  a byline: "By Manteiga Foundation", at most 11 px and smaller than the wordmark, within 12 px of
  it and visible at the three sizes (failed: "MANTEIGA FOUNDATION" in capitals, hidden on phones).
- `tests/test_template_download.py` - the zip holds the 16 archetypes, the viewer, the combined
  report, README and LICENSE, byte for byte as in the repository (failed: absent; fails when a file
  changes without `make_template.py`), and every relative link inside it resolves inside it.
- `tests/test_scripts.py` - a report folder with one slide, built by `merge_slides.py`,
  `make_pdf.py` and `make_images.py` run from it, gets its own one-page PDF and 1056 x 816
  thumbnail, and the repository's are left alone (failed: the PDF and thumbnails were written to
  the repository).
- `tests/test_demo_gif.py` - no browser: the demo GIF has one frame per archetype, each within a
  mean difference of 6 of its thumbnail (the GIF is a dithered copy; failed at 19 to 45 with the old
  thumbnails, 0.6 to 0.9 when fresh).

## Known defects

None open. Fixed and held by the tests above: charts missing or on the wrong slide in the combined report and
the sample PDF; every combined slide drifting from its archetype through shared CSS; footers clipped
on 09 and 16 and the Risk Matrix in the combined report; generated PDF and thumbnails without
Highcharts charts; thumbnails offset and cropped by the screen padding; chart layout depending on
font timing; another firm and out-of-sequence page numbers on some slides; a table of contents that
did not match the report; two severity palettes; card and badge shadows printing as grey boxes; slide 08's donut shortening its labels.

## Decisions and history

- Maturity chart order: the bands stack Poor at the bottom to Excellent on top. Highcharts draws
  the first series of a stack on top, so the array reads Excellent first. Commits 7d18c0a to
  37b0ed2 flipped it four times by reasoning; the test now measures it.
- Slide 09 fits its page with tighter spacing (top padding 0.25in, finding card padding 20 px and
  margin 16 px, radar 250 px); slide 16's map placeholder is 300 px tall (was 380 px). The table of
  contents rows have 6 px padding and the card 32 px, so fifteen rows fit.
- The third-party cache in `tests/.cache` exists because code.highcharts.com refused the test
  browser (403) and then rate-limited it (429) within one afternoon of runs.
- The logo moved from a header above the title into the footer (maintainer's decision): some slides
  had no logo and others a 45 px block, which left the titles at three different heights. Titles now
  start at 0.4in on every slide, 37 to 52 px higher; slide 09, which had no header, moved its finding
  card up 0.1in to make room for the footer's logo row. The cover keeps its logos. The maintainer
  then halved the remaining gap above the titles (43 to 49 px to the letters, now 19 to 25 px):
  titles start at 0.15in, the same top margin as slide 09's card.
- Landing page: the maintainer chose design A of spike 002 from three directions after their two
  retro computing references, and asked that the wording not limit the template to cybersecurity.
  The page dropped the Tailwind CDN script; the 16:9 claim in the Teams and Zoom feature (11 x 8.5
  is 1.29:1) was replaced with an accurate sentence.
- Hero slideshow instead of the GIF (the maintainer's request): one inline script, so the landing
  page carries its own script but loads none. Images at first load fell from 5.97 MB (the GIF and
  the gallery, which Chrome's lazy loading fetches at once) to 4.64 MB; the slideshow reuses the
  gallery's thumbnails. Download HTML is a reproducible zip (`scripts/make_template.py`, fixed
  dates, 100 KB) of the template folder, linked by relative path like the PDF.
- Severity palette: the Tailwind 500 tier, measured in OKLCH. Its five colours span 0.132 in
  lightness against 0.260 for the alternative (`#DC2626`, `#FBBF24`), adjacent severities stay
  0.096 to 0.104 apart (about five times a just-noticeable difference), and amber-400 text on white
  (1.67:1) became amber-500 (2.15:1). Trade-off: white text on `#EF4444` is 3.76:1 against 4.83:1
  on `#DC2626`, so slide 10's status pill (a status, not a severity, in small text) keeps `#DC2626`.
- Highcharts removed (maintainer's decision after spike 001): both charts are inline SVG, vector in
  print, with no library, CDN or licence. Slide 04 matches its Highcharts original to 0.02% of the
  chart's pixels; slide 08's donut was redrawn to show every label whole, which Highcharts did not.
