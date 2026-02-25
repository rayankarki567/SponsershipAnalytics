# Expected Outcome — Video-Based Sponsorship Analytics System

> **Document type:** Goals & Success Criteria  
> **Last updated:** February 2026

---

## 1. Summary

This project aims to deliver a **functional, end-to-end video-based sponsorship analytics prototype** that automates the traditionally manual process of measuring brand logo exposure in video content. The system will be demonstrably useful for sports broadcasters, event organizers, and marketing analysts.

---

## 2. Functional Deliverables

### 2.1 Core System
| Deliverable | Description | Status |
|-------------|-------------|--------|
| Video preprocessing pipeline | Standardize any uploaded video to 720p/30fps/.mp4 | Not Started |
| Frame extraction pipeline | Extract ~2 fps frames with timestamps | Not Started |
| YOLOv8 logo detector | Trained model, ≥ 0.75 mAP@0.5 on test set | Not Started |
| Exposure analytics engine | Compute duration, frequency, coverage, segments | Not Started |
| Sponsor pricing model | Output USD and NPR estimates per brand | Not Started |
| Web interface prototype | Upload → Process → View results | Not Started |

### 2.2 User-Facing Features
- Upload video through a browser-based interface
- Visual progress indicator during processing
- Bar charts showing exposure duration per brand
- Timeline/Gantt chart showing when each brand appeared
- Tabular sponsor report (sortable)
- **USD/NPR currency toggle** for pricing estimates
- Downloadable CSV report

---

## 3. Performance Targets

### 3.1 Detection Accuracy
| Metric | Target |
|--------|--------|
| mAP@0.5 (validation set) | ≥ 0.75 |
| Precision | ≥ 0.70 |
| Recall | ≥ 0.65 |
| F1-Score | ≥ 0.67 |

### 3.2 System Performance
| Metric | Target |
|--------|--------|
| Processing time (10-min video) | < 5 minutes on GPU |
| Processing time (10-min video, CPU only) | < 30 minutes |
| Exposure duration measurement error | ± 1 second per segment |
| Max supported video duration | 3 hours |
| Max supported file size | 500 MB |

### 3.3 Analytics Accuracy
- Total exposure duration computation error: **< 2%** vs manual ground truth
- Screen coverage ratio is computed per-frame and averaged — no special accuracy target, but consistent with visual inspection

---

## 4. Output Report Example

For a 90-minute football match with 3 sponsors:

| Sponsor | Detections | Exposure (s) | Avg Coverage | Score | Est. USD | Est. NPR |
|---------|-----------|-------------|-------------|-------|----------|---------|
| NikeLogo | 320 | 160 s | 4.2% | 82.1 | $4,105 | NPR 554,175 |
| AdidasLogo | 180 | 90 s | 2.8% | 52.3 | $2,615 | NPR 353,025 |
| RedBullLogo | 60 | 30 s | 1.5% | 21.7 | $1,085 | NPR 146,475 |

---

## 5. Web Interface Outcome

The web interface will enable a non-technical user to:

1. Upload a video file (drag-and-drop or file browser)
2. Click **"Analyze"**
3. Wait for processing with a live progress bar
4. View an interactive dashboard with:
   - Per-brand exposure bar chart
   - Temporal timeline showing when brands appeared
   - Numeric summary table with all KPIs
   - Pricing estimates with **USD/NPR toggle**
5. Download the full report as CSV

---

## 6. Currency Conversion

- All sponsorship estimates default to **USD**
- A toggle/button switches all monetary values to **NPR** instantly
- Exchange rate source:
  - **Live rate** (if API key configured): fetched from ExchangeRate-API, cached 24 hours
  - **Static fallback**: 1 USD = 135.00 NPR (configurable in `.env`)
- The rate used is displayed alongside all NPR values for transparency

---

## 7. Feasibility Demonstration Goals

This project will demonstrate the following:

1. **Automated detection is viable** — YOLOv8 can reliably detect sponsor logos in broadcast-quality video with research-grade accuracy
2. **Exposure metrics are computable** — Duration, frequency, and coverage can be extracted automatically without human review
3. **Pricing estimation is feasible** — A rule-based model can produce reasonable, explainable sponsorship value estimates
4. **The system is accessible** — A non-technical user can operate it through a simple web interface

---

## 8. Future Extension Possibilities

| Extension | Description |
|-----------|-------------|
| Real-time video monitoring | Process live streams (e.g., RTMP) |
| Expanded logo dataset | Support hundreds of logos across industries |
| ML-based pricing model | Trained on real sponsorship deal data |
| Audience reach integration | Weight exposure by concurrent viewership (CPM) |
| Multi-language UI | Interface in Nepali, Spanish, etc. |
| Animated logo detection | Handle rotating/fading logo animations |
| PDF report generation | Professional branded PDF output |
| REST API | Integrate analytics into third-party platforms |

---

## 9. Academic / FYP Success Criteria

| Criterion | Measure |
|-----------|---------|
| System completeness | All 5 modules implemented and integrated |
| Detection performance | mAP@0.5 ≥ 0.75 on held-out test set |
| Functional demo | End-to-end test with a real video |
| Documentation | All `docs/` MD files complete and up-to-date |
| Code quality | ≥ 80% test coverage (pytest) |
| Report | Written project report submitted per FYP guidelines |

---

*Refer to [docs/plan.md](../plan.md) for the phased development roadmap.*
