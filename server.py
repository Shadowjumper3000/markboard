import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}/index.html")
        httpd.serve_forever()
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask server is running!"


if __name__ == "__main__":
    app.run(debug=True)
