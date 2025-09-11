from flask import Flask, send_from_directory
import os

app = Flask(__name__)


# Serve index.html as the root route
@app.route("/")
def serve_index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")


# Optionally, serve other static files (like style.css)
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
