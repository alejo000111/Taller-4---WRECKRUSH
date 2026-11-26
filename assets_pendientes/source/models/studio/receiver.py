import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "layouts"))


class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        name = os.path.basename(self.path.strip("/")) or "dump.json"
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        os.makedirs(ROOT, exist_ok=True)
        with open(os.path.join(ROOT, name), "wb") as f:
            f.write(body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"saved {name} {len(body)}".encode())

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    HTTPServer(("127.0.0.1", port), Receiver).serve_forever()
