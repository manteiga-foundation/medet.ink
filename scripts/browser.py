"""Shared browser setup for the maintainer scripts and the tests.

Serves the repository over HTTP on a free port and opens pages in headless Chromium the way a
reader's browser shows them: a regular Chrome user agent (some CDNs refuse HeadlessChrome),
chart animations off (a capture must see the final state), web fonts loaded.
"""
from __future__ import annotations

import contextlib
import http.server
import socketserver
import threading
from pathlib import Path
from typing import Iterator

REPOSITORY = Path(__file__).resolve().parent.parent

CHROMIUM_ARGS = ['--use-gl=egl', '--ignore-gpu-blocklist']

# Chart libraries animate their first draw. Each library is configured the moment its script
# defines it, before any chart is created.
NO_ANIMATIONS = """(() => {
  const configure = {
    Chart: (C) => { C.defaults.animation = false; },
  };
  for (const [name, apply] of Object.entries(configure)) {
    let value;
    Object.defineProperty(window, name, {
      configurable: true,
      get: () => value,
      set: (library) => { value = library; try { apply(library); } catch (error) {} },
    });
  }
})();"""


def chrome_user_agent(browser) -> str:
    """The user agent of a regular desktop Chrome of the same version as the browser."""
    return ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
            f'(KHTML, like Gecko) Chrome/{browser.version} Safari/537.36')


@contextlib.contextmanager
def serve(directory: Path = REPOSITORY) -> Iterator[str]:
    """Serves a directory on 127.0.0.1 and a free port; yields its base URL."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format, *args):
            pass

    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield f'http://127.0.0.1:{httpd.server_address[1]}'
    finally:
        httpd.shutdown()
        httpd.server_close()


def new_page(browser, viewport: tuple[int, int] = (1056, 816)):
    """A page in a fresh context: regular Chrome user agent, chart animations off."""
    context = browser.new_context(viewport={'width': viewport[0], 'height': viewport[1]},
                                  user_agent=chrome_user_agent(browser))
    page = context.new_page()
    page.add_init_script(NO_ANIMATIONS)
    return page


def load(page, url: str) -> None:
    """Navigates and waits until the network is idle and the web fonts have loaded."""
    page.goto(url, wait_until='networkidle')
    page.evaluate('document.fonts.ready.then(() => true)')
