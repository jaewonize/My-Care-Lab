import functools
import http.server
import socketserver

DIRECTORY = "/Users/ttt/Desktop/Slow Museum"
PORT = 8766


class Handler(http.server.SimpleHTTPRequestHandler):
    """No-store responses so a plain refresh always shows the latest turn
    (no manual ?t= cache-bust needed)."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


HandlerF = functools.partial(Handler, directory=DIRECTORY)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server(("127.0.0.1", PORT), HandlerF) as httpd:
    httpd.serve_forever()
