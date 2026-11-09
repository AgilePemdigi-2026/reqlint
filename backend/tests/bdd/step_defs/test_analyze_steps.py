"""
Step definitions Behave untuk fitur Analisis User Story (analyze_user_story.feature).
Jalankan dengan perintah: behave
"""
import sys
from pathlib import Path
from behave import given, when, then

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from features.steps.reqlint_steps import (  # noqa: F401
    step_system_ready,
    step_send_user_story,
    step_check_detected_lang,
    step_check_two_rules,
    step_check_revisions_list,
)
