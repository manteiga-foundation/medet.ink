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
| 04 | `04-Slide-Cybersecurity-Maturity.html` | Maturity score against peers, position marker | Highcharts stacked area |
| 05 | `05-Slide-Scope.html` | Scope and methodology | |
| 06 | `06-Slide-Risk-Matrix.html` | Risk matrix | |
| 07 | `07-Slide-Testing-Phases.html` | Testing phases | |
| 08 | `08-Slide-Findings-Overview.html` | Findings by severity | Highcharts pie |
| 09 | `09-Slide-Technical-Details.html` | One technical finding | Chart.js radar |
| 10 | `10-Slide-Proof-of-Concept.html` | Proof of concept | |
| 11 | `11-Slide-Team.html` | Engagement team | |
| 12 | `12-Slide-Capability-Statement.html` | Capability statement | |
| 13 | `13-Slide-Company-Overview.html` | Company overview | |
| 14 | `14-Slide-Vulnerabilities-Overview.html` | Vulnerabilities overview | |
| 15 | `15-Slide-Exploitability-Overview.html` | Exploitability overview | |
| 16 | `16-Slide-Appendix-A.html` | Appendix A | |

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
| Maturity bands (slide 04) | Poor `#8B5CF6`, Below Avg `#EF4444`, Average `#F59E0B`, Good `#10B981`, Excellent `#3B82F6` |

Severity colours: two sets are in use and not yet unified (a decision for the maintainer).
Critical `#DC2626` (3 archetypes) or `#EF4444` (6); High `#F97316`; Medium `#FBBF24` (2) or
`#F59E0B` (7); Low `#10B981`; Informational `#0EA5E9`.

## Print rules

- `@page { size: 11in 8.5in; margin: 0 }`; in print, `html, body` flow (`height: auto`,
  `overflow: visible`), never `height: 100%; overflow: hidden`, which truncates the print to the
  first page.
- Slides a hair under the page in print (8.49in) with `overflow: hidden` and
  `page-break-after: always`: an exact 8.5in rounds over the boundary and adds a blank page.
- Images in flex layouts need `flex: none`, a fixed height and `object-fit: contain`, or they
  stretch the page; long unbroken strings in flex children need `min-width: 0` and an overflow.
- Merged documents need the global override `html, body { height: auto; overflow: auto }` (the
  merge script appends it) or the combined report cannot scroll past its first slide.

## Build pipeline

1. Edit an archetype.
2. `python3 scripts/merge_slides.py`: extracts each archetype's styles, scripts and body into
   `reports/combined_report.html` and the identical `reports/merged_report.html`.
3. `python3 scripts/make_pdf.py`: serves the repository on a free port, prints
   `reports/merged_report.html` with Playwright to `reports/final_report.pdf`.
4. `python3 scripts/make_images.py`: screenshots each archetype at 1056 x 816 into
   `assets/slide_NN.png`.
5. The README's demo GIF from the thumbnails:

```
ffmpeg -framerate 1 -i assets/slide_%02d.png \
  -vf "scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  -loop 0 assets/demo.gif
```

Steps 3 and 4 currently produce output without the Highcharts charts (known defect 3).

## Tests

`python3 -m unittest discover -s tests -v`; about 25 s once the third-party cache is filled. The
harness (`tests/harness.py`) serves the repository over HTTP on a free port, drives a headless
Chromium with a regular Chrome user agent, and answers third-party requests from `tests/.cache`.
Each test below was shown to fail against a deliberate break applied to a copy of the repository
(`MEDET_ROOT=<copy>`); the break is noted after "fails when".

