# 002: landing-style

Question: what should the landing page look like in the retro computing style of the maintainer's
two references (a hardware-console UI kit, and a hand-drawn "block computing" sketch board)?

## Approach

`build.py` writes three complete landing pages into this folder from one content source: the
current page's copy, buttons, gallery (16 cards), features and footer, unchanged. Only the style
differs. `capture.py` opens each in the test harness's Chromium at 1440 x 900, 1280 x 800 and
390 x 844, checks page errors, broken images and horizontal overflow, and writes the screenshots
that `index.html` lays side by side. All three drop the Tailwind CDN script the current page loads
and use only Google Fonts.

- A. Terminal Paper (conservative): cream paper with a faint grid, charcoal ink, IBM Plex Mono
  labels with Space Grotesk headings, hard offset shadows, an LED status in the navigation band,
  features as a spec sheet.
- B. Hardware Console (reference 1): bevelled panels with screws, LED indicators, keycap buttons,
  the demo on an LCD screen with scanlines, a gallery of small monitors with VT323 labels.
- C. Blueprint Sketchbook (reference 2): paper grain, ink borders roughened by an SVG filter,
  watercolour washes, the demo taped to the page, postage-stamp gallery cards, Courier Prime with a
  Big Shoulders Display wordmark.

## Results (Chromium 148)

| | Current | A. Terminal Paper | B. Hardware Console | C. Blueprint Sketchbook |
| --- | --- | --- | --- | --- |
| Page errors, broken images, sideways overflow (3 sizes) | - | none | none | none |
| Page height at 1440 / 390 px | - | 2705 / 4351 | 2562 / 4041 | 2850 / 4430 |
| HTML size (CSS inline) | 20.7 KB | 14.5 KB (6.0 KB CSS) | 16.4 KB (6.9 KB CSS) | 15.7 KB (6.7 KB CSS) |
| Scripts | Tailwind CDN | none | none | none |
| Font families | Inter | 2 | 3 | 2 |
| Lowest text contrast | - | 6.18:1 | 5.43:1 | 6.10:1 |

Found while building: B's gallery overflowed a phone screen by 182 px (grid items with unbroken
labels; fixed with `min-width: 0`); C's roughening filter broke 2 px rules into dashes (fixed with a
gentler filter for lines). A vision model reported uneven buttons in A, an orphaned word in C's
headline and low contrast in B; the DOM showed equal 48 px buttons 14 and 15 px apart, a balanced
four-line headline, and contrast above 5.4:1 throughout.

## Verdict

The maintainer chose A, Terminal Paper, and asked that the wording not limit the template to
cybersecurity. `index.html` is option A with root-relative paths, the social preview tags, and
broadened copy: "Beautiful HTML Presentations and Reports", a lead naming security assessments,
audits, strategy reviews and executive briefings, and a gallery note that calls the sample content
a fictional security assessment. B and C stay in this folder as the record of the alternatives.
