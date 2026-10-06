"""Renders every archetype to its gallery thumbnail: archetypes/NN-Slide-*.html -> assets/slide_NN.png."""
from playwright.sync_api import sync_playwright

from browser import CHROMIUM_ARGS, REPOSITORY, load, new_page, serve

ASSETS = REPOSITORY / 'assets'


def generate_images():
    slides = sorted((REPOSITORY / 'archetypes').glob('[0-9][0-9]-Slide-*.html'))
    with serve() as url, sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        page = new_page(browser, viewport=(1056, 816))  # 11in x 8.5in at 96 dpi
        for slide in slides:
            load(page, f'{url}/archetypes/{slide.name}')
            output = ASSETS / f'slide_{slide.name[:2]}.png'
            page.screenshot(path=str(output))
            print(f'Saved {output}')
        browser.close()


if __name__ == '__main__':
    generate_images()
