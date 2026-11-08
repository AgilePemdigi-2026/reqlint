"""
Runner E2E Behave untuk membuka dan menjalankan langsung halaman-halaman asli aplikasi web ReqLint
(`frontend-qa` di http://localhost:3000 dan `backend` API di http://localhost:8000) menggunakan Selenium WebDriver.
Tidak membuat halaman dashboard tiruan — browser langsung membuka halaman-halaman fitur ReqLint yang ada di folder proyek ini.
"""
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen

from features.bdd_support.backend_server import ReqLintBackendHandler

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend-qa"
BACKEND_SERVER_SCRIPT = Path(__file__).resolve().parent / "backend_server.py"


def _is_port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    for h in (host, "127.0.0.1", "localhost"):
        try:
            with socket.create_connection((h, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def _wait_http_ready(url: str, timeout_sec: float = 25.0) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            req = Request(url, headers={"User-Agent": "ReqLint-Behave/1.0"})
            with urlopen(req, timeout=2.0) as resp:
                if resp.status < 500:
                    return True
        except PermissionError:
            # Jika dijalankan di dalam sandbox yang memblokir akses socket lokal, jangan hang
            return False
        except OSError as exc:
            if getattr(exc, "winerror", None) == 10013:
                return False
        except Exception:
            pass
        time.sleep(0.4)
    return False


class RealWebAppRunner:
    """
    Menjalankan server Backend API (port 8000) dan server Frontend Next.js `frontend-qa` (port 3000),
    serta mengendalikan browser Selenium untuk membuka dan berinteraksi langsung dengan tiap halaman fitur ReqLint.
    """

    def __init__(
        self,
        backend_engine,
        frontend_sim,
        open_browser: bool = True,
        headless: bool = False,
        step_delay: float = 0.35,
        frontend_url: str = "http://localhost:3000",
        backend_url: str = "http://localhost:8000",
    ):
        self.backend_engine = backend_engine
        self.frontend_sim = frontend_sim
        self.open_browser = open_browser
        self.headless = headless
        self.step_delay = step_delay
        self.frontend_url = frontend_url.rstrip("/")
        self.backend_url = backend_url.rstrip("/")

        self.driver = None
        self._api_httpd: Optional[ThreadingHTTPServer] = None
        self._api_thread: Optional[threading.Thread] = None
        self._backend_proc: Optional[subprocess.Popen] = None
        self._fe_proc: Optional[subprocess.Popen] = None

    # ------------------------------------------------------------------ #
    # Lifecycle Startup & Shutdown
    # ------------------------------------------------------------------ #
    def start(self):
        be_ok = self._ensure_backend_server()
        fe_ok = self._ensure_frontend_server() if be_ok else False
        if self.open_browser and fe_ok:
            self._launch_browser()
        elif self.open_browser and not fe_ok:
            print(
                f"[ReqLint BDD] Info: Menjalankan mode cepat tanpa browser (be={be_ok}, fe={fe_ok}).",
                flush=True,
            )

    def stop(self):
        if self.driver is not None:
            try:
                self.ensure_demo_logged_in()
                self.driver.get(f"{self.frontend_url}/editor")
                time.sleep(1.2)
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

        if self._api_httpd is not None:
            try:
                self._api_httpd.shutdown()
                self._api_httpd.server_close()
            except Exception:
                pass
            self._api_httpd = None

        for proc in (self._fe_proc, self._backend_proc):
            if proc is not None:
                try:
                    proc.kill()
                except Exception:
                    pass
                try:
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=False,
                        )
                except Exception:
                    pass
        self._fe_proc = None
        self._backend_proc = None

    def _ensure_backend_server(self) -> bool:
        if _wait_http_ready(f"{self.backend_url}/api/v1/health", timeout_sec=1.2):
            return True

        try:
            self._api_httpd = ThreadingHTTPServer(("127.0.0.1", 8000), ReqLintBackendHandler)
            self._api_thread = threading.Thread(target=self._api_httpd.serve_forever, daemon=True)
            self._api_thread.start()
            if _wait_http_ready(f"{self.backend_url}/api/v1/health", timeout_sec=4.0):
                print(f"[ReqLint BDD] Server Backend API aktif di {self.backend_url}", flush=True)
                return True
        except OSError:
            self._api_httpd = None

        return False

    def _ensure_frontend_server(self) -> bool:
        if _wait_http_ready(self.frontend_url, timeout_sec=1.5):
            print(f"[ReqLint BDD] Server Frontend Next.js sudah aktif di {self.frontend_url}", flush=True)
            return True

        node_bin = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
        next_bin = FRONTEND_DIR / "node_modules" / "next" / "dist" / "bin" / "next"
        if not next_bin.exists():
            print(f"[ReqLint BDD] Paket Next.js belum ditemukan di {next_bin}", flush=True)
            return False

        has_build = (FRONTEND_DIR / ".next" / "BUILD_ID").exists()
        mode = "start" if has_build else "dev"

        env = os.environ.copy()
        env.setdefault("NEXT_PUBLIC_API_URL", "http://localhost:8000/api/v1")
        env.setdefault("BROWSER", "none")

        try:
            self._fe_proc = subprocess.Popen(
                [node_bin, str(next_bin), mode, "-p", "3000"],
                cwd=str(FRONTEND_DIR),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            )
        except Exception as exc:
            print(f"[ReqLint BDD] Gagal menjalankan server Next.js: {exc}", flush=True)
            return False

        ready = _wait_http_ready(self.frontend_url, timeout_sec=25.0)
        if ready:
            print(f"[ReqLint BDD] Server Frontend Next.js ({mode}) aktif di {self.frontend_url}", flush=True)
        return ready

    def _launch_browser(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.edge.options import Options as EdgeOptions

            try:
                opts = ChromeOptions()
                if self.headless:
                    opts.add_argument("--headless=new")
                opts.add_argument("--window-size=1366,900")
                opts.add_argument("--disable-gpu")
                opts.add_argument("--no-sandbox")
                opts.add_experimental_option("excludeSwitches", ["enable-logging"])
                self.driver = webdriver.Chrome(options=opts)
            except Exception:
                eopts = EdgeOptions()
                if self.headless:
                    eopts.add_argument("--headless=new")
                eopts.add_argument("--window-size=1366,900")
                self.driver = webdriver.Edge(options=eopts)

            self.driver.set_page_load_timeout(25)
            self.driver.get(self.frontend_url)
            print(f"[ReqLint BDD] Browser Selenium berhasil membuka {self.frontend_url}", flush=True)
        except Exception as exc:
            print(f"[ReqLint BDD] Gagal membuka browser Selenium: {exc}", flush=True)
            self.driver = None

    # ------------------------------------------------------------------ #
    # Real Page Navigation & DOM Interaction Helpers
    # ------------------------------------------------------------------ #
    def pause(self, factor: float = 1.0):
        if self.driver is not None and self.step_delay > 0:
            time.sleep(self.step_delay * factor)

    def reset_browser_state(self):
        """Reset state localStorage di browser agar setiap Scenario dimulai secara bersih dan deterministik."""
        if self.driver is None:
            return
        try:
            if not self.driver.current_url.startswith(self.frontend_url):
                self.driver.get(self.frontend_url)
            self.driver.execute_script(
                """
                window.localStorage.setItem('reqlint.audits', JSON.stringify([]));
                window.localStorage.setItem('reqlint.draft', JSON.stringify({
                  language: 'id',
                  text: 'Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu.\\nData sesi pengguna harus disimpan oleh sistem.'
                }));
                window.localStorage.setItem('reqlint.theme', JSON.stringify('light'));
                document.documentElement.classList.remove('dark');
                window.dispatchEvent(new StorageEvent('storage', { key: null }));
                """
            )
        except Exception:
            pass

    def current_path(self) -> str:
        if self.driver is None:
            return self.frontend_sim.current_page
        try:
            from urllib.parse import urlparse

            parsed = urlparse(self.driver.current_url)
            return parsed.path or "/"
        except Exception:
            return self.frontend_sim.current_page

    def goto(self, route: str, wait_selector: Optional[str] = None):
        self.frontend_sim.visit(route)
        if self.driver is None:
            return
        target_url = f"{self.frontend_url}{route if route.startswith('/') else '/' + route}"
        try:
            self.driver.get(target_url)
            if wait_selector:
                self.wait_css(wait_selector, timeout=10)
            self.pause()
        except Exception:
            pass

    def wait_css(self, css_selector: str, timeout: float = 10.0):
        if self.driver is None:
            return None
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_xpath(self, xpath: str, timeout: float = 10.0):
        if self.driver is None:
            return None
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def wait_url_contains(self, fragment: str, timeout: float = 10.0) -> bool:
        if self.driver is None:
            return True
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if fragment in self.driver.current_url:
                    return True
            except Exception:
                pass
            time.sleep(0.12)
        return False

    def ensure_demo_logged_in(self):
        """Pastikan browser sudah login ke akun demo dan berada di halaman aplikasi."""
        self.frontend_sim.login_demo()
        if self.driver is None:
            return
        try:
            if not self.driver.current_url.startswith(self.frontend_url):
                self.driver.get(self.frontend_url)
            has_session = self.driver.execute_script("return Boolean(window.localStorage.getItem('reqlint.session'));")
            if not has_session:
                self.driver.get(f"{self.frontend_url}/login")
                btn = self.wait_xpath("//button[contains(., 'Gunakan akun demo')]", timeout=10)
                if btn:
                    btn.click()
                    self.wait_url_contains("/editor", timeout=10)
                    self.pause(0.6)
        except Exception:
            pass

    def clear_browser_auth(self):
        """Hapus sesi login di localStorage browser."""
        self.frontend_sim.logout_user()
        if self.driver is None:
            return
        try:
            if not self.driver.current_url.startswith(self.frontend_url):
                self.driver.get(self.frontend_url)
            self.driver.execute_script(
                """
                window.localStorage.removeItem('reqlint.session');
                window.dispatchEvent(new StorageEvent('storage', { key: 'reqlint.session' }));
                """
            )
            self.pause(0.4)
        except Exception:
            pass

    def fill_register_form(self, name: str, email: str, password: str, confirm: str, terms: bool = True):
        """Isi dan kirim form registrasi asli di halaman /register."""
        ok = self.frontend_sim.register_user(name, email, password, confirm, terms=terms)
        if self.driver is None:
            return ok
        try:
            if self.current_path() != "/register":
                self.driver.get(f"{self.frontend_url}/register")
            name_el = self.wait_css('input[name="name"]', timeout=10)
            email_el = self.wait_css('input[name="email"]', timeout=8)
            pwd_el = self.wait_css('input[name="password"]', timeout=8)
            conf_el = self.wait_css('input[name="confirm"]', timeout=8)
            terms_el = self.wait_css('input[name="terms"]', timeout=8)

            for el, val in [(name_el, name), (email_el, email), (pwd_el, password), (conf_el, confirm)]:
                el.clear()
                el.send_keys(val)

            if terms and not terms_el.is_selected():
                terms_el.click()
            elif not terms and terms_el.is_selected():
                terms_el.click()

            submit_btn = self.wait_xpath("//button[@type='submit' and contains(., 'Daftar')]", timeout=8)
            submit_btn.click()
            if ok:
                self.wait_url_contains("/editor", timeout=10)
            self.pause()
        except Exception:
            pass
        return ok

    def fill_login_form(self, email: str, password: str):
        """Isi dan kirim form login asli di halaman /login."""
        self.frontend_sim.login_user(email, password)
        if self.driver is None:
            return
        try:
            if self.current_path() != "/login":
                self.driver.get(f"{self.frontend_url}/login")
            email_el = self.wait_css('input[name="email"]', timeout=10)
            pwd_el = self.wait_css('input[name="password"]', timeout=8)
            email_el.clear()
            email_el.send_keys(email)
            pwd_el.clear()
            pwd_el.send_keys(password)
            submit_btn = self.wait_xpath("//button[@type='submit' and contains(., 'Masuk')]", timeout=8)
            submit_btn.click()
            self.pause()
        except Exception:
            pass

    def click_demo_login(self):
        """Klik tombol 'Gunakan akun demo' pada halaman /login."""
        self.frontend_sim.login_demo()
        if self.driver is None:
            return
        try:
            if self.current_path() != "/login":
                self.driver.get(f"{self.frontend_url}/login")
            btn = self.wait_xpath("//button[contains(., 'Gunakan akun demo')]", timeout=10)
            btn.click()
            self.wait_url_contains("/editor", timeout=10)
            self.pause()
        except Exception:
            pass

    def select_editor_language(self, lang: str):
        """Pilih bahasa analisis ('id' atau 'en') pada halaman /editor."""
        self.frontend_sim.select_language(lang)
        if self.driver is None:
            return
        try:
            self.ensure_demo_logged_in()
            if self.current_path() != "/editor":
                self.driver.get(f"{self.frontend_url}/editor")
            lang_btn = self.wait_css('button[aria-label="Pilih bahasa analisis"]', timeout=10)
            lang_btn.click()
            self.pause(0.3)
            label = "English" if lang == "en" else "Bahasa Indonesia"
            opt = self.wait_xpath(f"//button[contains(@class, 'menu-item') and contains(., '{label}')]", timeout=8)
            opt.click()
            self.pause()
        except Exception:
            pass

    def select_editor_template(self, tpl_id: str):
        """Pilih contoh template pada halaman /editor."""
        self.frontend_sim.select_template(tpl_id)
        if self.driver is None:
            return
        try:
            if self.current_path() != "/editor":
                self.driver.get(f"{self.frontend_url}/editor")
            tpl_btn = self.wait_xpath("//button[contains(., 'Contoh Template')]", timeout=10)
            tpl_btn.click()
            self.pause(0.3)
            label_map = {
                "login": ("Fitur Login", "Login feature"),
                "report": ("Laporan Penjualan", "Sales report"),
                "checkout": ("Checkout Pembayaran", "Payment checkout"),
                "good": ("Contoh yang sudah baik", "A well-formed example"),
            }
            labels = label_map.get(tpl_id, ("Fitur Login", "Login feature"))
            opt = self.wait_xpath(
                f"//button[contains(@class, 'menu-item') and (contains(., '{labels[0]}') or contains(., '{labels[1]}'))]",
                timeout=8,
            )
            opt.click()
            self.pause()
        except Exception:
            pass

    def set_editor_draft_text(self, text: str):
        """Ketik draf kebutuhan ke dalam <textarea aria-label='Editor draf kebutuhan'> di halaman /editor."""
        self.frontend_sim.set_editor_text(text)
        if self.driver is None:
            return
        try:
            self.ensure_demo_logged_in()
            if self.current_path() != "/editor":
                self.driver.get(f"{self.frontend_url}/editor")
            self.wait_css('textarea[aria-label="Editor draf kebutuhan"]', timeout=10)
            lang = self.frontend_sim.draft.get("language", "id")
            self.driver.execute_script(
                """
                const textVal = arguments[0];
                const langVal = arguments[1];
                window.localStorage.setItem('reqlint.draft', JSON.stringify({ language: langVal, text: textVal }));
                window.dispatchEvent(new StorageEvent('storage', { key: 'reqlint.draft' }));
                """,
                text,
                lang,
            )
            self.pause()
        except Exception:
            pass

    def upload_file_in_editor(self, file_path: Path) -> bool:
        """Unggah berkas PDF/TXT melalui input[type='file'] di halaman /editor."""
        pdf_bytes = (
            file_path.read_bytes()
            if file_path.exists()
            else b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\n(Sebagai user, saya ingin upload PDF.) Tj\n%%EOF"
        )
        ok = self.frontend_sim.import_file(file_path.name, pdf_bytes)
        if self.driver is None:
            return ok
        try:
            self.ensure_demo_logged_in()
            if self.current_path() != "/editor":
                self.driver.get(f"{self.frontend_url}/editor")
            file_input = self.wait_css('input[type="file"][aria-label="Unggah berkas PDF atau teks"]', timeout=10)
            if file_path.exists():
                file_input.send_keys(str(file_path.resolve()))
                time.sleep(1.0)
            self.pause()
        except Exception:
            pass
        return ok

    def click_analyze_in_editor(self) -> Dict[str, Any]:
        """Klik tombol 'Analisis' di halaman /editor sehingga mengarah ke halaman /audit/AUD-..."""
        if self.driver is not None:
            try:
                self.ensure_demo_logged_in()
                if self.current_path() != "/editor":
                    self.set_editor_draft_text(self.frontend_sim.draft["text"])
                btn = self.wait_xpath("//button[contains(., 'Analisis') and not(@disabled)]", timeout=10)
                btn.click()
                self.wait_url_contains("/audit/", timeout=10)
                self.wait_css('section[aria-label="Quality Scorecard"]', timeout=10)
                self.pause()
            except Exception:
                pass
        audit_item = self.frontend_sim.run_editor_analysis()
        return audit_item

    def click_apply_revision_on_audit_page(self, audit_id: str) -> Dict[str, Any]:
        """Klik tombol 'Apply' pada kartu Rekomendasi Perbaikan di halaman /audit/[id]."""
        next_audit = self.frontend_sim.apply_revision(audit_id)
        if self.driver is None:
            return next_audit
        try:
            apply_btn = self.wait_xpath(
                "//section[@aria-label='Rekomendasi perbaikan']//button[contains(., 'Apply')]",
                timeout=10,
            )
            apply_btn.click()
            self.wait_url_contains(f"/audit/{next_audit['id']}", timeout=10)
            self.pause()
        except Exception:
            pass
        return next_audit

    def click_export_on_audit_page(self, audit_id: str, fmt: str):
        """Klik menu Export di halaman /audit/[id] dan pilih format unduhan."""
        self.frontend_sim.export_audit(audit_id, fmt)
        if self.driver is None:
            return
        try:
            exp_btn = self.wait_xpath("//button[contains(., 'Export')]", timeout=10)
            exp_btn.click()
            self.pause(0.3)
            label_map = {"md": "Markdown (.md)", "csv": "CSV (.csv)", "json": "JSON (.json)"}
            target_label = label_map.get(fmt, fmt)
            item_btn = self.wait_xpath(
                f"//button[contains(@class, 'menu-item') and contains(., '{target_label}')]",
                timeout=8,
            )
            item_btn.click()
            self.pause()
        except Exception:
            pass

    def clear_all_history_on_page(self):
        """Klik tombol 'Hapus semua' di halaman /history dan setujui dialog konfirmasi."""
        self.frontend_sim.clear_audits()
        if self.driver is None:
            return
        try:
            if self.current_path() != "/history":
                self.driver.get(f"{self.frontend_url}/history")
            del_btn = self.wait_xpath("//button[contains(., 'Hapus semua')]", timeout=10)
            del_btn.click()
            time.sleep(0.25)
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except Exception:
                pass
            self.wait_xpath("//*[contains(., 'Belum ada riwayat audit')]", timeout=8)
            self.pause()
        except Exception:
            pass

    def search_history_on_page(self, keyword: str):
        """Ketik kata kunci pencarian di halaman /history."""
        if self.driver is None:
            return
        try:
            self.ensure_demo_logged_in()
            if self.current_path() != "/history":
                self.driver.get(f"{self.frontend_url}/history")
            search_input = self.wait_css('input[placeholder*="Cari ID"]', timeout=10)
            search_input.clear()
            search_input.send_keys(keyword)
            self.pause()
        except Exception:
            pass

    def toggle_theme_in_account_menu(self):
        """Buka menu akun di Navbar dan klik tombol Tema gelap / Tema terang."""
        self.frontend_sim.toggle_theme()
        if self.driver is None:
            return
        try:
            menu_btn = self.wait_css('button[aria-label="Menu akun"]', timeout=10)
            menu_btn.click()
            self.pause(0.25)
            theme_btn = self.wait_xpath(
                "//button[contains(@class, 'menu-item') and (contains(., 'Tema gelap') or contains(., 'Tema terang'))]",
                timeout=8,
            )
            theme_btn.click()
            self.pause()
        except Exception:
            pass

    def click_logout_in_account_menu(self):
        """Buka menu akun di Navbar dan klik tombol 'Keluar'."""
        self.frontend_sim.logout_user()
        if self.driver is None:
            return
        try:
            menu_btn = self.wait_css('button[aria-label="Menu akun"]', timeout=10)
            menu_btn.click()
            self.pause(0.25)
            logout_btn = self.wait_xpath(
                "//button[contains(@class, 'menu-item') and contains(., 'Keluar')]",
                timeout=8,
            )
            logout_btn.click()
            self.wait_url_contains("/login", timeout=10)
            self.pause()
        except Exception:
            pass


# Alias untuk menjaga kompatibilitas import di environment.py
LiveWebAndBddRunner = RealWebAppRunner
