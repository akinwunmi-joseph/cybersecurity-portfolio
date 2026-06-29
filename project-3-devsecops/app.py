"""
Simple web application — target for DevSecOps pipeline scanning.
Intentionally contains some mild code patterns for Bandit to analyse.
"""

import os
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt."""
    salt = secrets.token_hex(16)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def get_config() -> dict:
    """Load configuration from environment variables (not hardcoded)."""
    return {
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
        "port": int(os.environ.get("PORT", "8080")),
        "host": os.environ.get("HOST", "127.0.0.1"),
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Cybersecurity Portfolio App - OK")

    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == "__main__":
    config = get_config()
    print(f"[*] Starting server on {config['host']}:{config['port']}")
    server = HTTPServer((config["host"], config["port"]), Handler)
    server.serve_forever()
