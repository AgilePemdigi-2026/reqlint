"""
Server HTTP mandiri untuk Backend API ReqLint (http://localhost:8000).
Melayani seluruh endpoint `/api/v1/*` menggunakan `ReqLintDirectEngine` lengkap dengan dukungan CORS
dan upload dokumen PDF (`multipart/form-data`), sehingga aplikasi web `frontend-qa` (http://localhost:3000)
terhubung penuh dengan status "FastAPI: Online".
"""
import json
import sys
from email.parser import BytesParser
from email.policy import default as default_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from features.bdd_support.reqlint_client import ReqLintDirectEngine

ENGINE = ReqLintDirectEngine()


def parse_multipart_upload(content_type: str, body: bytes) -> Optional[Tuple[str, bytes, str]]:
    try:
        header_bytes = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("latin-1")
        msg = BytesParser(policy=default_policy).parsebytes(header_bytes + body)
        if msg.is_multipart():
            for part in msg.iter_parts():
                filename = part.get_filename()
                field_name = part.get_param("name", header="content-disposition")
                if filename or field_name == "file":
                    payload = part.get_payload(decode=True) or b""
                    mime = part.get_content_type() or "application/pdf"
                    return (filename or "document.pdf", payload, mime)
    except Exception:
        pass
    return None


class ReqLintBackendHandler(BaseHTTPRequestHandler):
    engine: ReqLintDirectEngine = ENGINE

    def log_message(self, format, *args):
        return

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    def _handle_all(self, method: str):
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length > 0 else b""
        content_type = self.headers.get("Content-Type", "")
        req_headers = {k: v for k, v in self.headers.items()}

        files = None
        json_body = None
        if "multipart/form-data" in content_type.lower():
            parsed_file = parse_multipart_upload(content_type, raw_body)
            if parsed_file:
                files = {"file": parsed_file}
        elif raw_body:
            try:
                json_body = json.loads(raw_body.decode("utf-8"))
            except Exception:
                json_body = None

        active_engine = getattr(self.__class__, "engine", None) or ENGINE
        resp = active_engine.request(
            method,
            self.path,
            json_body=json_body,
            headers=req_headers,
            files=files,
        )
        self.send_response(resp.status_code)
        self._send_cors()
        for hk, hv in resp.headers.items():
            self.send_header(hk, hv)
        self.send_header("Content-Length", str(len(resp.content)))
        self.end_headers()
        self.wfile.write(resp.content)

    def do_GET(self):
        self._handle_all("GET")

    def do_POST(self):
        self._handle_all("POST")

    def do_PUT(self):
        self._handle_all("PUT")

    def do_DELETE(self):
        self._handle_all("DELETE")


def run_server(host: str = "0.0.0.0", port: int = 8000):
    server = ThreadingHTTPServer((host, port), ReqLintBackendHandler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()