- `tests/test_archetypes.py` - every archetype in Chromium at 1056 x 816:
  - numbered from 01 without gaps (fails when 17 is missing and 18 exists);
  - exactly one `.slide` of 1056 x 816 px (fails when a slide is 9.5in tall: 1056 x 912);
  - prints to exactly one 792 x 612 pt page (fails on the same break: two pages);
  - content stays inside the slide, within 2 px, except the known defects (fails when a 900 px
    block that does not shrink is added: 871 px over; a block that may shrink is absorbed by the
    flex column and proves nothing);
  - no uncaught page errors (fails when a script calls an undefined function, or a chart library
    does not load);
  - every chart the archetype's script creates is drawn: painted canvas pixels for Chart.js,
    series for Highcharts (fails when Chart.js is not loaded; a canvas keeps a 300 x 150 default,
    so canvas size alone proves nothing);
  - expected failure: the known footer overflow on 09 and 16.
- `tests/test_maturity_chart.py` - slide 04's bands, read from the drawn chart: Poor at the bottom,
  then Below Avg, Average, Good, Excellent on top, at every category (fails when the series array
  is reversed).
- `tests/test_combined_report.py` - the combined report:
  - the committed file is byte for byte what `merge_slides.py` produces from the archetypes
    (fails when an archetype is edited without regenerating);
  - one slide per archetype (fails when an archetype is added without regenerating: 16 != 17);
  - prints one 792 x 612 pt page per slide (fails when the last archetype's `.slide` is 9.5in
    tall, which in the merged stylesheet applies to every slide);
  - content stays inside each slide, except the known defects (fails on the 900 px block);
  - each slide draws the charts its archetype draws on its own, except the known defects (fails
    when slide 09's canvas id is changed in the combined report);
  - expected failures: the known overflow (06, 09, 16), the known wrong charts (04, 08), page
    errors, duplicate ids.
- `tests/test_links.py` - no browser:
  - every local `href`/`src` on the landing page, the viewer (including its scripted slide list)
    and the combined report resolves to a file (fails when a thumbnail is deleted, or a script
    points at a missing path);
  - the landing page links every archetype and its thumbnail (fails when an archetype is added
    without a gallery card);
  - the social preview: `og:url`/`twitter:url` are https://medet.ink/, matching `CNAME`, and
    `og:image`/`twitter:image` are committed files (fails when the image is renamed).

## Known defects

Each is held by an expected-failure test; a fix removes it from the test's known set.

1. Combined report charts. `merge_slides.py` collects every `<script>` of each archetype into
   `<head>` and also keeps it in the slide's body, so inline chart scripts run twice. The head copies
   run before any slide exists (Highcharts error #13, twice) after declaring `const chartData`; the
   body copy of slide 04 then throws `Identifier 'chartData' has already been declared` and the
   maturity chart is never drawn. Slide 08's pie is drawn into the first `id="chart-container"`,
   which is slide 04's (both archetypes use that id), so slide 04 shows the pie and slide 08 shows
   no chart. Chart.js reports `Canvas is already in use` on slide 09 (its chart is drawn).
   `reports/final_report.pdf` page 4 carries none of the maturity chart's text (legend, categories)
   where a print of the archetype does.
2. Overflow. Slides 09 and 16 reach 82 px and 75 px past the page: the footer starts at 863 px
   and 854 px on an 816 px page and is clipped, on screen and in print. In the combined report the
   Risk Matrix card on slide 06 is 969 px tall (it fits in its own archetype): 389 px over.
3. Headless scripts. `make_pdf.py` and `make_images.py` launch Chromium with its default user
   agent; code.highcharts.com answers `HeadlessChrome` with 403 (Chromium reports
   `ERR_BLOCKED_BY_ORB`), so Highcharts is undefined and slides 04 and 08 render without charts.

## Decisions and history

- Maturity chart order: the bands stack Poor at the bottom to Excellent on top. Highcharts draws
  the first series of a stack on top, so the array reads Excellent first. Commits 7d18c0a to
  37b0ed2 flipped it four times by reasoning; the test now measures it.
- The third-party cache in `tests/.cache` exists because code.highcharts.com refused the test
  browser (403) and then rate-limited it (429) within one afternoon of runs; the template itself
  still loads its libraries from the CDNs.
