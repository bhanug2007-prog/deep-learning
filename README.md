# 🎓 AI Answer Evaluation System

Automatically evaluates descriptive answer sheets by:
1. **Extracting handwritten text** using a fine-tuned CRNN OCR model *(Trained Model)*
2. **Scoring semantically** using Sentence-BERT cosine similarity *(Pretrained Model)*
3. **Keyword & grammar scoring** using rule-based NLP

---

## 📁 Project Structure

```
AI_Answer_Evaluation/
│
├── frontend/                  # React + Vite UI
│   ├── public/
│   └── src/
│       ├── components/        # Reusable UI components
│       ├── pages/             # Dashboard, Upload, Results
│       ├── services/          # Axios API calls
│       └── styles/            # CSS / Tailwind
│
├── backend/                   # FastAPI application
│   ├── routes/                # API endpoint routers
│   ├── services/              # Business logic
│   ├── utils/                 # Helper functions
│   └── middleware/            # Auth, logging, CORS
│
├── models/
│   ├── crnn/                  # CRNN architecture + training
│   ├── sbert/                 # Sentence-BERT wrapper
│   └── saved/                 # Saved .pth weight files
│
├── dataset/
│   ├── raw/                   # Original downloaded images
│   ├── processed/             # Preprocessed (resized, normalized)
│   ├── augmented/             # Augmented training images
│   └── iam_sample/            # IAM handwriting dataset samples
│
├── database/
│   ├── schema.sql             # MySQL table definitions + seed data
│   └── models.py              # SQLAlchemy ORM models
│
├── notebooks/                 # Jupyter notebooks for experiments
├── tests/
│   ├── unit/                  # Unit tests per module
│   └── integration/           # End-to-end API tests
│
├── scripts/
│   └── setup.py               # One-command environment setup
│
├── docs/                      # Additional documentation
│
├── config.py                  # Central configuration loader
├── requirements.txt           # All Python dependencies
├── .env.example               # Environment variable template
└── .gitignore
```

---

## 🤖 AI Architecture

| Component | Type | Model | Purpose |
|-----------|------|-------|---------|
| OCR | **Trained** | CRNN (ResNet18 + BiLSTM + CTC) | Extract text from handwritten images |
| Semantic Scoring | **Pretrained** | Sentence-BERT (`all-MiniLM-L6-v2`) | Compare student answer vs model answer |
| Keyword Scoring | Rule-based | NLTK + custom logic | Check presence of key terms |
| Grammar Scoring | Rule-based | SpaCy | Sentence structure quality |

---

## 🚀 Phase-by-Phase Plan

| Phase | Description | Status |
|-------|-------------|--------|
| **1** | Project Setup — folders, requirements, config | ✅ Done |
| **2** | Database Design — MySQL schema + ORM models | ⏳ Next |
| **3** | OCR Model Training — CRNN fine-tuning on IAM | 🔜 |
| **4** | Backend Development — FastAPI REST endpoints | 🔜 |
| **5** | AI Evaluation Pipeline — OCR + SBERT scoring | 🔜 |
| **6** | Frontend Development — React dashboard | 🔜 |
| **7** | Testing & Deployment | 🔜 |

---

## ⚙️ Phase 1 Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Tesseract OCR
- Node.js 18+ (for frontend, later)

### Install (Linux/macOS)
```bash
# 1. Clone / navigate to project
cd AI_Answer_Evaluation

# 2. Run setup script (creates venv + installs all packages)
python scripts/setup.py

# 3. Activate virtual environment
source venv/bin/activate

# 4. Configure environment
cp .env.example .env
# → Edit .env: set DB_PASSWORD and SECRET_KEY

# 5. Verify config loads correctly
python config.py
```

### Install Tesseract (Ubuntu)
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### Install MySQL (Ubuntu)
```bash
sudo apt install mysql-server
sudo mysql_secure_installation
```

---

## 📦 Key Dependencies

```
torch / torchvision       → CRNN training
sentence-transformers     → Sentence-BERT semantic scoring
opencv-python             → Image preprocessing
pytesseract               → Tesseract OCR fallback
fastapi + uvicorn         → REST API backend
sqlalchemy + pymysql      → MySQL ORM
```

---

## 📝 License
MIT — Academic / Educational Use
