"""
config.py
─────────────────────────────────────────────────────────────
Central configuration — loads .env and exposes typed settings.
Every module imports from here instead of reading os.environ directly.
─────────────────────────────────────────────────────────────
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# ── Application ──────────────────────────────────────────────
APP_NAME  = os.getenv("APP_NAME", "AI Answer Evaluation System")
APP_ENV   = os.getenv("APP_ENV",  "development")
APP_DEBUG = os.getenv("APP_DEBUG", "True") == "True"
APP_PORT  = int(os.getenv("APP_PORT", 8000))
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

# ── Database ─────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/ai_evaluation_db"
)

# ── Model Paths ──────────────────────────────────────────────
CRNN_MODEL_PATH  = BASE_DIR / os.getenv("CRNN_MODEL_PATH", "models/saved/crnn_finetuned.pth")
SBERT_MODEL_NAME = os.getenv("SBERT_MODEL_NAME", "all-MiniLM-L6-v2")
TESSERACT_CMD    = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")

# ── OCR Settings ─────────────────────────────────────────────
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", 0.6))
OCR_ENGINE               = os.getenv("OCR_ENGINE", "hybrid")   # crnn | tesseract | hybrid

# ── Scoring Weights ──────────────────────────────────────────
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", 0.5))
KEYWORD_WEIGHT  = float(os.getenv("KEYWORD_WEIGHT",  0.3))
GRAMMAR_WEIGHT  = float(os.getenv("GRAMMAR_WEIGHT",  0.2))

# ── File Upload ──────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB  = int(os.getenv("MAX_UPLOAD_SIZE_MB", 10))
ALLOWED_EXTENSIONS  = set(os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,pdf").split(","))
UPLOAD_DIR          = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── CORS ─────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")


# ── Validation ───────────────────────────────────────────────
def validate():
    total_weight = round(SEMANTIC_WEIGHT + KEYWORD_WEIGHT + GRAMMAR_WEIGHT, 4)
    assert total_weight == 1.0, (
        f"Scoring weights must sum to 1.0 — current sum: {total_weight}"
    )
    print(f"✅  Config loaded  |  ENV={APP_ENV}  |  OCR={OCR_ENGINE}")


if __name__ == "__main__":
    validate()
