# Development Plan — Video-Based Sponsorship Analytics System

> **Document type:** Project Roadmap  
> **Last updated:** February 2026  
> **Total estimated duration:** ~16 weeks

---

## Phase Overview

| Phase | Name | Duration | Status |
|-------|------|----------|--------|
| 0 | Project Setup & Environment | Week 1 | Not Started |
| 1 | Data Collection & Preparation | Week 2–3 | Not Started |
| 2 | Video Preprocessing & Frame Extraction | Week 3–4 | Not Started |
| 3 | YOLOv8 Model Training & Evaluation | Week 5–8 | Not Started |
| 4 | Exposure Analytics Engine | Week 9–10 | Not Started |
| 5 | Sponsor Pricing Model | Week 11–12 | Not Started |
| 6 | Web Interface Development | Week 12–14 | Not Started |
| 7 | Integration, Testing & Validation | Week 14–15 | Not Started |
| 8 | Documentation & Final Review | Week 16 | Not Started |

---

## Phase 0 — Project Setup & Environment (Week 1)

### Goals
- Initialize project repository and folder structure
- Set up Python virtual environment
- Install all required dependencies
- Establish documentation convention (these MD files)

### Tasks
- [ ] Create `e:\FYP` folder structure as per `docs/project_structure.md`
- [ ] Create and activate Python virtual environment
- [ ] Install: `ultralytics`, `opencv-python`, `numpy`, `pandas`, `matplotlib`, `plotly`, `fastapi` / `streamlit`, `pillow`, `requests`
- [ ] Create `requirements.txt`
- [ ] Create `.env.example` for configurable constants (exchange rate, thresholds)
- [ ] Confirm GPU availability for YOLOv8 training (CUDA check)

### Deliverables
- Functional project skeleton
- `requirements.txt`
- All documentation MD files (this set)

---

## Phase 1 — Data Collection & Preparation (Week 2–3)

### Goals
- Assemble a dataset of logos for training the YOLOv8 model
- Annotate training images with bounding boxes
- Split data into train / validation / test sets

### Tasks
- [ ] Select 5–10 target sponsor/brand logos (e.g., sports event footage brands)
- [ ] Collect minimum **200 images per class** from:
  - Web scraping (with license compliance)
  - Video frame extraction from publicly available footage
  - Synthetic augmentation (rotation, scale, brightness jitter)
- [ ] Use **Roboflow** or **LabelImg** for bounding box annotation
- [ ] Export dataset in **YOLOv8 format** (YAML + `images/` + `labels/`)
- [ ] Apply train/val/test split: **70% / 20% / 10%**
- [ ] Store dataset in `data/dataset/`

### Deliverables
- Annotated dataset YAML (`data/dataset/data.yaml`)
- `data/dataset/images/` and `data/dataset/labels/`
- Class distribution report

---

## Phase 2 — Video Preprocessing & Frame Extraction (Week 3–4)

### Goals
- Implement `src/preprocessing/` module
- Implement `src/frame_extraction/` module
- Validate output frames and metadata

### Tasks
- [ ] Implement `preprocess_video()`:
  - Normalize to 1280×720 (720p) if needed
  - Standardize to 30 fps
  - Convert to `.mp4` (H.264) if unsupported format
  - Detect and skip corrupted frames
- [ ] Implement `extract_frames()`:
  - OpenCV `VideoCapture` loop
  - Sample every N-th frame based on target fps (default: 2 fps)
  - Save frames as `frame_{index:05d}.jpg`
  - Generate `frames_metadata.csv` (frame_id, timestamp_sec, file_path)
- [ ] Write unit tests for both modules
- [ ] Benchmark extraction time on sample videos

### Deliverables
- `src/preprocessing/video_preprocessor.py`
- `src/frame_extraction/frame_extractor.py`
- `data/frames/frames_metadata.csv`
- Unit test results

---

## Phase 3 — YOLOv8 Model Training & Evaluation (Week 5–8)

### Goals
- Fine-tune YOLOv8 on the logo dataset using transfer learning
- Evaluate model performance and tune hyperparameters
- Export final model weights

### Tasks
- [ ] Load YOLOv8n or YOLOv8s pretrained weights (COCO)
- [ ] Configure training:
  - Epochs: 100 (early stopping enabled)
  - Image size: 640×640
  - Batch size: 16 (adjust for GPU VRAM)
  - Augmentation: mosaic, flips, HSV jitter
- [ ] Train using `ultralytics` CLI or Python API
- [ ] Evaluate on validation set:
  - mAP@0.5, mAP@0.5:0.95
  - Precision, Recall, F1 per class
- [ ] Review confusion matrix and failure cases
- [ ] Retrain / adjust dataset if mAP@0.5 < 0.75
- [ ] Export best weights to `models/yolov8/best.pt`
- [ ] Implement `src/detection/logo_detector.py`

