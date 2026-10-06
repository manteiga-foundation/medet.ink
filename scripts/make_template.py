"""Packs the HTML template for download.

archetypes, the viewer, reports/combined_report.html, README.md and LICENSE ->
reports/medet-ink-template.zip, the landing page's Download HTML.

Everything sits in one folder, medet-ink-template/, with the combined report at its top as the
README's instructions describe. The pages need no local file beyond each other (the archetypes
load only fonts and Chart.js from CDNs), so the folder works wherever it is unzipped. The archive
is reproducible: sorted entries with fixed dates and permissions, so it changes only when its
files do.
"""
import zipfile
from pathlib import Path

ROOT = Path.cwd()
TARGET = ROOT / 'reports' / 'medet-ink-template.zip'
FOLDER = 'medet-ink-template/'
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def files() -> dict[str, Path]:
    """Name inside the archive -> file in the repository."""
    chosen = {
        'README.md': ROOT / 'README.md',
        'LICENSE': ROOT / 'LICENSE',
        'combined_report.html': ROOT / 'reports' / 'combined_report.html',
        'archetypes/index.html': ROOT / 'archetypes' / 'index.html',
    }
    for path in sorted((ROOT / 'archetypes').glob('[0-9][0-9]-Slide-*.html')):
        chosen[f'archetypes/{path.name}'] = path
    return chosen


def main():
    with zipfile.ZipFile(TARGET, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(files().items()):
            entry = zipfile.ZipInfo(FOLDER + name, date_time=FIXED_DATE)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, path.read_bytes())
    print(f'Packed {len(files())} files into {TARGET.relative_to(ROOT)} ({TARGET.stat().st_size // 1024} KB).')


if __name__ == '__main__':
    main()
