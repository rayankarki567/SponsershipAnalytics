# System Architecture — Video-Based Sponsorship Analytics System

> **Document type:** Architecture Reference  
> **Last updated:** February 2026  
> **Status:** Finalized (v1.0)

---

## 1. Overview

The system follows a **sequential, modular processing pipeline**. Each module is independently implemented and communicates with the next through structured data contracts (JSON/CSV). This design supports isolated testing, future replacement of individual components, and clear separation of concerns.

---

## 2. Pipeline Diagram

```
┌─────────────────────────────────────────┐
│          USER (Web Interface)           │
│  Upload video file via browser/UI       │
└───────────────────┬─────────────────────┘
                    │  video file (mp4/avi/mov)
                    ▼
┌─────────────────────────────────────────┐
│        INPUT VALIDATION LAYER           │
│  - File format check                    │
│  - Resolution check                     │
│  - Duration check                       │
└───────────────────┬─────────────────────┘
                    │  valid video
                    ▼
┌─────────────────────────────────────────┐
│  MODULE 1: VIDEO PREPROCESSING          │
│  - Resolution normalization             │
│  - Frame rate standardization           │
│  - Format conversion (if needed)        │
│  - Corrupted frame removal              │
└───────────────────┬─────────────────────┘
                    │  preprocessed video
                    ▼
┌─────────────────────────────────────────┐
│  MODULE 2: FRAME EXTRACTION             │
│  - OpenCV frame decomposition           │
│  - Sampling rate: ~2 fps                │
│  - Index + timestamp each frame         │
└───────────────────┬─────────────────────┘
                    │  indexed frames (images)
                    ▼
┌─────────────────────────────────────────┐
│  MODULE 3: LOGO DETECTION (YOLOv8)      │
│  - Load pretrained YOLOv8 weights       │
│  - Detect predefined logo classes       │
│  - Output: bbox, confidence, class,     │
│            frame timestamp              │
└───────────────────┬─────────────────────┘
                    │  detection records (JSON/CSV)
                    ▼
┌─────────────────────────────────────────┐
│  MODULE 4: EXPOSURE ANALYTICS ENGINE    │
│  - Aggregate frame-level detections     │
│  - Compute: frequency, duration,        │
│    screen coverage ratio, segments      │
│  - Temporal continuity analysis         │
└───────────────────┬─────────────────────┘
                    │  exposure metrics
                    ▼
┌─────────────────────────────────────────┐
│  MODULE 5: SPONSOR PRICING MODEL        │
│  - Weighted linear scoring              │
│  - Inputs: duration, prominence,        │
│    confidence, frequency                │
│  - Output: sponsorship value index      │
│  - USD ↔ NPR conversion                │
└───────────────────┬─────────────────────┘
                    │  pricing report
                    ▼
┌─────────────────────────────────────────┐
│        OUTPUT LAYER (Web Interface)     │
│  - Visual charts (bar, timeline)        │
│  - Tabular report (per sponsor)         │
│  - Download report (CSV/PDF)            │
│  - USD / NPR toggle                     │
└─────────────────────────────────────────┘
```

---

## 3. Data Flow Contracts

### 3.1 After Frame Extraction
Each frame produces a metadata record:

```json
{
  "frame_id": 42,
  "timestamp_sec": 21.0,
  "file_path": "data/frames/frame_042.jpg"
}
```

### 3.2 After Logo Detection
Each detection event:

```json
{
  "frame_id": 42,
  "timestamp_sec": 21.0,
  "logo_class": "NikeLogoInternational",
  "confidence": 0.91,
  "bbox": {
    "x1": 120, "y1": 80, "x2": 240, "y2": 160
  },
  "bbox_area_ratio": 0.034
}
```

### 3.3 After Exposure Analytics
Per-sponsor aggregated metrics:

```json
{
  "sponsor": "NikeLogoInternational",
  "total_detections": 87,
  "total_exposure_sec": 43.5,
  "avg_screen_coverage_pct": 3.4,
  "exposure_segments": [
    {"start_sec": 5.0, "end_sec": 12.0, "duration_sec": 7.0},
    {"start_sec": 30.0, "end_sec": 46.5, "duration_sec": 16.5}
  ]
}
```

### 3.4 After Pricing Model
Pricing output:

```json
{
  "sponsor": "NikeLogoInternational",
  "sponsorship_score": 74.3,
  "estimated_value_usd": 1486.00,
  "estimated_value_npr": 200610.00,
  "exchange_rate_used": 135.00
}
```

---

## 4. Module Independence Principle

Each module:
- Reads input from a **defined input contract** (file or in-memory structure)
- Writes output to a **defined output contract**
- Has its own unit tests
- Can be swapped or upgraded without affecting adjacent modules

---

## 5. Validation Layer Details

| Check | Criteria |
|-------|----------|
| File format | `.mp4`, `.avi`, `.mov`, `.mkv` |
| Min resolution | 360p (640×360) |
| Max file size | 500 MB (configurable) |
| Min duration | 5 seconds |
| Max duration | 3 hours (configurable) |

---

## 6. Technology Stack

| Component | Technology |
|-----------|-----------|
| Video I/O & frame extraction | `opencv-python` |
| Object detection | `ultralytics` (YOLOv8) |
| Numerical processing | `numpy`, `pandas` |
| Backend API | `FastAPI` or `Flask` |
| Frontend UI | `Streamlit` (prototype) → HTML/JS (final) |
| Visualization | `matplotlib`, `plotly` |
| Data storage | `JSON`, `CSV`, `SQLite` |
| Currency conversion | Static rate / `ExchangeRate-API` |

---

## 7. Design Decisions

| Decision | Rationale |
|----------|-----------|
| 2 fps sampling rate | Reduces compute while preserving temporal resolution for typical broadcast footage |
| YOLOv8 transfer learning | Faster training convergence; leverages pretrained COCO weights |
| Rule-based pricing model | Reproducible, explainable; extendable to ML-based pricing later |
| JSON/CSV output | Human-readable; easy to import into Excel or downstream tools |
| USD as base currency | Standard for international sponsorship benchmarks |

---

*See individual module documents in `docs/modules/` for implementation-level detail.*
