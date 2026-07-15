import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_mock_response(payload):
    response = load_json(ROOT / "api" / "evaluate.json")
    response["fileName"] = payload.get("fileName", response.get("fileName", "unknown"))
    return response


def try_openai_review(payload):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    file_name = payload.get("fileName", "unknown")
    content = payload.get("content", "")
    prompt = (
        "You are a helpful reviewer. Review the following document and return concise JSON containing "
        "summary, score, highlights, and nextSteps."
        f"\nDocument name: {file_name}\nContent:\n{content[:4000]}"
    )

    body = json.dumps({
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": "Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
            message = data["choices"][0]["message"]["content"]
        return json.loads(message)
    except Exception:
        return None


def build_response(payload):
    llm_response = try_openai_review(payload)
    if llm_response:
        return {
            "status": "ok",
            "mock": False,
            "fileName": payload.get("fileName", "unknown"),
            "review": llm_response,
        }
    return build_mock_response(payload)


class ReviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health.json":
            self.send_json(load_json(ROOT / "api" / "health.json"))
            return

        if parsed.path == "/api/evaluate.json":
            self.send_json(build_response({"fileName": "sample-upload.txt", "content": ""}))
            return

        file_path = (ROOT / parsed.path.lstrip("/")).resolve()
        if str(file_path).startswith(str(ROOT)) and file_path.exists() and file_path.is_file():
            self.send_file(file_path)
            return

        if parsed.path in {"/", "/index.html"}:
            self.send_file(ROOT / "frontend" / "index.html")
            return

        self.send_error(404)

    def send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8" if path.suffix == ".html" else "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    with ThreadingHTTPServer((host, port), ReviewHandler) as server:
        print(f"Serving at http://{host}:{port}")
        server.serve_forever()
