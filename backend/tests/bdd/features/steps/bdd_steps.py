"""Memuat seluruh step definitions Behave dari features/steps/reqlint_steps.py."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[5]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from features.steps.reqlint_steps import *  # noqa: F401,F403

