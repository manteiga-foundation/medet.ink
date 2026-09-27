import os
import sys
import threading
import http.server
import socketserver
from playwright.sync_api import sync_playwright

PORT = 8000
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    global PORT
    with socketserver.TCPServer(("", 0), Handler) as httpd:
        PORT = httpd.server_address[1]
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

def generate_pdf():
    # Start the local HTTP server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for PORT to be assigned
    import time
    while PORT == 8000:
        time.sleep(0.1)

    with sync_playwright() as p:
        # Launch Chromium with specific flags to ensure WebGL/Canvas and Highcharts render correctly headless
        browser = p.chromium.launch(
            headless=True,
            args=["--use-gl=egl", "--ignore-gpu-blocklist"]
        )
        page = browser.new_page()

        # Disable animations globally so the PDF captures the final state immediately
        page.add_init_script("""
            window.addEventListener('load', () => {
                if (window.Chart) {
                    window.Chart.defaults.animation = false;
                }
                if (window.Highcharts) {
                    window.Highcharts.setOptions({
                        plotOptions: { series: { animation: false } },
                        chart: { animation: false }
                    });
                }
            });
        """)

        # Navigate to the target report (update path as needed)
        target_url = f"http://localhost:{PORT}/reports/merged_report.html"
        print(f"Navigating to {target_url}...")
        
        page.goto(target_url, wait_until="networkidle")

        # Give Highcharts a moment to finish rendering
        page.wait_for_timeout(2000)

        # Output to the reports folder
        output_pdf = os.path.join(DIRECTORY, 'reports', 'final_report.pdf')
        page.pdf(
            path=output_pdf,
            format="Letter",
            print_background=True,
            margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
        )
        print(f"PDF generated successfully at: {output_pdf}")

        browser.close()

if __name__ == "__main__":
    generate_pdf()
