"""Helper umum: substitusi variabel, akses JSON, pembuat PDF, dan pengelola proses server."""
import os
import re
import signal
import subprocess
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

_VAR_PATTERN = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


# --------------------------------------------------------------------------- #
# Variabel skenario: ${nama} di dalam teks step / docstring diganti nilainya
# --------------------------------------------------------------------------- #
def new_scenario_vars():
    token = uuid.uuid4().hex[:10]
    email = f"bdd_{token}@example.com"
    return {
        "uid": token,
        "email_unik": email,
        "email_unik_upper": email.upper(),
        "password": "Rahasia123",
    }


def render(context, text):
    if text is None:
        return None

    def _replace(match):
        key = match.group(1)
        if key not in context.vars:
            raise KeyError(
                f"Variabel ${{{key}}} belum didefinisikan. Variabel tersedia: {sorted(context.vars)}"
            )
        return str(context.vars[key])

    return _VAR_PATTERN.sub(_replace, text)


# --------------------------------------------------------------------------- #
# Akses JSON dengan path bertitik, mis. "data.items.0.id_audit"
# --------------------------------------------------------------------------- #
def get_path(data, path):
    current = data
    for part in [p for p in path.split(".") if p]:
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(f"Field '{part}' (dari path '{path}') tidak ada. Kunci tersedia: {list(current)}")
            current = current[part]
        else:
            raise KeyError(f"Tidak bisa masuk ke '{part}' pada path '{path}' (nilai: {current!r})")
    return current


def has_path(data, path):
    try:
        get_path(data, path)
        return True
    except (KeyError, IndexError, ValueError, TypeError):
        return False


# --------------------------------------------------------------------------- #
# Pembuat berkas PDF untuk pengujian upload
# --------------------------------------------------------------------------- #
def make_pdf(text=None, pages=1, line_length=80):
    import pymupdf as fitz

    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page()
        if text:
            lines = [text[i:i + line_length] for i in range(0, len(text), line_length)]
            y = 50
            for line in lines:
                page.insert_text((40, y), line, fontsize=9)
                y += 12
    data = doc.write()
    doc.close()
    return data


# --------------------------------------------------------------------------- #
# Server lokal (Next.js / uvicorn) yang dinyalakan otomatis oleh environment.py
# --------------------------------------------------------------------------- #
def is_url_up(url, timeout=5):
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.status < 500
    except HTTPError as exc:
        return exc.code < 500
    except Exception:
        return False


class ServerProcess:
    def __init__(self, name, command, cwd, env, log_path):
        self.name = name
        self.command = command
        self.cwd = Path(cwd)
        self.env = env
        self.log_path = Path(log_path)
        self.proc = None
        self._log = None

    def start_and_wait(self, url, timeout):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_path, "w", encoding="utf-8", errors="replace")
        kwargs = {}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        self.proc = subprocess.Popen(
            self.command,
            cwd=str(self.cwd),
            env=self.env,
            shell=True,
            stdout=self._log,
            stderr=subprocess.STDOUT,
            **kwargs,
        )
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                return False
            if is_url_up(url, timeout=15):
                return True
            time.sleep(1.5)
        return False

    def stop(self):
        if self.proc and self.proc.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"], capture_output=True)
            else:
                try:
                    os.killpg(self.proc.pid, signal.SIGTERM)
                except Exception:
                    self.proc.terminate()
        if self._log:
            self._log.close()
            self._log = None

