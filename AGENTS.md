# Working on medet.ink

This file is the working contract for anyone, person or agent, who changes this repository. It is
short on purpose: the README describes the template to its users, `docs/template.md` holds the
notes on what is built, and this file explains how we build it.

## What medet.ink is

An open-source suite of HTML report archetypes for cybersecurity deliverables (penetration tests,
assessments), published at https://medet.ink from this repository through GitHub Pages. Each
archetype is a standalone HTML page that prints to exactly one 11 x 8.5 in landscape page; the
combined report assembles them into one document that prints to a paginated PDF.

Two audiences, two rules:

- Template users get pure HTML and CSS: open a file, edit it, print it. Nothing we add may require
  a build step, a package manager or a server to use the template.
- Maintainers have tooling (Python and Playwright, under `scripts/` and `tests/`) to generate the
  combined report, the PDF and the gallery images, and to verify them. That tooling is never a
  requirement for users.

The sample content is fictional (ACME). Real client data never enters the repository; network
addresses in samples use the documentation ranges of RFC 5737 (192.0.2.0/24, 198.51.100.0/24,
203.0.113.0/24), mapped consistently across the report.

Stack: HTML5 and print CSS; charts in inline SVG drawn by each slide's own script, and Chart.js
from a CDN for one radar; Google Fonts (Montserrat, Fira Code); the landing page uses the Tailwind
CDN. Tooling: Python 3.9 or newer, Playwright for Python, pypdf; the tests use the standard
library's `unittest`.

## Vocabulary (fixed, use these words)

- **Archetype** - one standalone slide file, `archetypes/NN-Slide-Name.html`, numbered from 01
  without gaps. The build scripts and the tests glob this pattern.
- **Slide** - the `.slide` element: one printed page, 11 x 8.5 in = 1056 x 816 CSS px = 792 x 612
  PDF points. Exactly one per archetype.
- **Combined report** - `reports/combined_report.html`, every archetype in one document, generated
  by `scripts/merge_slides.py`, which also writes the identical `reports/merged_report.html` that
  `scripts/make_pdf.py` prints. Never edited by hand.
- **Sample PDF** - `reports/final_report.pdf`, printed from the combined report; the landing page's
  Download PDF.
- **Gallery** - the archetype cards on the landing page with their thumbnails
  `assets/slide_NN.png` (`scripts/make_images.py`), plus `assets/demo.gif` in the README.
- **Landing page** - `index.html` at the root, served at https://medet.ink (domain in `CNAME`).
- **Viewer** - `archetypes/index.html`, an iframe viewer that steps through the archetypes.
- **Derived artifact** - anything generated from the archetypes: the combined reports, the sample
  PDF, the thumbnails, the GIF. Regenerated in the same change as the edit that affects it.
- **Known defect** - a measured problem, recorded as an expected-failure test and listed in
  `docs/template.md`. Fixing one is a slice of its own.

## How we work: the methodology

Every slice follows the same loop. Do not skip steps because a change looks small; the small ones
(a series order, a CSS height, a duplicated id) are the ones that broke the report.

1. **RED first.** Write the failing test before the change, in `tests/`, against the rendered page
   in real Chromium: geometry from the DOM, chart state from the drawn SVG or the chart library,
   pagination from the printed PDF. Run it and see it fail for the right reason. A test for
   behaviour that already exists cannot fail first, so prove that it can fail: apply a deliberate
   break to a copy of the repository, run the suite against the copy with `MEDET_ROOT=<copy>`, and
   record in `docs/template.md` what the test fails on.
2. **GREEN.** The smallest change that passes, then refactor with the tests still green.
   Regenerate every derived artifact the change touches: `merge_slides.py` always after an
   archetype edit, `make_pdf.py` and `make_images.py` when the printed or pictured result changed.
3. **Gates before "done":** `python3 -m unittest discover -s tests -v` passes, with expected
   failures only for the known defects listed in `docs/template.md`. An unexpected success means a
   known defect was fixed: remove it from the known set in the same change. A page that opens in a
   browser is not verification.
