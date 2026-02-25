# Project Structure Guide — Video-Based Sponsorship Analytics System

> **Document type:** Codebase Structure Reference  
> **Last updated:** February 2026

---

## 1. Full Directory Layout

```
e:\FYP\
│
├── README.md                          ← Project overview and quick start
│
├── .env.example                       ← Template for environment variables
├── .env                               ← Local config (NOT committed to git)
├── .gitignore                         ← Exclude venv, data, models, __pycache__
├── requirements.txt                   ← Python dependencies
│
├── config.py                          ← Loads .env values, shared constants
│
├── docs/
│   ├── architecture.md                ← Full pipeline architecture
│   ├── plan.md                        ← Phased development roadmap
│   ├── expected_outcome.md            ← Goals and success criteria
│   ├── project_structure.md           ← This file
│   └── modules/
│       ├── 01_video_preprocessing.md
│       ├── 02_frame_extraction.md
│       ├── 03_logo_detection.md
│       ├── 04_exposure_analytics.md
│       └── 05_sponsor_pricing.md
│
├── src/
│   ├── __init__.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── video_preprocessor.py      ← preprocess_video()
│   │
│   ├── frame_extraction/
│   │   ├── __init__.py
│   │   └── frame_extractor.py         ← extract_frames()
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   └── logo_detector.py           ← run_detection()
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── exposure_analytics.py      ← compute_exposure_analytics()
│   │
│   ├── pricing/
│   │   ├── __init__.py
│   │   └── pricing_model.py           ← compute_pricing(), usd_to_npr()
│   │
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py                     ← Main Streamlit or FastAPI app
│   │   ├── routes.py                  ← API route handlers (if FastAPI)
│   │   ├── utils.py                   ← Helper functions for UI
│   │   └── static/                    ← CSS, JS, images (if HTML frontend)
│   │
│   └── pipeline.py                    ← Orchestrates all modules end-to-end
│
├── models/
│   └── yolov8/
│       ├── best.pt                    ← Final fine-tuned YOLOv8 weights
│       ├── last.pt                    ← Last epoch weights (backup)
│       └── data.yaml                  ← Dataset config used for training
│
├── data/
│   ├── raw/                           ← Uploaded videos (temp storage)
│   ├── processed/                     ← Preprocessed videos
│   │   ├── processed_video.mp4
│   │   └── corruption_log.txt
│   ├── frames/                        ← Extracted frame images
│   │   ├── frame_00000.jpg
│   │   └── frames_metadata.csv
│   ├── outputs/                       ← Detection + analytics + pricing outputs
│   │   ├── detections.json
│   │   ├── detections.csv
│   │   ├── exposure_report.json
│   │   ├── exposure_report.csv
│   │   ├── pricing_report.json
│   │   └── pricing_report.csv
│   └── dataset/                       ← YOLOv8 training dataset
│       ├── data.yaml
│       ├── images/
│       │   ├── train/
│       │   ├── val/
│       │   └── test/
│       └── labels/
│           ├── train/
│           ├── val/
│           └── test/
│
├── runs/                              ← YOLOv8 training run outputs (auto-generated)
│   └── detect/
│       └── logo_train/
│           ├── weights/
│           │   ├── best.pt
│           │   └── last.pt
│           ├── results.csv
│           ├── confusion_matrix.png
│           └── PR_curve.png
│
└── tests/
    ├── __init__.py
    ├── test_preprocessing.py
    ├── test_frame_extraction.py
    ├── test_logo_detector.py
    ├── test_exposure_analytics.py
    ├── test_pricing_model.py
    └── fixtures/
        ├── sample_video.mp4           ← Short test video
        ├── sample_detections.csv      ← Mock detection data
        └── sample_frames/             ← Small set of test frames
```

---

## 2. Key Files Reference

| File | Role |
|------|------|
| `config.py` | Single source of truth for all configurable constants |
| `src/pipeline.py` | Orchestrates preprocessing → extraction → detection → analytics → pricing |
| `src/web/app.py` | Entry point for the web application |
| `models/yolov8/best.pt` | The trained detection model — most critical asset |
| `data/outputs/pricing_report.json` | Final output of the system |
| `.env` | API keys and local overrides (never commit) |
| `requirements.txt` | All pip dependencies |

---

## 3. `.env.example` Template

```env
# YOLOv8
MODEL_PATH=models/yolov8/best.pt
CONFIDENCE_THRESHOLD=0.25
IOU_THRESHOLD=0.45

# Frame Extraction
SAMPLE_FPS=2.0

# Video Preprocessing
TARGET_WIDTH=1280
TARGET_HEIGHT=720
TARGET_FPS=30
MAX_FILE_SIZE_MB=500
VARIANCE_THRESHOLD=10

# Analytics
GAP_TOLERANCE_SEC=1.0
MIN_SEGMENT_DURATION_SEC=0.5

# Pricing
WEIGHT_DURATION=0.40
WEIGHT_COVERAGE=0.30
WEIGHT_CONFIDENCE=0.15
WEIGHT_FREQUENCY=0.15
BASE_VALUE_USD=5000
MAX_DURATION_SEC=300
MAX_COVERAGE_PCT=10.0
MAX_FREQUENCY=600

# Currency
STATIC_NPR_RATE=135.00
EXCHANGE_RATE_API_KEY=
```

---

## 4. `requirements.txt` (Initial)

```
ultralytics>=8.0.0
opencv-python>=4.8.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
plotly>=5.15.0
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0
pillow>=10.0.0
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=7.4.0
torch>=2.0.0
torchvision>=0.15.0
```

---

## 5. `.gitignore` (Key Entries)

```gitignore
# Virtual environment
venv/
.venv/
env/

# Data (large files)
data/raw/
data/processed/
data/frames/
data/dataset/

# Model weights
models/yolov8/*.pt

# Training runs
runs/

# Environment secrets
.env

# Python cache
__pycache__/
*.pyc
*.pyo

# OS files
.DS_Store
Thumbs.db
```

---

## 6. Module Dependency Graph

```
config.py
    │
    ├── src/preprocessing/video_preprocessor.py
    │       │
    │       └── src/frame_extraction/frame_extractor.py
    │               │
    │               └── src/detection/logo_detector.py
    │                       │
    │                       └── src/analytics/exposure_analytics.py
    │                               │
    │                               └── src/pricing/pricing_model.py
    │                                       │
    │                                       └── src/web/app.py
    │
    └── (all modules import config.py for constants)
```

---

## 7. Running Individual Modules (CLI Usage Pattern)

```python
# preprocessing
from src.preprocessing.video_preprocessor import preprocess_video
output_path, meta = preprocess_video("data/raw/match.mp4", "data/processed/")

# frame extraction
from src.frame_extraction.frame_extractor import extract_frames
metadata_path, count = extract_frames("data/processed/processed_video.mp4", "data/frames/")

# detection
from src.detection.logo_detector import run_detection
detections = run_detection("data/frames/frames_metadata.csv", "models/yolov8/best.pt")

# analytics
from src.analytics.exposure_analytics import compute_exposure_analytics
report = compute_exposure_analytics("data/outputs/detections.csv")

# pricing
from src.pricing.pricing_model import compute_pricing
pricing = compute_pricing(report, weights={"duration":0.4,"coverage":0.3,"confidence":0.15,"frequency":0.15})

# or run everything via pipeline
from src.pipeline import run_pipeline
results = run_pipeline("data/raw/match.mp4")
```

---

*Refer to module-specific docs in `docs/modules/` for implementation details.*
