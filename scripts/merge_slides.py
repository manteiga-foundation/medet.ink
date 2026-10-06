"""Merges the archetypes into one document.

archetypes/NN-Slide-*.html -> reports/combined_report.html (and the identical merged_report.html,
which make_pdf.py prints).

One document shares one stylesheet, one id space and one script scope, so each archetype is kept
to its own slide:

- Its stylesheet is nested under a wrapper class for its slide (CSS nesting), so a rule of one
  archetype never reaches another slide. Its page-level rules (html, body) become the wrapper's
  inherited typography; the page itself is laid out by this script. @import rules move to the
  top, @page is declared once, other global at-rules (@keyframes, @font-face) are hoisted.
- External scripts load once, in <head>. Inline scripts stay in the slide's body, where they run
  once, after their slide's markup exists.
- Element ids must be unique across archetypes; the tests check the merged result.
"""
import os
import re
from pathlib import Path

ROOT = Path.cwd()
PAGE_LEVEL = {'html', 'body', ':root'}
# Page-level declarations that still matter inside a slide: the ones descendants inherit.
INHERITED = {'color', 'font-family', 'font-size', 'font-weight', 'line-height', 'letter-spacing',
             'text-rendering', '-webkit-font-smoothing', '-moz-osx-font-smoothing'}
NESTABLE = ('@media', '@supports', '@container', '@layer')


def _find(text, i, stops):
    """Index of the first character in stops from i, outside quotes and parentheses."""
    depth, quote = 0, None
    while i < len(text):
        c = text[i]
        if quote:
            if c == '\\':
                i += 1
            elif c == quote:
                quote = None
        elif c in '"\'':
            quote = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0 and c in stops:
            return i
        i += 1
    return len(text)


def _blocks(css):
    """Top-level statements: (prelude, body) for blocks, (statement, None) for ';' at-rules."""
    out, i = [], 0
    while i < len(css):
        j = _find(css, i, '{;}')
        if j >= len(css):
            break
        prelude = css[i:j].strip()
        if css[j] == ';':
            out.append((prelude, None))
            i = j + 1
            continue
        if css[j] == '}':
            i = j + 1
            continue
        depth, k = 1, j + 1
        while k < len(css) and depth:
            k = _find(css, k, '{}')
            if k >= len(css):
                break
            depth += 1 if css[k] == '{' else -1
            k += 1
        out.append((prelude, css[j + 1:k - 1]))
        i = k
    return out


def _split(text, separator):
    parts, i = [], 0
    while i <= len(text):
        j = _find(text, i, separator)
        parts.append(text[i:j].strip())
        i = j + 1
    return [p for p in parts if p]


def _scope(css, hoisted, imports, page):
    """The rules of one archetype, ready to nest under its slide's wrapper class.

    Inherited declarations of its page-level rules are also collected in page.
    """
    rules = []
    for prelude, body in _blocks(css):
        if body is None:
            if prelude.startswith('@import'):
                imports.append(prelude + ';')
            continue
        if prelude.startswith('@page'):
            continue
        if prelude.startswith(NESTABLE):
            rules.append(f'{prelude} {{\n{_scope(body, hoisted, imports, [])}\n}}')
            continue
        if prelude.startswith('@'):
            hoisted.append(f'{prelude} {{{body}}}')
            continue
        selectors = _split(prelude, ',')
        own = [s for s in selectors if s not in PAGE_LEVEL]
        if own:
            rules.append(f'{", ".join(own)} {{{body}}}')
        if len(own) < len(selectors):
            inherited = [' '.join(d.split()) for d in _split(body, ';')
                         if d.split(':', 1)[0].strip().lower() in INHERITED]
            if inherited:
                page.extend(inherited)
                rules.append('& { ' + '; '.join(inherited) + '; }')
    return '\n'.join(rules)


def build_combined():
    slides = sorted((ROOT / 'archetypes').glob('[0-9][0-9]-Slide-*.html'))
    imports, hoisted, styles, bodies, scripts, pages = [], [], [], [], [], []

    for path in slides:
        content = path.read_text(encoding='utf-8')
        wrapper = f'archetype-{path.name[:2]}'

        css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', content, re.I | re.S))
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        page = []
        styles.append(f'/* --- {path.name} --- */\n.{wrapper} {{\n{_scope(css, hoisted, imports, page)}\n}}')
        pages.append(page)

        for tag in re.findall(r'<script[^>]*\ssrc=[^>]*>\s*</script>', content, re.I):
            if tag not in scripts:
                scripts.append(tag)

        body = re.search(r'<body[^>]*>(.*?)</body>', content, re.I | re.S)
        if body:
            bodies.append(f'<!-- --- {path.name} --- -->\n<div class="archetype {wrapper}">\n'
                          f'{body.group(1).strip()}\n</div>')

    imports = list(dict.fromkeys(imports))
    hoisted = list(dict.fromkeys(hoisted))
    # Typography every archetype gives its page goes on this document's page too: chart libraries
    # measure text in elements they attach to <body>.
    shared = [d for d in (pages[0] if pages else []) if all(d in page for page in pages)]
    newline = '\n'
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ACME - Full Penetration Testing Report</title>
    {(newline + '    ').join(scripts)}
    <style>
{newline.join(imports)}

@page {{ size: 11in 8.5in; margin: 0; }}
{newline.join(hoisted)}

{(newline + newline).join(styles)}

/* --- The combined document: slides one after another, one per printed page --- */
html, body {{ margin: 0; padding: 0; height: auto; overflow: visible; {' '.join(d + ';' for d in shared)} }}
@media screen {{
    html, body {{ overflow-x: hidden; }}
    body {{
        padding: 2rem 0;
        background-color: #64748B;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
    }}
    .slide {{
        margin: 0 !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
    }}
}}
    </style>
</head>
<body>
{(newline + newline).join(bodies)}
</body>
</html>
"""

    os.makedirs(ROOT / 'reports', exist_ok=True)
    for name in ('combined_report.html', 'merged_report.html'):
        (ROOT / 'reports' / name).write_text(html, encoding='utf-8')
    print(f'Generated reports/combined_report.html and reports/merged_report.html from {len(slides)} slides.')


if __name__ == '__main__':
    build_combined()
