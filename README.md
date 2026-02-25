# Video-Based Sponsorship Analytics System

> **Final Year Project (FYP)**  
> Date Started: February 2026  
> Status: Planning & Development

---

## Project Summary

An automated system that processes uploaded videos to detect brand logos using YOLOv8, computes sponsorship exposure metrics, and estimates a sponsorship pricing score. The system exposes results via a web interface with visual summaries and tabular reports. Pricing is interconvertible between **USD** and **NPR**.

---

## System Pipeline (High-Level)

```
Video Upload
     ↓
Video Preprocessing      (resolution, FPS, format, corrupted frames)
     ↓
Frame Extraction         (OpenCV, indexed + timestamped)
     ↓
Logo Detection           (YOLOv8, bounding box, confidence, class label)
     ↓
Exposure Analytics       (duration, frequency, screen coverage, segments)
     ↓
Sponsor Pricing Model    (weighted scoring → USD / NPR estimate)
     ↓
Web Interface Output     (charts, tables, report)
```

---

## Repository Structure

```
FYP/
├── README.md                        ← You are here
├── docs/
│   ├── architecture.md              ← Full system architecture description
│   ├── plan.md                      ← Phased development plan & milestones
│   ├── expected_outcome.md          ← Expected outcomes & success criteria
│   ├── project_structure.md         ← Codebase directory layout guide
│   └── modules/
│       ├── 01_video_preprocessing.md
│       ├── 02_frame_extraction.md
│       ├── 03_logo_detection.md
│       ├── 04_exposure_analytics.md
│       └── 05_sponsor_pricing.md
├── src/
│   ├── preprocessing/
│   ├── frame_extraction/
│   ├── detection/
│   ├── analytics/
│   ├── pricing/
│   └── web/
├── models/
│   └── yolov8/ (prefered - nano or efficient)
├── data/
│   ├── raw/
│   ├── frames/
│   └── outputs/
├── tests/
├── requirements.txt
└── .env.example
```

---

## Core Technologies

| Layer               | Technology                          |
|---------------------|-------------------------------------|
| Object Detection    | YOLOv8 (Ultralytics)                |
| Video Processing    | OpenCV (`cv2`)                      |
| Backend             | Python (FastAPI or Flask)           |
| Frontend            | HTML/CSS/JS or Streamlit (TBD)      |
| Data Storage        | JSON / CSV / SQLite                 |
| Visualization       | Matplotlib, Plotly                  |
| Currency Conversion | Static rate or ExchangeRate API     |

---

## Documentation Index

| File | Purpose |
|------|---------|
| [docs/architecture.md](docs/architecture.md) | Full pipeline architecture |
| [docs/plan.md](docs/plan.md) | Development phases and task breakdown |
| [docs/modules/01_video_preprocessing.md](docs/modules/01_video_preprocessing.md) | Preprocessing module detail |
| [docs/modules/02_frame_extraction.md](docs/modules/02_frame_extraction.md) | Frame extraction module detail |
| [docs/modules/03_logo_detection.md](docs/modules/03_logo_detection.md) | YOLOv8 detection module detail |
| [docs/modules/04_exposure_analytics.md](docs/modules/04_exposure_analytics.md) | Analytics engine detail |
| [docs/modules/05_sponsor_pricing.md](docs/modules/05_sponsor_pricing.md) | Pricing model detail |
| [docs/expected_outcome.md](docs/expected_outcome.md) | Goals and success criteria |
| [docs/project_structure.md](docs/project_structure.md) | Codebase structure guide |

---

## Quick Start (to be updated as code is added)

```bash
# 1. Clone / open project
cd "e:\FYP"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the web app
python src/web/app.py
```

---

## Currency Conversion Note

All sponsorship value estimates are produced in **USD** by default.  
An interconversion button/toggle converts values to **NPR** (Nepalese Rupee) using a configurable exchange rate (static fallback: **1 USD = 135.00 NPR**, updatable via API).

---

*Refer to individual module docs under `docs/modules/` for implementation details.*
