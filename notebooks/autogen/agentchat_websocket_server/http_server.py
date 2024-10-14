from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from tempfile import TemporaryDirectory
from autogen.io.websockets import IOWebsockets

from .on_connect import on_connect

html_path = Path(__file__.parent) / "chat.html"

# Define the custom request handler for serving the HTML file
class MyRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=html_path, **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.path = "/chat.html"
        return SimpleHTTPRequestHandler.do_GET(self)

# Run WebSocket server in the background
with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
    print(f"WebSocket server started at {uri}")

    # Start the HTTP server to serve the HTML page
    with HTTPServer(("", 8000), MyRequestHandler) as httpd:
        print("HTTP server started at http://localhost:8000")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Stopping HTTP server")