4. **Look at it.** Slides at 1056 x 816 (`make_images.py`), the printed PDF page by page, and the
   landing page at 1440 x 900, 1280 x 800 and 390 x 844 when it changes. Inspect by eye or with a
   vision model; treat what you see as a lead and confirm it with a DOM probe before changing code.
   Vision models misjudge order, spacing and clipping; the tests measure them.
5. **Document.** `docs/template.md` (archetypes, tokens, the test list with what each test fails
   on, known defects, decisions), the README when what users see changes (gallery, counts,
   instructions), and "Where things stand" below. One commit per slice, with a message that says
   what changed and why. Never push or rewrite history unless the maintainer asks.
6. **Report honestly:** what changed, what is verified (counts and commands), one real finding or
   trade-off, next candidates. Plain text, no emojis.

When something is uncertain (which way does the chart stack? which colour? which layout?), do not
argue it: **measure it** (a probe in Chromium, with the numbers in the report) or **render every
candidate in context** (each option as a real slide, side by side) and let the maintainer pick.
Larger questions get a spike: a throwaway experiment outside the repository, written up in
`docs/spikes/NNN-name.md` with Question, Approach, Results (a table of measurements) and Verdict.

Why this rule exists here: four consecutive commits flipped the maturity chart's series order by
reasoning about the array (Highcharts, which drew the chart then, put the first series of a stack
on top). One measurement of the rendered bands settles it, and `tests/test_maturity_chart.py` now
holds the answer.

## Commands

```
python3 -m pip install -r requirements-dev.txt   # maintainers only: Playwright for Python, pypdf
python3 -m playwright install chromium

python3 -m unittest discover -s tests -v          # the gate (about a minute)
MEDET_ROOT=/path/to/copy python3 -m unittest discover -s tests   # the suite against a copy
python3 scripts/merge_slides.py                   # archetypes -> reports/combined_report.html (+ merged_report.html)
python3 scripts/make_pdf.py                       # reports/merged_report.html -> reports/final_report.pdf
python3 scripts/make_images.py                    # archetypes -> assets/slide_NN.png
python3 -m http.server 8000                       # preview the site at http://127.0.0.1:8000
```

Run everything from the repository root. The demo GIF recipe is in `docs/template.md`.

## Conventions that tests depend on

- One `.slide` per archetype, 11in x 8.5in, with `@page { size: 11in 8.5in; margin: 0 }`; content
  stays inside it (the overflow probe allows 2 px). In print, slides sit a hair under the page
  (8.49in) with `overflow: hidden` and `page-break-after: always`, so no blank trailing pages.
- Archetype files are `NN-Slide-Name.html`, numbered from 01 without gaps, in the running order the
  consistency test lists (the company overview closes the report). A new or moved archetype also
  needs its gallery card and `assets/slide_NN.png` on the landing page, its place in the viewer's
  list, and regenerated derived artifacts; the tests check the viewer and the gallery follow.
- Slides after the cover have no header: titles start at 0.15in, and the logo is a `.footer-logo`
  placed first in the footer's bottom row, centred on the brand line. The cover keeps its logos.
- Charts are drawn by the archetype's own script inside `document.fonts.ready.then(...)`. An inline
  SVG chart draws into a container with `data-chart="name"` (unique across the report), finds it
  through that attribute, and keeps its variables inside a function so it can run twice; a Chart.js
  chart is created with `new Chart(`. The tests count the containers and calls, expect as many
  charts drawn, and redraw them to check that a late font changes nothing.
- Chart.js loads from jsDelivr pinned to a version (`chart.js@4.5.1`), never an unpinned "latest".
  No page loads Highcharts.
- The combined report is one document. `merge_slides.py` scopes each archetype's CSS to its slide,
  but ids and inline-script globals still share one namespace: new archetypes use ids unique to the
  slide (`chart-04`) and keep script variables out of the global scope.
- A capture of a slide is a capture of its `.slide` element: on screen an archetype sits inside
  0.5in of body padding. `scripts/browser.py` is the one browser setup for the scripts and the
  tests (regular Chrome user agent, chart animations off, fonts loaded); the tests also serve
  third-party files from `tests/.cache` (delete the folder to refresh it).
