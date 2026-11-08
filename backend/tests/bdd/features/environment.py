"""Environment Behave untuk folder backend/tests/bdd/features."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from features.environment import (  # noqa: F401
    before_all,
    before_feature,
    before_scenario,
    before_step,
    after_step,
    after_all,
)
