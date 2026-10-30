"""Local CBZ library API. No provider scraping, no personal paths."""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

MAX_FILE_BYTES = 500 * 1024 * 1024

def files_in_library(root: Path):
    """Return only regular CBZ files inside root, excluding symlinks."""
    if not root.is_dir() or root.is_symlink():
        return []
    return sorted((f for f in root.rglob("*.cbz")
                   if f.is_file() and not f.is_symlink()
                   and not any(p.is_symlink() for p in f.parents if p != root)
                   and f.stat().st_size <= MAX_FILE_BYTES), key=lambda p: str(p).casefold())

def lookup(root: Path, requested: str):
    if not requested or requested.startswith("/") or "\\" in requested:
        return None
    if any(part in ("", ".", "..") for part in requested.split("/")):
        return None
    path = root.joinpath(*requested.split("/"))
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (ValueError, OSError):
        return None
    if not path.is_file() or path.is_symlink() or path.suffix.lower() != ".cbz":
        return None
    if path.stat().st_size > MAX_FILE_BYTES:
        return None
    return path

def make_handler(root: Path, token: str):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, data):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not hmac.compare_digest(self.headers.get("X-MangaSama-Pairing", ""), token):
                return self.reply(403, {"error": "PAIRING_REQUIRED"})
            path = urlsplit(self.path).path
            if path == "/v1/health":
                return self.reply(200, {"ok": True, "service": "manga-sama-library", "version": 1})
            if path == "/v1/library":
                return self.reply(200, {"items": [
                    {"path": f.relative_to(root).as_posix(), "bytes": f.stat().st_size}
                    for f in files_in_library(root)]})
            prefix = "/v1/files/"
            if not path.startswith(prefix):
                return self.reply(404, {"error": "NOT_FOUND"})
            requested = unquote(path[len(prefix):])
            file = lookup(root, requested)
            if file is None:
                return self.reply(404, {"error": "NOT_FOUND"})
            size = file.stat().st_size
            with file.open("rb") as src:
                digest = hashlib.file_digest(src, "sha256").hexdigest()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.comicbook+zip")
            self.send_header("Content-Disposition", "attachment; filename=volume.cbz")
            self.send_header("Content-Length", str(size))
            self.send_header("X-Content-SHA256", digest)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with file.open("rb") as src:
                while chunk := src.read(65536):
                    self.wfile.write(chunk)
    return Handler

def main():
    root = Path(os.environ.get("MANGASAMA_LIBRARY_DIR", "")).expanduser()
    token = os.environ.get("MANGASAMA_PAIRING_TOKEN", "")
    if not root.is_dir():
        raise SystemExit("Set MANGASAMA_LIBRARY_DIR to an existing CBZ directory")
    if len(token) < 32:
        raise SystemExit("Set MANGASAMA_PAIRING_TOKEN to a random value of at least 32 characters")
    host = os.environ.get("MANGASAMA_BIND", "127.0.0.1")
    port = int(os.environ.get("MANGASAMA_PORT", "18879"))
    if not (1024 <= port <= 65535):
        raise SystemExit("Invalid port")
    print(f"Serving local CBZ library at {host}:{port} (HTTP; use HTTPS proxy for LAN)")
    ThreadingHTTPServer((host, port), make_handler(root, token)).serve_forever()

if __name__ == "__main__":
    main()
