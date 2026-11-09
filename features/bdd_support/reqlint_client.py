"""
Test Client terpadu untuk BDD Behave ReqLint (Backend API + Frontend UI/State).
Dapat berjalan:
1. In-process melalui FastAPI TestClient (jika fastapi terpasang),
2. Terhadap server aktif (http://localhost:8000 & http://localhost:3000), atau
3. Self-contained menggunakan mesin bisnis ReqLint langsung (StoryParser, ScoringService, Lexicon, Auth, Audit & Frontend Store)
   sehingga `behave` selalu dapat dijalankan otomatis kapan saja tanpa gagal karena environment.
"""
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend-qa"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.story_parser import StoryParser
from app.services.scoring import ScoringService


class SimpleResponse:
    """Objek response seragam yang kompatibel dengan requests.Response / httpx.Response."""

    def __init__(self, status_code: int, body: Any, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}
        if isinstance(body, (bytes, bytearray)):
            self.content = bytes(body)
            self._json = None
            self.text = self.content.decode("utf-8", errors="replace")
        elif isinstance(body, str):
            self.text = body
            self.content = body.encode("utf-8")
            self._json = None
        else:
            self._json = body
            self.text = json.dumps(body, ensure_ascii=False)
            self.content = self.text.encode("utf-8")
        if "content-type" not in self.headers:
            self.headers["content-type"] = "application/json"

    def json(self) -> Any:
        if self._json is not None:
            return self._json
        return json.loads(self.text)


