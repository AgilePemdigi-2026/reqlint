"""
Step definitions Behave untuk fitur Upload Dokumen PDF (upload_pdf_document.feature).
Jalankan dengan perintah: behave
"""
import sys
from pathlib import Path
from behave import given, when, then

ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from features.steps.reqlint_steps import (  # noqa: F401
    step_upload_endpoint_ready,
    step_upload_named_pdf,
    step_status_200_ok,
    step_confirm_pdf_extracted,
)
