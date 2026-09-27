import os
import glob
import threading
import http.server
import socketserver
from playwright.sync_api import sync_playwright
import time

DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    global PORT
    with socketserver.TCPServer(("", 0), Handler) as httpd:
        PORT = httpd.server_address[1]
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

def generate_images():
    # Start server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    while PORT == 8000:
        time.sleep(0.1)

    # Make sure assets dir exists
    assets_dir = os.path.join(DIRECTORY, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    slides = sorted(glob.glob(os.path.join(DIRECTORY, 'archetypes', '[0-1][0-9]-Slide-*.html')))
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--use-gl=egl", "--ignore-gpu-blocklist"]
        )
        page = browser.new_page(viewport={'width': 1056, 'height': 816}) # 11x8.5 inches at 96 dpi

        page.add_init_script("""
            window.addEventListener('load', () => {
                if (window.Chart) { window.Chart.defaults.animation = false; }
                if (window.Highcharts) {
                    window.Highcharts.setOptions({
                        plotOptions: { series: { animation: false } },
                        chart: { animation: false }
                    });
                }
            });
        """)

        for i, slide_path in enumerate(slides, start=1):
            filename = os.path.basename(slide_path)
            url = f"http://localhost:{PORT}/archetypes/{filename}"
            print(f"Navigating to {url}...")
            
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(1000) # give charts extra time to render
            
            out_png = os.path.join(assets_dir, f"slide_{i:02d}.png")
            page.screenshot(path=out_png)
            print(f"Saved {out_png}")

        browser.close()

if __name__ == "__main__":
    generate_images()
