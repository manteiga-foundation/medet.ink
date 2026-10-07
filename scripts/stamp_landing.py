"""Stamps the landing page's links to files that change with their content version.

index.html links thumbnails, slides and reports whose names stay the same when their content
changes, and GitHub Pages lets browsers keep a copy for four hours, so a returning visitor would see
an old thumbnail under a new name. Each such link gets ?v=<first 8 hex of the file's SHA-256>: a
changed file gets a new address, an unchanged one keeps its cache. Run after regenerating any
derived artifact or editing an archetype; tests/test_landing.py fails on a stale stamp.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path.cwd()
PAGE = ROOT / 'index.html'
LINK = re.compile(r'((?:href|src|data-src)=")((?:archetypes|assets|reports)/[^"?#]+)(?:\?v=[0-9a-f]*)?(")')


def stamp(match: re.Match) -> str:
    path = match.group(2)
    version = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:8]
    return f'{match.group(1)}{path}?v={version}{match.group(3)}'


def main():
    before = PAGE.read_text(encoding='utf-8')
    after, count = LINK.subn(stamp, before)
    PAGE.write_text(after, encoding='utf-8')
    changed = sum(1 for a, b in zip(LINK.finditer(before), LINK.finditer(after)) if a.group(0) != b.group(0))
    print(f'Stamped {count} links in index.html ({changed} changed).')


if __name__ == '__main__':
    main()
