"""
scripts/setup.py
─────────────────────────────────────────────────────────────
Phase 1 Setup Script — run once to bootstrap the environment.
  • Creates virtual environment
  • Installs all requirements
  • Copies .env.example → .env  (if .env missing)
  • Creates uploads/ folder
  • Verifies key tool availability (tesseract, mysql)
─────────────────────────────────────────────────────────────
Usage:
    python scripts/setup.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / "venv"
REQ  = ROOT / "requirements.txt"
ENV  = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"


def run(cmd: str, check: bool = True):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode


def banner(msg: str):
    print(f"\n{'─'*55}")
    print(f"  {msg}")
    print(f"{'─'*55}")


# ── Step 1 — Virtual environment ─────────────────────────────
banner("Step 1 — Creating virtual environment")
if not VENV.exists():
    run(f"{sys.executable} -m venv {VENV}")
    print("  ✅  venv created")
else:
    print("  ⏭   venv already exists, skipping")

PY = VENV / "bin" / "python" if os.name != "nt" else VENV / "Scripts" / "python.exe"

# ── Step 2 — Install dependencies ────────────────────────────
banner("Step 2 — Installing Python dependencies")
run(f"{PY} -m pip install --upgrade pip")
run(f"{PY} -m pip install -r {REQ}")
print("  ✅  Dependencies installed")

# ── Step 3 — Environment file ────────────────────────────────
banner("Step 3 — Environment file")
if not ENV.exists():
    shutil.copy(ENV_EXAMPLE, ENV)
    print("  ✅  .env created from .env.example")
    print("  ⚠️   Please edit .env and set DB_PASSWORD and SECRET_KEY")
else:
    print("  ⏭   .env already exists, skipping")

# ── Step 4 — Create uploads directory ────────────────────────
banner("Step 4 — Upload directory")
(ROOT / "uploads").mkdir(exist_ok=True)
print("  ✅  uploads/ folder ready")

# ── Step 5 — Verify external tools ───────────────────────────
banner("Step 5 — Verifying external tools")

tesseract_ok = shutil.which("tesseract") is not None
mysql_ok     = shutil.which("mysql")     is not None

print(f"  Tesseract OCR : {'✅  Found' if tesseract_ok else '❌  Not found — install: sudo apt install tesseract-ocr'}")
print(f"  MySQL         : {'✅  Found' if mysql_ok     else '❌  Not found — install: sudo apt install mysql-server'}")

# ── Step 6 — Download NLTK data ──────────────────────────────
banner("Step 6 — Downloading NLTK data")
run(f'{PY} -c "import nltk; nltk.download(\'punkt\'); nltk.download(\'stopwords\')"', check=False)
print("  ✅  NLTK data ready")

# ── Done ─────────────────────────────────────────────────────
banner("✅  Phase 1 Setup Complete!")
print("""
  Next steps:
  1. Edit .env  →  set DB_PASSWORD, SECRET_KEY
  2. Start MySQL and run:  mysql -u root -p < database/schema.sql
  3. Activate venv:        source venv/bin/activate
  4. Run backend:          uvicorn backend.main:app --reload
  5. When ready, send Phase 2 prompt to continue!
""")
