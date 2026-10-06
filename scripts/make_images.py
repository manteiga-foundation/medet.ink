"""Renders every archetype to its gallery thumbnail: archetypes/NN-Slide-*.html -> assets/slide_NN.png."""
from playwright.sync_api import sync_playwright

from browser import CHROMIUM_ARGS, REPOSITORY, load, new_page, serve

ASSETS = REPOSITORY / 'assets'


def generate_images():
    slides = sorted((REPOSITORY / 'archetypes').glob('[0-9][0-9]-Slide-*.html'))
    with serve() as url, sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        # On screen an archetype sits inside 0.5in of padding: leave room for it, then capture
        # the slide itself (11in x 8.5in, 1056 x 816 px), not the viewport around it.
        page = new_page(browser, viewport=(1152, 912))
        for slide in slides:
            load(page, f'{url}/archetypes/{slide.name}')
            output = ASSETS / f'slide_{slide.name[:2]}.png'
            page.locator('.slide').first.screenshot(path=str(output))
            print(f'Saved {output}')
        browser.close()


if __name__ == '__main__':
    generate_images()
