# Module 03 — Logo Detection (YOLOv8)

> **Document type:** Module Reference  
> **Module path:** `src/detection/logo_detector.py`  
> **Model path:** `models/yolov8/best.pt`  
> **Last updated:** February 2026  
> **Depends on:** [Module 02 — Frame Extraction](02_frame_extraction.md)  
> **Feeds into:** [Module 04 — Exposure Analytics Engine](04_exposure_analytics.md)

---

## 1. Purpose

This module runs the **YOLOv8 object detection model** on each extracted frame to identify predefined brand logo classes. It outputs bounding box coordinates, confidence scores, class labels, and timestamps for every detection — forming the raw data input to the analytics engine.

---

## 2. Position in Pipeline

```
[Frame Extraction] → ▶ LOGO DETECTION ◀ → [Exposure Analytics Engine]
```

---

## 3. Model Overview

### YOLOv8 (You Only Look Once v8)
- Developed by **Ultralytics**
- Single-stage real-time object detector
- Model variants: `yolov8n` (nano), `yolov8s` (small), `yolov8m` (medium)
- **Selected for this project:** `yolov8s` (balance of speed and accuracy)
- Pretrained on COCO dataset; fine-tuned on custom logo dataset

### Transfer Learning Approach
1. Start with pretrained `yolov8s.pt` (COCO weights)
2. Replace the detection head output layer to match the number of logo classes
3. Train on the custom logo dataset for 100 epochs
4. Retain best weights by mAP@0.5 on validation set

---

## 4. Training Configuration

```yaml
# data.yaml (example)
path: data/dataset
train: images/train
val: images/val
test: images/test

nc: 8   # number of logo classes
names:
  0: NikeLogo
  1: AdidasLogo
  2: PumaLogo
  3: RedBullLogo
  4: CocaColaLogo
  5: PepsiLogo
  6: SamsungLogo
  7: SonyLogo
```

### Hyperparameters
| Parameter | Value |
|-----------|-------|
| Epochs | 100 (early stopping: patience=20) |
| Image size | 640 × 640 |
| Batch size | 16 |
| Optimizer | SGD (default) |
| Learning rate | 0.01 |
| Mosaic augmentation | Enabled |
| Flip augmentation | Horizontal |
| HSV jitter | Enabled |
| Confidence threshold | 0.25 (post-training) |
| IoU threshold (NMS) | 0.45 |

### Training Command
```bash
yolo detect train \
  model=yolov8s.pt \
  data=data/dataset/data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  project=runs/detect \
  name=logo_train \
  patience=20
```

---

## 5. Detection Output Schema

Each detection from a frame produces a record:

```json
{
  "frame_id": 42,
  "timestamp_sec": 21.0,
  "logo_class": "NikeLogo",
  "class_id": 0,
  "confidence": 0.91,
  "bbox": {
    "x1": 120,
    "y1": 80,
    "x2": 240,
    "y2": 160
  },
  "bbox_width": 120,
  "bbox_height": 80,
  "bbox_area_px": 9600,
  "frame_area_px": 921600,
  "bbox_area_ratio": 0.01042
}
```

`bbox_area_ratio = bbox_area_px / frame_area_px`

---

## 6. Input / Output Contract

### Input
| Item | Type | Description |
|------|------|-------------|
| `frames_metadata_path` | `str` | Path to `frames_metadata.csv` |
| `model_path` | `str` | Path to `models/yolov8/best.pt` |
| `confidence_threshold` | `float` | Min confidence to record (default: 0.25) |
| `frame_width` | `int` | Frame width in pixels (default: 1280) |
| `frame_height` | `int` | Frame height in pixels (default: 720) |

### Output
| Item | Type | Description |
|------|------|-------------|
| `detections.json` | JSON array | All detection records |
| `detections.csv` | CSV | Flat table of detection records |
| `total_detections` | `int` | Total number of detection events |

---

## 7. Pseudocode

```python
from ultralytics import YOLO
import pandas as pd
import json

def run_detection(frames_metadata_path, model_path, confidence_threshold=0.25):
    model = YOLO(model_path)
    metadata = pd.read_csv(frames_metadata_path)
    
    frame_width = 1280
    frame_height = 720
    frame_area = frame_width * frame_height
    
    detections = []
    
    for _, row in metadata.iterrows():
        results = model.predict(source=row["file_path"],
                                conf=confidence_threshold,
                                verbose=False)
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                bbox_area = (x2 - x1) * (y2 - y1)
                
                detections.append({
                    "frame_id": int(row["frame_id"]),
                    "timestamp_sec": float(row["timestamp_sec"]),
                    "logo_class": model.names[int(box.cls)],
                    "class_id": int(box.cls),
                    "confidence": round(float(box.conf), 4),
                    "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "bbox_area_px": bbox_area,
                    "frame_area_px": frame_area,
                    "bbox_area_ratio": round(bbox_area / frame_area, 6)
                })
    
    # Save outputs
    with open("data/outputs/detections.json", "w") as f:
        json.dump(detections, f, indent=2)
    
    pd.DataFrame(detections).to_csv("data/outputs/detections.csv", index=False)
    
    return detections
```

---

## 8. Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| mAP@0.5 | Mean Average Precision at IoU 0.5 | ≥ 0.75 |
| mAP@0.5:0.95 | Stricter localization accuracy | ≥ 0.50 |
| Precision | TP / (TP + FP) | ≥ 0.70 |
| Recall | TP / (TP + FN) | ≥ 0.65 |
| F1-Score | Harmonic mean of P and R | ≥ 0.67 |
| Inference time | Time per frame | < 100 ms (GPU) |

---

## 9. Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL_PATH` | `models/yolov8/best.pt` | Fine-tuned model weights |
| `CONFIDENCE_THRESHOLD` | `0.25` | Min detection confidence |
| `IOU_THRESHOLD` | `0.45` | NMS IoU threshold |
| `DETECTION_OUTPUT_DIR` | `data/outputs/` | Where to save JSON/CSV |

---

## 10. File Outputs

```
data/
└── outputs/
    ├── detections.json     ← full detection records
    └── detections.csv      ← flat CSV version

models/
└── yolov8/
    ├── best.pt             ← final trained weights
    └── last.pt             ← last epoch weights

runs/
└── detect/
    └── logo_train/
        ├── results.csv
        ├── confusion_matrix.png
        ├── PR_curve.png
        └── weights/
            └── best.pt
```

---

## 11. Dependencies

```
ultralytics
opencv-python
torch
torchvision
pandas
numpy
```

---

## 12. Known Limitations

- Model accuracy degrades on **small logos** (< 32×32 px in source video)
- **Partial occlusion** may reduce confidence below threshold
- logos with similar visual structure may cause false positives (e.g., Nike swoosh vs. Puma leaping cat at low resolution)
- Currently supports **static logos only** (no animated logo handling)

---

## 13. Next Steps

- [ ] Collect and annotate training dataset (Phase 1)
- [ ] Train and evaluate model (Phase 3)
- [ ] Tune confidence threshold on validation set
- [ ] Add batch inference support for faster processing

---

*Previous: [02_frame_extraction.md](02_frame_extraction.md) | Next: [04_exposure_analytics.md](04_exposure_analytics.md)*