### Deliverables
- Trained model: `models/yolov8/best.pt`
- Training metrics report (`runs/detect/train/`)
- `src/detection/logo_detector.py`
- Detection output schema (JSON per frame)

### Performance Target
| Metric | Minimum Acceptable |
|--------|--------------------|
| mAP@0.5 | ≥ 0.75 |
| Precision | ≥ 0.70 |
| Recall | ≥ 0.65 |
| Inference time/frame | < 100 ms on GPU |

---

## Phase 4 — Exposure Analytics Engine (Week 9–10)

### Goals
- Aggregate per-frame detection records into sponsor-level metrics
- Compute all required exposure KPIs

### Tasks
- [ ] Implement `src/analytics/exposure_analytics.py`:
  - Load detection records from CSV/JSON
  - Group by `logo_class`
  - Compute total detections (frequency)
  - Compute total exposure duration using timestamp gaps
  - Compute average `bbox_area_ratio` (screen coverage %)
  - Identify continuous exposure segments (gap tolerance: 1 second)
- [ ] Generate `outputs/exposure_report.json` per video
- [ ] Generate `outputs/exposure_report.csv` for tabular display
- [ ] Write unit tests with mock detection data
- [ ] Handle edge cases: zero detections, single-frame detections

### Deliverables
- `src/analytics/exposure_analytics.py`
- Sample `outputs/exposure_report.json`
- Unit tests

---

## Phase 5 — Sponsor Pricing Model (Week 11–12)

### Goals
- Implement a weighted scoring model converting exposure metrics to a USD estimate
- Add USD ↔ NPR conversion functionality

### Tasks
- [ ] Design scoring formula:
  ```
  score = w1 * normalized_duration
        + w2 * normalized_coverage
        + w3 * avg_confidence
        + w4 * normalized_frequency
  ```
  Default weights: `w1=0.40, w2=0.30, w3=0.15, w4=0.15`
- [ ] Map score (0–100) to USD estimate using a calibrated linear scale
  (e.g., score 100 → $5,000 for a 90-minute broadcast)
- [ ] Implement NPR conversion:
  - Static fallback rate: 1 USD = 135.00 NPR
  - Optional: fetch live rate from ExchangeRate-API
- [ ] Expose weights and base rate as configurable in `.env`
- [ ] Implement `src/pricing/pricing_model.py`
- [ ] Write unit tests for score and conversion functions

### Deliverables
- `src/pricing/pricing_model.py`
- `outputs/pricing_report.json`
- Configurable weight parameters

---

## Phase 6 — Web Interface Development (Week 12–14)

### Goals
- Build a prototype web interface for end-to-end user interaction
- Display results as charts, tables, and downloadable reports

### Tasks
#### Option A: Streamlit (faster prototype)
- [ ] Build `src/web/app.py` using Streamlit
- [ ] File upload widget (drag-and-drop video)
- [ ] Progress bar during processing
- [ ] Results page: bar chart (exposure per brand), timeline chart
- [ ] Tabular summary (sortable)
- [ ] USD/NPR toggle switch
- [ ] Download button (CSV report)

#### Option B: FastAPI + HTML frontend (if time permits)
- [ ] REST endpoints: `POST /upload`, `GET /results/{job_id}`
- [ ] HTML/CSS/JS frontend

### Deliverables
- Functional prototype web app
- USD/NPR toggle working
- Downloadable CSV output

---

## Phase 7 — Integration, Testing & Validation (Week 14–15)

### Goals
- Test the full pipeline end-to-end with real video samples
- Fix bugs and validate accuracy of metrics

### Tasks
- [ ] Run 5+ test videos through full pipeline
- [ ] Manually verify detection accuracy on sampled frames
- [ ] Validate exposure duration calculations
- [ ] Validate pricing scores are reasonable
- [ ] Performance benchmark: time per 10-minute video
- [ ] Fix all critical bugs
- [ ] Run all unit tests (`pytest`); aim for ≥ 80% coverage

### Deliverables
- Integration test report
- Bug fix log
- Pytest coverage report

---

## Phase 8 — Documentation & Final Review (Week 16)

### Goals
- Finalize all documentation
- Prepare project report and demo

### Tasks
- [ ] Update all `docs/` MD files with final implementation details
- [ ] Record a demo walkthrough video
- [ ] Write project report (following FYP guidelines)
- [ ] Clean up code (comments, type hints, docstrings)
- [ ] Final commit and tag release `v1.0`

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Insufficient training data | Medium | High | Augmentation + web scraping |
| Low mAP on logo detection | Medium | High | Retrain with more images; try YOLOv8m |
| GPU not available | Low | Medium | Use Google Colab for training |
| Video upload too slow in UI | Low | Low | Process asynchronously |
| Currency API downtime | Low | Low | Use static fallback rate |

---

*This plan is a living document — update task statuses and notes as work progresses.*
