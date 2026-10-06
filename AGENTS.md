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

Stack: HTML5 and print CSS; Highcharts and Chart.js from CDNs; Google Fonts (Montserrat, Fira
Code); the landing page uses the Tailwind CDN. Tooling: Python 3.9 or newer, Playwright for Python,
pypdf; the tests use the standard library's `unittest`.

## Vocabulary (fixed, use these words)

- **Archetype** - one standalone slide file, `archetypes/NN-Slide-Name.html`, numbered from 01
  without gaps. The build scripts and the tests glob this pattern.
- **Slide** - the `.slide` element: one printed page, 11 x 8.5 in = 1056 x 816 CSS px = 792 x 612
  PDF points. Exactly one per archetype.
- **Combined report** - `reports/combined_report.html`, every archetype in one document, generated
  by `scripts/merge_slides.py`, which also writes the identical `reports/merged_report.html` that
  `scripts/make_pdf.py` prints. Never edited by hand.
- **Sample PDF** - `reports/final_report.pdf`, printed from the combined report; the landing page's
  Download PDF. (`assets/sample-report.pdf` is an older 13-page edition.)
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
   in real Chromium: geometry from the DOM, chart state from the chart library, pagination from
   the printed PDF. Run it and see it fail for the right reason. A test for behaviour that already
   exists cannot fail first, so prove that it can fail: apply a deliberate break to a copy of the
   repository, run the suite against the copy with `MEDET_ROOT=<copy>`, and record in
   `docs/template.md` what the test fails on.
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
reasoning about the array. One measurement of the rendered bands settles it (Highcharts draws the
first series of a stack on top), and `tests/test_maturity_chart.py` now holds the answer.

## Commands

```
python3 -m pip install -r requirements-dev.txt   # maintainers only: Playwright for Python, pypdf
python3 -m playwright install chromium

python3 -m unittest discover -s tests -v          # the gate (under a minute)
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
- Archetype files are `NN-Slide-Name.html`, numbered from 01 without gaps. A new archetype also
  needs its gallery card and `assets/slide_NN.png` on the landing page, an entry in the viewer's
  list, and regenerated derived artifacts.
- Charts are created in the archetype's own script with `Highcharts.chart(` or `new Chart(`; the
  tests count those calls in the source and expect as many charts drawn.
- Highcharts draws the first series of a stack on top (`yAxis.reversedStacks` defaults to true).
- The combined report is one document: ids, top-level script names and class rules from every
  archetype share one namespace there. New archetypes use ids and classes unique to the slide
  (for example `chart-04`) and keep their script variables out of the global scope. Today's
  collisions are known defects.
- Headless Chromium must present a regular Chrome user agent: code.highcharts.com answers 403 to
  `HeadlessChrome` and rate-limits repeated runs (429). The tests also serve third-party files from
  `tests/.cache` (fetched once; Highcharts falls back to its npm release on jsDelivr). Delete that
  folder to refresh it.
- Disable chart animations, or wait for them, before capturing images or PDFs.
- Public pages link only to files in the repository, by relative path; the social preview
  (`og:image`, `twitter:image`) is an absolute https://medet.ink/ URL of a committed file.
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
tests/harness.py                 the site over HTTP, Chromium, third-party cache, DOM probes
tests/test_*.py                  the suite (listed in docs/template.md)
docs/template.md                 notes on what is built: archetypes, tokens, tests, known defects
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
- The landing page stays sleek and minimal: a slim navigation band, concise text.
- Published from `main` through GitHub Pages with the `CNAME` file.

## Where things stand (update when it changes)

Done: sixteen archetypes, cover to appendix, each one landscape Letter page; the combined report
and the 16-page sample PDF generated from them; the landing page with gallery, viewer and social
preview; the test suite (20 tests: 15 passing, each shown to fail against a deliberate break, and 5
expected failures for the known defects below).

Known defects (measured; details and numbers in `docs/template.md`):

1. Combined report charts: `merge_slides.py` copies every inline script twice (into `<head>` and
   with each slide), so slide 04's maturity chart is never drawn and slide 08's pie lands on
   slide 04; four page errors. Page 4 of the sample PDF lacks the maturity chart as well.
2. Slides 09 and 16 push their footer (confidentiality notice, page number) below the page edge,
   where it is clipped; in the combined report the Risk Matrix (slide 06) is clipped as well.
3. `scripts/make_pdf.py` and `scripts/make_images.py` launch headless Chromium with its default
   user agent, which code.highcharts.com refuses, so their output lacks the Highcharts charts.

Seen, not decided (ask before changing): two severity palettes in use; page totals, numbering and
branding differ between archetypes; the README counts 13 layouts and a 13-page PDF where there are
16; `patch.py`, `patch2.py`, `patch3.py` at the root are one-off edits from the chart-order commits;
`.DS_Store` is tracked; vendoring the chart libraries would make the template work offline, but
Highcharts is not MIT-licensed, so that is a licensing decision.

Next candidates, in recommended order: the merge script's duplicated scripts (clears defect 1);
the headless scripts' user agent, then regenerate the sample PDF and thumbnails (defect 3); the
footer overflow and the Risk Matrix (defect 2); then the undecided items with the maintainer.