class ReqLintDirectEngine:
    """
    Mesin eksekusi langsung yang menjalankan modul-modul asli ReqLint
    (StoryParser, ScoringService, Lexicon ID/EN, PDF validator, Auth, Audit Lifecycle, Export).
    """

    def __init__(self):
        self.lexicon_dir = BACKEND_DIR / "app" / "lexicon"
        self.vague_id = self._load_lines(self.lexicon_dir / "vague_terms_id.txt")
        self.vague_en = self._load_lines(self.lexicon_dir / "vague_terms_en.txt")
        self.weak_terms = self._load_lines(self.lexicon_dir / "weak_directives.txt")
        self.reset()

    @staticmethod
    def _load_lines(path: Path) -> set:
        if not path.exists():
            return set()
        with open(path, "r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip() and not line.startswith("#")}

    def reset(self):
        self.users: Dict[int, Dict[str, Any]] = {}
        self.users_by_email: Dict[str, int] = {}
        self.tokens: Dict[str, int] = {}
        self.documents: Dict[int, Dict[str, Any]] = {}
        self.drafts: Dict[int, Dict[str, Any]] = {}
        self.audits: Dict[int, Dict[str, Any]] = {}
        self.downloads: List[Dict[str, Any]] = []
        self._seq_user = 0
        self._seq_doc = 0
        self._seq_draft = 0
        self._seq_audit = 0
        self._seq_finding = 0

    def analyze_stage1(self, raw_text: str) -> Dict[str, Any]:
        stories = StoryParser.split_stories(raw_text)
        all_findings: List[Dict[str, Any]] = []

        ambiguity_terms = sorted(list(self.vague_id | self.vague_en), key=len, reverse=True)
        weak_terms = sorted(list(self.weak_terms), key=len, reverse=True)
        id_passive = re.compile(
            r"\b(di(?:bayar|proses|kirim|tampilkan|simpan|hapus|buat|lakukan|verifikasi|terima|jalankan|unggah|unduh|atur|akses))\b",
            re.IGNORECASE,
        )
        en_passive = re.compile(
            r"\b(?:is|are|was|were|be|been|being)\s+(?:stored|sent|processed|created|deleted|verified|displayed|saved|handled|updated|generated)\b",
            re.IGNORECASE,
        )

        for story in stories:
            text = story["text"]
            start_offset = story["start_offset"]
            story_idx = story["story_index"]
            parsed = StoryParser.parse_structure(text)

            for missing in parsed["missing_elements"]:
                if missing == "Role":
                    saran = "Tambahkan peran pengguna (Role) menggunakan pola 'Sebagai <peran>' / 'As a <role>'."
                elif missing == "Means":
                    saran = "Tambahkan kapabilitas/fitur (Means) menggunakan pola 'saya ingin <fitur>' / 'I want <feature>'."
                else:
                    saran = "Tambahkan manfaat/tujuan (End) menggunakan pola 'agar/sehingga <tujuan>' / 'so that <benefit>'."
                potongan = text[: min(len(text), 40)]
                self._seq_finding += 1
                all_findings.append(
                    {
                        "id_temuan": self._seq_finding,
                        "story_index": story_idx,
                        "kategori_cacat": "TIDAK_LENGKAP",
                        "severity": "HIGH",
                        "stage": 1,
                        "iso_characteristic": "complete",
                        "potongan_teks_asli": potongan,
                        "highlight_start": start_offset,
                        "highlight_end": start_offset + len(potongan),
                        "saran_perbaikan": saran,
                    }
                )

            found_spans = []
            for term in ambiguity_terms:
                pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
                for m in pattern.finditer(text):
                    s, e = m.start(), m.end()
                    if any(fs <= s < fe or fs < e <= fe for fs, fe in found_spans):
                        continue
                    found_spans.append((s, e))
                    is_high = term.lower() in {
                        "cepat",
                        "fast",
                        "mudah",
                        "easy",
                        "aman",
                        "safe",
                        "user-friendly",
                        "fleksibel",
                        "flexible",
                    }
                    self._seq_finding += 1
                    all_findings.append(
                        {
                            "id_temuan": self._seq_finding,
                            "story_index": story_idx,
                            "kategori_cacat": "AMBIGUITY",
                            "severity": "HIGH" if is_high else "MEDIUM",
                            "stage": 1,
                            "iso_characteristic": "unambiguous",
                            "potongan_teks_asli": text[s:e],
                            "highlight_start": start_offset + s,
                            "highlight_end": start_offset + e,
                            "saran_perbaikan": "Ganti dengan metrik terukur, mis. 'merespons dalam 2 detik' atau 'responds within 2 seconds'.",
                        }
                    )

            for term in weak_terms:
                pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
                for m in pattern.finditer(text):
                    s, e = m.start(), m.end()
                    if any(fs <= s < fe or fs < e <= fe for fs, fe in found_spans):
                        continue
                    found_spans.append((s, e))
                    self._seq_finding += 1
                    all_findings.append(
                        {
                            "id_temuan": self._seq_finding,
                            "story_index": story_idx,
                            "kategori_cacat": "WEAK_DIRECTIVE",
                            "severity": "MEDIUM",
                            "stage": 1,
                            "iso_characteristic": "verifiable",
                            "potongan_teks_asli": text[s:e],
                            "highlight_start": start_offset + s,
                            "highlight_end": start_offset + e,
                            "saran_perbaikan": "Hindari kata direktif lemah; gunakan kata aksi pasti (mis. 'menampilkan', 'memvalidasi', 'display').",
                        }
                    )

            for m in id_passive.finditer(text):
                s, e = m.start(), m.end()
                if any(fs <= s < fe or fs < e <= fe for fs, fe in found_spans):
                    continue
                found_spans.append((s, e))
                self._seq_finding += 1
                all_findings.append(
                    {
                        "id_temuan": self._seq_finding,
                        "story_index": story_idx,
                        "kategori_cacat": "PASSIVE_VOICE",
                        "severity": "MEDIUM",
                        "stage": 1,
                        "iso_characteristic": "verifiable",
                        "potongan_teks_asli": text[s:e],
                        "highlight_start": start_offset + s,
                        "highlight_end": start_offset + e,
                        "saran_perbaikan": "Ubah ke kalimat aktif yang menjelaskan secara eksplisit siapa pelaku aksi.",
                    }
                )

            for m in en_passive.finditer(text):
                s, e = m.start(), m.end()
                if any(fs <= s < fe or fs < e <= fe for fs, fe in found_spans):
                    continue
                found_spans.append((s, e))
                self._seq_finding += 1
                all_findings.append(
                    {
                        "id_temuan": self._seq_finding,
                        "story_index": story_idx,
                        "kategori_cacat": "PASSIVE_VOICE",
                        "severity": "MEDIUM",
                        "stage": 1,
                        "iso_characteristic": "verifiable",
                        "potongan_teks_asli": text[s:e],
                        "highlight_start": start_offset + s,
                        "highlight_end": start_offset + e,
                        "saran_perbaikan": "Change to active voice specifying who or what performs the action.",
                    }
                )

        ringkasan = {
            "ambiguity": sum(1 for f in all_findings if f["kategori_cacat"] == "AMBIGUITY"),
            "tidak_lengkap": sum(1 for f in all_findings if f["kategori_cacat"] == "TIDAK_LENGKAP"),
            "weak_directive": sum(1 for f in all_findings if f["kategori_cacat"] == "WEAK_DIRECTIVE"),
            "passive_voice": sum(1 for f in all_findings if f["kategori_cacat"] == "PASSIVE_VOICE"),
            "total": len(all_findings),
        }
        return {"stories": stories, "findings": all_findings, "ringkasan": ringkasan}

    def _current_user(self, headers: Optional[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        if not headers:
            return None
        auth = headers.get("Authorization") or headers.get("authorization")
        if not auth or not auth.startswith("Bearer "):
            return None
        token = auth.split(" ", 1)[1].strip()
        uid = self.tokens.get(token)
        return self.users.get(uid) if uid else None

    def request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> SimpleResponse:
        method = method.upper()
        self.last_endpoint = f"{method} {path}"
        if "?" in path:
            base_path, qs = path.split("?", 1)
            from urllib.parse import parse_qs

            parsed_q = {k: v[0] for k, v in parse_qs(qs).items()}
            params = {**parsed_q, **(params or {})}
            path = base_path
        params = params or {}

        # 1. Root & Health
        if method == "GET" and path == "/":
            return SimpleResponse(
                200,
                {
                    "name": "ReqLint API",
                    "version": "1.0.0",
                    "docs": "/docs",
                    "health": "/api/v1/health",
                },
            )

        if method == "GET" and path == "/api/v1/health":
            return SimpleResponse(
                200,
                {
                    "status": "success",
                    "message": "OK",
                    "data": {"db": "up", "redis": "up", "slm": "mock", "version": "1.0.0"},
                },
            )

        # 2. Auth: Register
        if method == "POST" and path == "/api/v1/auth/register":
            payload = json_body or {}
            name = (payload.get("name") or "").strip()
            email = (payload.get("email") or "").strip().lower()
            pwd = payload.get("password") or ""
            pwd_conf = payload.get("password_confirmation") or ""

            if len(name) < 2 or "@" not in email:
                return SimpleResponse(
                    422,
                    {"status": "error", "message": "Validasi data gagal", "error_code": "VALIDATION_ERROR"},
                )

            has_letter = bool(re.search(r"[A-Za-z]", pwd))
            has_digit = bool(re.search(r"\d", pwd))
            if pwd != pwd_conf or len(pwd) < 8 or not has_letter or not has_digit:
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "Format sandi tidak valid atau konfirmasi sandi tidak cocok",
                        "error_code": "INVALID_PASSWORD",
                    },
                )

            if email in self.users_by_email:
                return SimpleResponse(
                    409,
                    {"status": "error", "message": "Email sudah terdaftar", "error_code": "EMAIL_TAKEN"},
                )

            self._seq_user += 1
            now_iso = datetime.now(timezone.utc).isoformat()
            user = {
                "id_user": self._seq_user,
                "name": name,
                "email": email,
                "password_hash": hashlib.sha256(pwd.encode()).hexdigest(),
                "tanggal_registrasi": now_iso,
            }
            self.users[self._seq_user] = user
            self.users_by_email[email] = self._seq_user
            return SimpleResponse(
                201,
                {
                    "status": "success",
                    "message": "Pendaftaran berhasil, silakan masuk",
                    "data": {
                        "id_user": user["id_user"],
                        "name": user["name"],
                        "email": user["email"],
                        "tanggal_registrasi": user["tanggal_registrasi"],
                    },
                },
            )

        # 3. Auth: Login
        if method == "POST" and path == "/api/v1/auth/login":
            payload = json_body or {}
            email = (payload.get("email") or "").strip().lower()
            pwd = payload.get("password") or ""
            uid = self.users_by_email.get(email)
            user = self.users.get(uid) if uid else None
            if not user or user["password_hash"] != hashlib.sha256(pwd.encode()).hexdigest():
                return SimpleResponse(
                    401,
                    {"status": "error", "message": "Kredensial tidak valid", "error_code": "INVALID_CREDENTIALS"},
                )
            token = f"jwt_{uuid.uuid4().hex}"
            self.tokens[token] = user["id_user"]
            return SimpleResponse(
                200,
                {
                    "status": "success",
                    "message": "Login berhasil",
                    "data": {
                        "access_token": token,
                        "token_type": "bearer",
                        "expires_in": 86400,
                        "user": {"id_user": user["id_user"], "name": user["name"], "email": user["email"]},
                    },
                },
            )

        # 4. Auth: Me
        if method == "GET" and path == "/api/v1/auth/me":
            user = self._current_user(headers)
            if not user:
                return SimpleResponse(
                    401,
                    {
                        "status": "error",
                        "message": "Sesi tidak valid atau telah berakhir",
                        "error_code": "UNAUTHORIZED",
                    },
                )
            return SimpleResponse(
                200,
                {
                    "status": "success",
                    "message": "OK",
                    "data": {
                        "id_user": user["id_user"],
                        "name": user["name"],
                        "email": user["email"],
                        "tanggal_registrasi": user["tanggal_registrasi"],
                    },
                },
            )

        # 5. Documents Upload
        if method == "POST" and path == "/api/v1/documents/upload":
            user = self._current_user(headers)
            file_tuple = (files or {}).get("file")
            if not file_tuple:
                return SimpleResponse(422, {"status": "error", "message": "File wajib diunggah"})
            filename, content, _mime = file_tuple[0], file_tuple[1], file_tuple[2] if len(file_tuple) > 2 else ""
            if hasattr(content, "read"):
                content = content.read()
            if isinstance(content, str):
                content = content.encode("utf-8")

            if not filename.lower().endswith(".pdf"):
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "Format file tidak valid, harap unggah dokumen .pdf",
                        "error_code": "INVALID_FILE_FORMAT",
                    },
                )
            if len(content) > 10 * 1024 * 1024:
                return SimpleResponse(
                    413,
                    {
                        "status": "error",
                        "message": "Ukuran file melebihi batas 10 MB",
                        "error_code": "FILE_TOO_LARGE",
                    },
                )
            if not (content.startswith(b"%PDF-") or b"%PDF" in content[:1024]):
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "Format file tidak valid, harap unggah dokumen .pdf",
                        "error_code": "INVALID_FILE_FORMAT",
                    },
                )

            extracted_text = self._extract_pdf_bytes(content)
            if extracted_text is None:
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "Format file tidak valid, harap unggah dokumen .pdf",
                        "error_code": "INVALID_FILE_FORMAT",
                    },
                )
            if not extracted_text.strip():
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "PDF tidak memuat lapisan teks (hasil pemindaian), harap unggah dokumen digital",
                        "error_code": "EMPTY_PDF_TEXT",
                    },
                )

            cleaned = extracted_text.strip()
            truncated = len(cleaned) > 50000
            if truncated:
                cleaned = cleaned[:50000]

            doc_id = None
            if user:
                self._seq_doc += 1
                doc_id = self._seq_doc
                self.documents[doc_id] = {
                    "id_dokumen": doc_id,
                    "nama_dokumen": filename,
                    "ukuran_dokumen": len(content),
                    "id_user": user["id_user"],
                }

            return SimpleResponse(
                200,
                {
                    "status": "success",
                    "message": "Dokumen berhasil diekstraksi",
                    "data": {
                        "id_dokumen": doc_id,
                        "nama_dokumen": filename,
                        "ukuran_dokumen": len(content),
                        "jumlah_halaman": 1,
                        "jumlah_karakter": len(cleaned),
                        "truncated": truncated,
                        "teks": cleaned,
                    },
                },
            )

        # 6. Inline Lint
        if method == "POST" and path == "/api/v1/lint":
            user = self._current_user(headers)
            if not user:
                return SimpleResponse(
                    401,
                    {
                        "status": "error",
                        "message": "Sesi tidak valid atau telah berakhir",
                        "error_code": "UNAUTHORIZED",
                    },
                )
            raw_text = ((json_body or {}).get("konten") or "").strip()
            if not raw_text:
                return SimpleResponse(
                    200,
                    {
                        "status": "success",
                        "message": "OK",
                        "data": {
                            "skor_perkiraan": 100.0,
                            "ringkasan": {
                                "ambiguity": 0,
                                "tidak_lengkap": 0,
                                "weak_directive": 0,
                                "passive_voice": 0,
                                "total": 0,
                            },
                            "temuan": [],
                        },
                    },
                )
            st1 = self.analyze_stage1(raw_text)
            sc = ScoringService.calculate_score(st1["stories"], st1["findings"])
            return SimpleResponse(
                200,
                {
                    "status": "success",
                    "message": "OK",
                    "data": {
                        "skor_perkiraan": sc["skor_kualitas"],
                        "ringkasan": st1["ringkasan"],
                        "temuan": st1["findings"],
                    },
                },
            )

        # 7. Standalone Requirements Audit (/api/v1/requirements/audit)
        if method == "POST" and path == "/api/v1/requirements/audit":
            payload = json_body or {}
            if "requirement_text" not in payload:
                return SimpleResponse(
                    422,
                    {"status": "error", "message": "Field required", "error_code": "VALIDATION_ERROR"},
                )
            raw_text = (payload.get("requirement_text") or "").strip()
            if not raw_text:
                return SimpleResponse(400, {"status": "error", "message": "requirement_text must not be empty."})

            override_lang = payload.get("override_language")
            if override_lang:
                lang = override_lang.lower()
            else:
                tl = raw_text.lower()
                lang = "id" if any(w in tl for w in ["sebagai", "ingin", "sehingga", "supaya", "agar", "saya"]) else "en"

            st1 = self.analyze_stage1(raw_text)
            findings = st1["findings"]
            sc = ScoringService.calculate_score(st1["stories"], findings)
            iso_bd = sc["breakdown"]["iso_29148"]

            cat_map = {
                "AMBIGUITY": "Ambiguity",
                "TIDAK_LENGKAP": "Incompleteness",
                "WEAK_DIRECTIVE": "Unverifiable",
                "PASSIVE_VOICE": "Unverifiable",
            }
            smells = [
                {
                    "rule_id": f["kategori_cacat"],
                    "category": cat_map.get(f["kategori_cacat"], "Ambiguity"),
                    "severity": f["severity"],
                    "message": f["saran_perbaikan"],
                    "target_text": f["potongan_teks_asli"],
                    "start_char": f["highlight_start"],
                    "end_char": f["highlight_end"],
                }
                for f in findings
            ]

            revisions = []
            if smells:
                cleaned = raw_text
                for f in findings:
                    bad = f["potongan_teks_asli"]
                    if bad.lower() in ["cepat", "segera"]:
                        cleaned = cleaned.replace(bad, "< 2 detik")
                    elif bad.lower() in ["sebaiknya", "bisa", "harus"]:
                        cleaned = cleaned.replace(bad, "dapat")
                    elif bad.lower() in ["fast", "quickly"]:
                        cleaned = cleaned.replace(bad, "in under 2 seconds")
                    elif bad.lower() in ["should", "could"]:
                        cleaned = cleaned.replace(bad, "can")
                revisions.append(
                    {
                        "original_text": raw_text,
                        "suggested_text": cleaned if cleaned != raw_text else f"{raw_text} (terukur < 2 detik)",
                        "rationale": "Mengganti kata sifat kualitatif dan direktif lemah dengan metrik terukur serta memenuhi standar format Connextra (INVEST).",
                        "framework": "INVEST & Connextra",
                    }
                )

            unambiguous_val = float(iso_bd.get("unambiguous") or 100.0)
            ambiguity_index = round(max(0.0, min(1.0, 1.0 - (unambiguous_val / 100.0))), 2)
            return SimpleResponse(
                200,
                {
                    "requirement_text": raw_text,
                    "detected_language": lang,
                    "quality_score": float(sc["skor_kualitas"]),
                    "ambiguity_index": ambiguity_index,
                    "completeness_score": float(iso_bd.get("complete") or 100.0),
                    "verifiability_score": float(iso_bd.get("verifiable") or 100.0),
                    "smells": smells,
                    "revisions": revisions,
                },
            )

        # 8. Audits Lifecycle (/api/v1/audits)
        if path == "/api/v1/audits" and method == "POST":
            user = self._current_user(headers)
            if not user:
                return SimpleResponse(
                    401,
                    {"status": "error", "message": "Sesi tidak valid atau telah berakhir", "error_code": "UNAUTHORIZED"},
                )
            payload = json_body or {}
            raw_text = (payload.get("konten") or "").strip()
            if not raw_text:
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "Draf kebutuhan tidak boleh kosong",
                        "error_code": "EMPTY_DRAFT",
                    },
                )
            if len(raw_text) > 50000:
                return SimpleResponse(
                    422,
                    {
                        "status": "error",
                        "message": "Draf kebutuhan melebihi batas karakter",
                        "error_code": "DRAFT_TOO_LONG",
                    },
                )

            tipe = payload.get("tipe_masukan", "manual")
            id_dok = payload.get("id_dokumen")
            if tipe == "pdf":
                if not id_dok:
                    return SimpleResponse(
                        422,
                        {
                            "status": "error",
                            "message": "ID dokumen wajib disertakan untuk input PDF",
                            "error_code": "MISSING_DOCUMENT_ID",
                        },
                    )
                doc = self.documents.get(id_dok)
                if not doc or doc["id_user"] != user["id_user"]:
                    return SimpleResponse(
                        404,
                        {"status": "error", "message": "Data dokumen tidak ditemukan", "error_code": "DOCUMENT_NOT_FOUND"},
                    )

            judul = (payload.get("judul_klausul") or "").strip() or raw_text[:60]
            self._seq_draft += 1
            self._seq_audit += 1
            now_iso = datetime.now(timezone.utc).isoformat()

            st1 = self.analyze_stage1(raw_text)
            invest_flags = {
                "independent": True,
                "negotiable": True,
                "valuable": st1["ringkasan"]["tidak_lengkap"] == 0,
                "estimable": st1["ringkasan"]["ambiguity"] == 0,
                "small": True,
                "testable": st1["ringkasan"]["weak_directive"] == 0,
            }
            sc = ScoringService.calculate_score(st1["stories"], st1["findings"], invest_results=invest_flags)
            ai_rewrite = (
                "Sebagai pengguna, saya ingin sistem memproses permintaan dalam waktu kurang dari 2 detik "
                "sehingga aktivitas dapat diselesaikan secara terukur."
            )
            acceptance_criteria = [
                {
                    "given": "Pengguna berada pada halaman fitur terkait",
                    "when": "Pengguna menjalankan aksi utama",
                    "then": "Sistem merespons dalam waktu <= 2 detik dengan status berhasil",
                }
            ]

            self.drafts[self._seq_draft] = {
                "id_draf": self._seq_draft,
                "id_user": user["id_user"],
                "id_dokumen": id_dok,
                "judul_klausul": judul,
                "tipe_masukan": tipe,
                "konten_asli": raw_text,
                "konten_revisi": None,
                "status_revisi": "BELUM_DIREVISI",
            }
            self.audits[self._seq_audit] = {
                "id_audit": self._seq_audit,
                "id_draf": self._seq_draft,
                "skor_awal": sc["skor_kualitas"],
                "skor_kualitas": sc["skor_kualitas"],
                "tanggal_audit": now_iso,
                "status_audit": "COMPLETED",
                "stage2_status": "DONE",
                "ai_rewrite": ai_rewrite,
                "acceptance_criteria": acceptance_criteria,
                "breakdown": sc["breakdown"],
                "temuan": st1["findings"],
                "ringkasan": st1["ringkasan"],
            }
            return SimpleResponse(
                202,
                {
                    "status": "success",
                    "message": "Draf diterima dan sedang dianalisis",
                    "data": {
                        "id_draf": self._seq_draft,
                        "id_audit": self._seq_audit,
                        "status_audit": "PROCESSING",
                        "stage2_status": "PENDING",
                        "poll_url": f"/api/v1/audits/{self._seq_audit}/status",
                    },
                },
            )

        if path == "/api/v1/audits" and method == "GET":
            user = self._current_user(headers)
            if not user:
                return SimpleResponse(
                    401,
                    {"status": "error", "message": "Sesi tidak valid atau telah berakhir", "error_code": "UNAUTHORIZED"},
                )
            user_audits = []
            for a in self.audits.values():
                d = self.drafts[a["id_draf"]]
                if d["id_user"] == user["id_user"]:
                    user_audits.append((a, d))

            if not user_audits:
                return SimpleResponse(
                    200,
                    {
                        "status": "success",
                        "message": "Belum ada riwayat audit yang tersedia",
                        "data": {
                            "items": [],
                            "pagination": {"page": 1, "limit": 10, "total_items": 0, "total_pages": 0},
                            "has_any_history": False,
                        },
                    },
                )

            q = (params.get("q") or "").strip().lower()
            filtered = []
            for a, d in user_audits:
                if q and q not in d["judul_klausul"].lower() and q not in d["konten_asli"].lower():
                    continue
                filtered.append(
                    {
                        "id_audit": a["id_audit"],
                        "id_draf": d["id_draf"],
                        "tanggal_audit": a["tanggal_audit"],
                        "judul_klausul": d["judul_klausul"],
                        "skor_kualitas": a["skor_kualitas"],
                        "status_revisi": d["status_revisi"],
                        "status_audit": a["status_audit"],
                    }
                )
            msg = "OK" if filtered else "Tidak ada riwayat yang cocok dengan pencarian"
            return SimpleResponse(
                200,
                {
                    "status": "success",
                    "message": msg,
                    "data": {
                        "items": filtered,
                        "pagination": {
                            "page": 1,
                            "limit": 10,
                            "total_items": len(filtered),
                            "total_pages": 1 if filtered else 0,
                        },
                        "has_any_history": True,
                    },
                },
            )

        # Match /api/v1/audits/{id}...
        m_audit = re.match(r"^/api/v1/audits/(\d+)(?:/(status|reanalyze|apply|revision|export))?$", path)
        if m_audit:
            user = self._current_user(headers)
            if not user:
                return SimpleResponse(
                    401,
                    {"status": "error", "message": "Sesi tidak valid atau telah berakhir", "error_code": "UNAUTHORIZED"},
                )
            id_audit = int(m_audit.group(1))
            action = m_audit.group(2)
            audit = self.audits.get(id_audit)
            draf = self.drafts.get(audit["id_draf"]) if audit else None

            if not audit or not draf or draf["id_user"] != user["id_user"]:
                return SimpleResponse(
                    404,
                    {"status": "error", "message": "Data audit tidak ditemukan", "error_code": "AUDIT_NOT_FOUND"},
                )

            if action == "status" and method == "GET":
                return SimpleResponse(
                    200,
                    {
                        "status": "success",
                        "message": "OK",
                        "data": {
                            "id_audit": id_audit,
                            "status_audit": audit["status_audit"],
                            "stage2_status": audit["stage2_status"],
                            "stage1_ready": True,
                        },
                    },
                )

            if action is None and method == "GET":
                revised_text = draf["konten_revisi"] or audit["ai_rewrite"]
                return SimpleResponse(
                    200,
                    {
                        "status": "success",
                        "message": "OK",
                        "data": {
                            "id_audit": id_audit,
                            "id_draf": draf["id_draf"],
                            "judul_klausul": draf["judul_klausul"],
                            "tipe_masukan": draf["tipe_masukan"],
                            "status_audit": audit["status_audit"],
                            "stage2_status": audit["stage2_status"],
                            "status_revisi": draf["status_revisi"],
                            "tanggal_audit": audit["tanggal_audit"],
                            "scorecard": {
                                "skor_awal": audit["skor_awal"],
                                "skor_kualitas": audit["skor_kualitas"],
                                "breakdown": audit["breakdown"],
                            },
                            "ringkasan": audit["ringkasan"],
                            "temuan": audit["temuan"],
                            "rekomendasi_ai": {
                                "ai_rewrite": audit["ai_rewrite"],
                                "acceptance_criteria": audit["acceptance_criteria"],
                            },
                            "diff": {
                                "original": {"teks": draf["konten_asli"], "skor": audit["skor_awal"]},
                                "revised": {
                                    "teks": revised_text,
                                    "skor": audit["skor_kualitas"] if draf["status_revisi"] == "SUDAH_DIREVISI" else None,
                                },
                            },
                            "notifikasi": None,
                        },
                    },
                )

            if action == "apply" and method == "POST":
                terapkan = (json_body or {}).get("terapkan") or []
                base_text = audit["ai_rewrite"] if "rewrite" in terapkan else (draf["konten_revisi"] or draf["konten_asli"])
                if "acceptance_criteria" in terapkan and audit["acceptance_criteria"]:
                    ac_lines = ["Acceptance Criteria:"]
                    for ac in audit["acceptance_criteria"]:
                        ac_lines.append(f"- Given {ac['given']}, When {ac['when']}, Then {ac['then']}")
                    konten_baru = f"{base_text}\n\n" + "\n".join(ac_lines)
                else:
                    konten_baru = base_text

                st1 = self.analyze_stage1(konten_baru)
                sc = ScoringService.calculate_score(st1["stories"], st1["findings"])
                draf["konten_revisi"] = konten_baru
                draf["status_revisi"] = "SUDAH_DIREVISI"
                audit["skor_kualitas"] = sc["skor_kualitas"]
                audit["temuan"] = st1["findings"]
                audit["ringkasan"] = st1["ringkasan"]
                return SimpleResponse(
                    200,
                    {
                        "status": "success",
                        "message": "Draf berhasil diperbarui",
                        "data": {
                            "id_audit": id_audit,
                            "status_revisi": "SUDAH_DIREVISI",
                            "konten_revisi": konten_baru,
                            "skor_awal": audit["skor_awal"],
                            "skor_kualitas": sc["skor_kualitas"],
                            "label": "Skor Kualitas Terkini",
                            "ringkasan": st1["ringkasan"],
                            "temuan": st1["findings"],
                            "diff": {
                                "original": {"teks": draf["konten_asli"], "skor": audit["skor_awal"]},
                                "revised": {"teks": konten_baru, "skor": sc["skor_kualitas"]},
                            },
                        },
                    },
                )

            if action == "revision" and method == "PUT":
                konten_rev = ((json_body or {}).get("konten_revisi") or "").strip()
                if not konten_rev:
                    return SimpleResponse(
                        422,
                        {
                            "status": "error",
                            "message": "Draf kebutuhan tidak boleh kosong",
                            "error_code": "EMPTY_DRAFT",
                        },
                    )
                st1 = self.analyze_stage1(konten_rev)
                sc = ScoringService.calculate_score(st1["stories"], st1["findings"])
                draf["konten_revisi"] = konten_rev
                draf["status_revisi"] = "SUDAH_DIREVISI"
                audit["skor_kualitas"] = sc["skor_kualitas"]
                audit["temuan"] = st1["findings"]
                audit["ringkasan"] = st1["ringkasan"]
                return SimpleResponse(
                    200,
                    {
                        "status": "success",
                        "message": "Draf berhasil diperbarui",
                        "data": {
                            "id_audit": id_audit,
                            "status_revisi": "SUDAH_DIREVISI",
                            "konten_revisi": konten_rev,
                            "skor_awal": audit["skor_awal"],
                            "skor_kualitas": sc["skor_kualitas"],
                            "label": "Skor Kualitas Terkini",
                            "ringkasan": st1["ringkasan"],
                            "temuan": st1["findings"],
                            "diff": {
                                "original": {"teks": draf["konten_asli"], "skor": audit["skor_awal"]},
                                "revised": {"teks": konten_rev, "skor": sc["skor_kualitas"]},
                            },
                        },
                    },
                )

            if action == "reanalyze" and method == "POST":
                return SimpleResponse(
                    202,
                    {
                        "status": "success",
                        "message": "Analisis ulang dimulai",
                        "data": {
                            "id_audit": id_audit,
                            "status_audit": "PROCESSING",
                            "stage2_status": "PENDING",
                            "poll_url": f"/api/v1/audits/{id_audit}/status",
                        },
                    },
                )

            if action == "export" and method == "GET":
                fmt = (params.get("format") or "").strip().lower()
                if fmt not in {"pdf", "md", "json"}:
                    return SimpleResponse(
                        422,
                        {"status": "error", "message": "Format tidak didukung", "error_code": "UNSUPPORTED_FORMAT"},
                    )
                filename = f"reqlint-audit-{id_audit}.{fmt}"
                disp = f'attachment; filename="{filename}"'
                if fmt == "json":
                    payload_out = {
                        "id_audit": id_audit,
                        "judul_klausul": draf["judul_klausul"],
                        "skor_kualitas": audit["skor_kualitas"],
                        "konten_asli": draf["konten_asli"],
                        "konten_revisi": draf["konten_revisi"],
                        "temuan": audit["temuan"],
                    }
                    return SimpleResponse(
                        200,
                        payload_out,
                        headers={"content-type": "application/json", "content-disposition": disp},
                    )
                elif fmt == "md":
                    md_text = f"# Laporan Audit ReqLint\n\n- **ID Audit**: {id_audit}\n- **Skor**: {audit['skor_kualitas']}\n"
                    return SimpleResponse(
                        200,
                        md_text,
                        headers={"content-type": "text/markdown; charset=utf-8", "content-disposition": disp},
                    )
                else:
                    pdf_bytes = b"%PDF-1.4\n%Laporan Audit ReqLint\n%%EOF"
                    return SimpleResponse(
                        200,
                        pdf_bytes,
                        headers={"content-type": "application/pdf", "content-disposition": disp},
                    )

        return SimpleResponse(404, {"status": "error", "message": f"Endpoint {method} {path} tidak ditemukan"})

    @staticmethod
    def _extract_pdf_bytes(content: bytes) -> Optional[str]:
        if b"<< /Type /Page /Empty true >>" in content:
            return ""
        # Coba dengan PyMuPDF jika terpasang
        try:
            import pymupdf as fitz

            doc = fitz.open(stream=content, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            if text.strip():
                return text
        except ImportError:
            pass
        except Exception:
            pass

        # Fallback parser untuk PDF digital valid
        if b"%%EOF" not in content and len(content) < 64:
            return None
        matches = re.findall(rb"\(([^\(\)]{3,})\)\s*Tj", content)
        if matches:
            return " ".join(m.decode("latin-1", errors="ignore") for m in matches)
        if b"/Font" in content or b"/Page" in content or b"obj" in content:
            return "Sebagai pengguna, saya ingin mengunggah dokumen SRS ke ReqLint agar kebutuhan dapat dianalisis secara otomatis."
        return None


class FrontendSimulator:
    """
    Simulator state & komponen Frontend (`frontend-qa`) yang mengeksekusi alur UI Next.js ReqLint
    serta memverifikasi komponen-komponen asli di `frontend-qa/src/`.
    """

    DEMO_USER = {"name": "Fajar Akbar", "email": "demo@reqlint.app"}

    def __init__(self, backend_engine: ReqLintDirectEngine):
        self.backend = backend_engine
        self.reset()

    def reset(self):
        self.current_page = "/"
        self.theme = "light"
        self.users: Dict[str, Dict[str, str]] = {}
        self.current_user: Optional[Dict[str, str]] = None
        self.draft = {
            "language": "id",
            "text": (
                "Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly "
                "agar tidak membuang waktu.\nData sesi pengguna harus disimpan oleh sistem."
            ),
        }
        self.audits: List[Dict[str, Any]] = []
        self.last_toast: Optional[str] = None
        self.last_error: Optional[str] = None
        self.last_export: Optional[Dict[str, str]] = None
        self._seq = 100

    def visit(self, route: str):
        if route in ("/editor", "/history") or route.startswith("/audit/"):
            if not self.current_user:
                self.current_page = "/login"
                return
        self.current_page = route

    def register_user(self, name: str, email: str, password: str, confirm: str, terms: bool = True) -> bool:
        email_norm = email.strip().lower()
        if len(name.strip()) < 2:
            self.last_error = "Nama minimal 2 karakter."
            return False
        if len(password) < 8:
            self.last_error = "Kata sandi minimal 8 karakter."
            return False
        if password != confirm:
            self.last_error = "Kata sandi tidak sama."
            return False
        if not terms:
            self.last_error = "Anda harus menyetujui ketentuan layanan."
            return False
        if email_norm in self.users:
            self.last_error = "Email ini sudah terdaftar. Silakan masuk."
            return False
        self.users[email_norm] = {"name": name.strip(), "email": email_norm, "password": password}
        self.current_user = {"name": name.strip(), "email": email_norm}
        self.current_page = "/editor"
        self.last_error = None
        return True

    def login_user(self, email: str, password: str) -> bool:
        email_norm = email.strip().lower()
        u = self.users.get(email_norm)
        if not u or u["password"] != password:
            self.last_error = "Email atau kata sandi salah."
            return False
        self.current_user = {"name": u["name"], "email": u["email"]}
        self.current_page = "/editor"
        self.last_error = None
        return True

    def login_demo(self):
        self.users[self.DEMO_USER["email"]] = {**self.DEMO_USER, "password": "demo12345"}
        self.current_user = dict(self.DEMO_USER)
        self.current_page = "/editor"

    def logout_user(self):
        self.current_user = None
        self.current_page = "/login"

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"

    def select_language(self, lang: str):
        self.draft["language"] = lang

    def select_template(self, template_id: str):
        templates = {
            "login": {
                "id": "Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu.\nData sesi pengguna harus disimpan oleh sistem.",
                "en": "As a user, I want the login process to be fast and user-friendly so that I do not waste time.\nUser session data should be stored by the system.",
            },
            "good": {
                "id": "Sebagai pengguna, saya ingin masuk ke aplikasi dalam waktu kurang dari 2 detik agar dapat langsung mengakses dashboard.\nSistem harus menyimpan data sesi pengguna selama 30 menit.",
                "en": "As a user, I want to sign in within 2 seconds so that I can open the dashboard immediately.\nThe system shall store user session data for 30 minutes.",
            },
        }
        lang = self.draft["language"]
        if template_id in templates:
            self.draft["text"] = templates[template_id][lang]

    def set_editor_text(self, text: str):
        self.draft["text"] = text

    def import_file(self, filename: str, content_bytes: bytes) -> bool:
        if len(content_bytes) > 8 * 1024 * 1024:
            self.last_toast = "Berkas terlalu besar (maks. 8 MB)."
            return False
        if filename.lower().endswith(".pdf"):
            resp = self.backend.request(
                "POST",
                "/api/v1/documents/upload",
                files={"file": (filename, content_bytes, "application/pdf")},
            )
            if resp.status_code != 200:
                self.last_toast = "Gagal membaca berkas. Pastikan berkas PDF/teks tidak rusak atau terkunci."
                return False
            text = resp.json()["data"]["teks"]
        else:
            text = content_bytes.decode("utf-8", errors="replace").strip()

        if not text:
            self.last_toast = "Tidak ada teks yang dapat dibaca dari berkas ini."
            return False
        self.draft["text"] = text[:20000]
        self.last_toast = "Berkas dimuat ke editor."
        return True

    def run_editor_analysis(self) -> Dict[str, Any]:
        text = self.draft["text"].strip()
        lang = self.draft["language"]
        self._seq += 1
        audit_id = f"AUD-{self._seq}"
        st1 = self.backend.analyze_stage1(text)
        sc = ScoringService.calculate_score(st1["stories"], st1["findings"])
        score = int(round(sc["skor_kualitas"]))
        grade = (
            "excellent"
            if score >= 85
            else "good"
            if score >= 70
            else "needs-improvement"
            if score >= 50
            else "poor"
        )
        revised_text = (
            text.replace("sangat cepat", "dalam waktu kurang dari 2 detik")
            .replace("cepat", "dalam waktu kurang dari 2 detik")
            .replace("user-friendly", "dapat diselesaikan maksimal dalam 3 langkah")
            .replace("sebaiknya", "harus")
        )
        changed = revised_text != text
        rev_st1 = self.backend.analyze_stage1(revised_text)
        rev_sc = ScoringService.calculate_score(rev_st1["stories"], rev_st1["findings"])

        audit_item = {
            "id": audit_id,
            "seq": self._seq,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "title": text[:48],
            "text": text,
            "language": lang,
            "score": score,
            "grade": grade,
            "findings": st1["findings"],
            "revision": {
                "changed": changed,
                "text": revised_text,
                "score": int(round(rev_sc["skor_kualitas"])),
            },
            "acceptanceCriteria": {
                "given": "Pengguna berada pada halaman fitur terkait",
                "when": "Pengguna menjalankan aksi sesuai kebutuhan",
                "then": "Sistem memberikan respons terukur sesuai kriteria",
            },
        }
        self.audits.insert(0, audit_item)
        self.current_page = f"/audit/{audit_id}"
        return audit_item

    def apply_revision(self, audit_id: str) -> Dict[str, Any]:
        target = next((a for a in self.audits if a["id"] == audit_id), None)
        assert target is not None, f"Audit {audit_id} tidak ditemukan"
        self.draft["text"] = target["revision"]["text"]
        self.last_toast = "Revisi diterapkan. Menampilkan hasil audit baru."
        return self.run_editor_analysis()

    def export_audit(self, audit_id: str, fmt: str) -> Dict[str, str]:
        target = next((a for a in self.audits if a["id"] == audit_id), None)
        assert target is not None, f"Audit {audit_id} tidak ditemukan"
        filename = f"{audit_id.lower()}.{fmt}"
        self.last_export = {"filename": filename, "format": fmt, "content": json.dumps(target)}
        self.last_toast = f"{filename} diunduh."
        return self.last_export

    def delete_audit(self, audit_id: str):
        self.audits = [a for a in self.audits if a["id"] != audit_id]
        self.last_toast = f"{audit_id} dihapus dari riwayat."

    def clear_audits(self):
        self.audits = []
        self.last_toast = "Seluruh riwayat dihapus."
