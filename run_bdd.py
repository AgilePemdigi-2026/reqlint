#!/usr/bin/env python3
"""
ReqLint BDD Test Runner
Executes all Behavior-Driven Development (BDD) test suites using pytest-bdd.
"""

import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding if needed
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    root_dir = Path(__file__).resolve().parent
    backend_dir = root_dir / "backend"

    print("=" * 70)
    print("[BDD] MENJALANKAN PENGUJIAN BDD REQLINT (BEHAVIOR-DRIVEN DEVELOPMENT)")
    print("      Standar Acuan: ISO/IEC/IEEE 29148:2018 & Kriteria INVEST")
    print("=" * 70)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/bdd",
        "--tb=short"
    ]

    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    print(f"Directory : {backend_dir}")
    print(f"Command   : {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=backend_dir)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