- Every slide's footer reads "Property of ACME Consulting | acmecyber.com" and its page indicator
  `NN / TOTAL` with TOTAL the archetype count; the table of contents lists pages 02 onward under
  each archetype's `<title>`; the README states the archetype count. Adding an archetype means
  updating all of them; the tests say where.
- Severity colours come from one palette (Critical `#EF4444`, High `#F97316`, Medium `#F59E0B`,
  Low `#10B981`, Informational `#0EA5E9`), and a severity-coded element carries its severity as a
  class (`critical`, `high`, `medium`/`med`, `low`, `info`, alone or prefixed `sev-`, `color-`,
  `rsk-`), which is how the palette test finds it.
- Every IPv4 address in the archetypes, the README and the landing page lies in an RFC 5737 range,
  and no real organisation is named; the tests check both.
- Public pages link only to files in the repository, by relative path; the social preview
  (`og:image`, `twitter:image`) is an absolute https://medet.ink/ URL of a committed file. Every
  file under `assets/` and `reports/` is generated or linked, and no `.DS_Store` is tracked.
- Commit in a separate step after reading the test counts; never chain a test run through `grep`
  into `git commit` (grep exits 0 when it prints failures).

## Map

```
index.html                       landing page: gallery, social preview tags (Tailwind CDN)
archetypes/NN-Slide-*.html       the archetypes (16 today)
archetypes/index.html            the viewer (iframe; its slide list lives in its script)
reports/combined_report.html     generated: every archetype in one document (and merged_report.html)
reports/final_report.pdf         generated: the sample PDF
assets/slide_NN.png, demo.gif    generated: gallery thumbnails, README demo
scripts/merge_slides.py          archetypes -> combined report
scripts/make_pdf.py              merged report -> PDF (Playwright)
scripts/make_images.py           archetypes -> thumbnails (Playwright)
scripts/browser.py               the browser setup the scripts and the tests share
tests/harness.py                 Chromium for the tests, third-party cache, DOM and image probes
tests/test_*.py                  the suite (listed in docs/template.md)
docs/template.md                 notes on what is built: archetypes, tokens, charts, tests, decisions
docs/spikes/                     measured experiments and their verdicts
CNAME                            medet.ink, the GitHub Pages custom domain
```

## Standing decisions (do not re-litigate without the maintainer)

- Pure HTML and CSS for users, with no build step; tooling stays on the maintainer's side.
- Executive-ready tone: formal and concise, no emojis in any public text (README, pages, reports,
  commit messages).
- Printable, non-interactive report layouts: no tabs or accordions in report content (a PDF cannot
  open them); vertical lists and tables instead.
- Explicit empty states: a severity with no findings keeps its row and states that none were
  identified, so every table stays a reusable template.
- Evidence: one screenshot per page, framed, captioned and naming the finding it supports, never
  shrunk into grids; every finding has its own replication page (numbered steps beside the raw
  request and response); real evidence before mock-ups; each finding labelled CONFIRMED, LIKELY or
  HYPOTHESIS at the level its evidence supports.
- Sample data is fictional and sanitized.
- Design tokens are lifted from the archetypes, never restyled from scratch (`docs/template.md`).
- Charts are inline SVG drawn by the slide's own script (spike 001); no Highcharts.
- The landing page stays sleek and minimal: a slim navigation band, concise text.
- Published from `main` through GitHub Pages with the `CNAME` file.

## Where things stand (update when it changes)

Done: sixteen archetypes, cover to company overview, each one landscape Letter page that holds its
content, with the logo in the footer and titles at 0.15in; one firm (ACME), one page count and a
table of contents that matches across them; one severity palette; sample content with documentation
addresses only; the charts in inline SVG (slides 04 and 08) and one Chart.js radar (slide 09); the
combined report, in which every slide looks exactly like its archetype; the 16-page sample PDF,
thumbnails and demo GIF, all faithful renders; the landing page with gallery, viewer and social
preview; the suite (44 tests, all passing, each seen failing for the right reason first). No known
defects are open.

Open, the maintainer decides:

1. The repository's public history still holds slide 16's earlier content (the name BICSA and
   private 10.0.x.x addresses). Removing it means rewriting history and force-pushing.
