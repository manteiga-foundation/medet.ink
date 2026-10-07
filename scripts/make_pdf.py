"""Prints the combined report to PDF: reports/merged_report.html -> reports/final_report.pdf.

Works on the folder it runs in: the repository root (the sample PDF) or a report folder laid out
the same way.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser import CHROMIUM_ARGS, load, new_page, serve

ROOT = Path.cwd()
SOURCE = 'reports/merged_report.html'
OUTPUT = ROOT / 'reports' / 'final_report.pdf'


def generate_pdf():
    with serve(ROOT) as url, sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        page = new_page(browser)
        print(f'Printing {url}/{SOURCE}...')
        load(page, f'{url}/{SOURCE}')
        # The page size comes from the slides' own @page rule: 11in x 8.5in landscape.
        page.pdf(path=str(OUTPUT), prefer_css_page_size=True, print_background=True,
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        browser.close()
    print(f'PDF generated at {OUTPUT}')


if __name__ == '__main__':
    generate_pdf()
