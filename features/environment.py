"""
Konfigurasi lifecycle Behave (before_all, before_feature, before_scenario, before_step, after_step, after_all)
untuk menjalankan BDD Testing Behave sekaligus membuka dan menguji halaman-halaman web asli ReqLint (http://localhost:3000).
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from features.bdd_support.helpers import new_scenario_vars
from features.bdd_support.reqlint_client import ReqLintDirectEngine, FrontendSimulator
from features.bdd_support.live_web_runner import RealWebAppRunner


def _as_bool(val, default=True) -> bool:
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def before_all(context):
    context.root_dir = ROOT_DIR
    context.backend = ReqLintDirectEngine()
    context.frontend = FrontendSimulator(context.backend)

    userdata = context.config.userdata
    open_browser = _as_bool(userdata.get("open_browser"), default=True)
    headless = _as_bool(userdata.get("headless"), default=False)
    step_delay = float(userdata.get("step_delay", 0.35))
    frontend_url = userdata.get("frontend_url", "http://localhost:3000")
    backend_url = userdata.get("backend_url", "http://localhost:8000")

    context.web = RealWebAppRunner(
        backend_engine=context.backend,
        frontend_sim=context.frontend,
        open_browser=open_browser,
        headless=headless,
        step_delay=step_delay,
        frontend_url=frontend_url,
        backend_url=backend_url,
    )
    context.live_runner = context.web
    context.web.start()


def before_feature(context, feature):
    context.current_feature_name = feature.name


def before_scenario(context, scenario):
    context.vars = new_scenario_vars()
    context.backend.reset()
    context.frontend.reset()
    context.response = None
    context.data = None
    context.auth_headers = {}
    context.second_user_headers = {}
    if getattr(context, "web", None) is not None:
        context.web.reset_browser_state()


def before_step(context, step):
    pass


def after_step(context, step):
    pass


def after_all(context):
    if getattr(context, "web", None) is not None:
        context.web.stop()
