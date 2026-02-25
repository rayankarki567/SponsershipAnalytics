# Module 04 — Exposure Analytics Engine

> **Document type:** Module Reference  
> **Module path:** `src/analytics/exposure_analytics.py`  
> **Last updated:** February 2026  
> **Depends on:** [Module 03 — Logo Detection](03_logo_detection.md)  
> **Feeds into:** [Module 05 — Sponsor Pricing Model](05_sponsor_pricing.md)

---

## 1. Purpose

The Exposure Analytics Engine **transforms raw frame-level detection records into interpretable sponsorship exposure metrics**. It answers the key business questions:
- How often did each brand appear?
- For how long was each brand visible?
- How prominently was each brand displayed?
- Were exposures sustained or fragmented?

---

## 2. Position in Pipeline

```
[Logo Detection] → ▶ EXPOSURE ANALYTICS ENGINE ◀ → [Sponsor Pricing Model]
```

---

## 3. Computed Metrics

### 3.1 Frequency (Total Detections)
- Count of all frame-level detections per logo class
- Measures **how often** the logo appeared in sampled frames

```
frequency = COUNT(detection records for logo_class X)
```

### 3.2 Total Exposure Duration
- Computed using temporal continuity of detection timestamps
- **Not simply** `frequency × (1 / sample_fps)` — gaps between detections are considered
- A **gap tolerance** (`GAP_TOLERANCE_SEC`, default: 1.0 s) determines whether consecutive detections belong to the same exposure segment

```
For each consecutive pair of detections (t_i, t_{i+1}):
  if (t_{i+1} - t_i) <= GAP_TOLERANCE:
      they belong to the same segment
  else:
      new segment starts at t_{i+1}

duration = SUM of all segment durations
```

### 3.3 Average Screen Coverage Ratio
- Average of `bbox_area_ratio` across all detection records for a logo class
- Expressed as a **percentage** of the total frame area
- Reflects **visual prominence** of the brand on screen

```
avg_coverage = MEAN(bbox_area_ratio) × 100  [in %]
```

### 3.4 Continuous Exposure Segments
- List of distinct time intervals during which the logo was continuously visible
- Each segment has: `start_sec`, `end_sec`, `duration_sec`
- Useful for identifying prime-time vs. brief appearances

---

## 4. Temporal Continuity Algorithm

```
Input: sorted list of timestamps T = [t0, t1, t2, ..., tn] for one logo class
Output: list of segments [(start, end, duration), ...]

segments = []
segment_start = T[0]
prev_t = T[0]

for t in T[1:]:
    if (t - prev_t) > GAP_TOLERANCE:
        segments.append((segment_start, prev_t, prev_t - segment_start))
        segment_start = t
    prev_t = t

# close final segment
segments.append((segment_start, prev_t, prev_t - segment_start))
```

**Gap Tolerance Rationale:**  
At 2 fps, two detections that are 0.5 s apart are adjacent frames. A 1-second gap tolerance allows for one missed frame between detections (e.g., brief occlusion) without breaking the segment.

---

## 5. Input / Output Contract

### Input
| Item | Type | Description |
|------|------|-------------|
| `detections_path` | `str` | Path to `detections.json` or `detections.csv` |
| `gap_tolerance_sec` | `float` | Max gap between detections in a segment (default: 1.0) |
| `sample_fps` | `float` | Sampling rate used during frame extraction (default: 2.0) |

### Output — Per Sponsor Record

```json
{
  "sponsor": "NikeLogo",
  "total_detections": 87,
  "total_exposure_sec": 43.5,
  "avg_screen_coverage_pct": 3.4,
  "avg_confidence": 0.88,
  "max_screen_coverage_pct": 7.2,
  "exposure_segments": [
    {"start_sec": 5.0,  "end_sec": 12.0, "duration_sec": 7.0},
    {"start_sec": 30.0, "end_sec": 46.5, "duration_sec": 16.5}
  ],
  "num_segments": 2,
  "longest_segment_sec": 16.5,
  "first_appearance_sec": 5.0,
  "last_appearance_sec": 46.5
}
```

### Output Files
- `data/outputs/exposure_report.json` — array of per-sponsor records
- `data/outputs/exposure_report.csv` — flat CSV for tabular display

---

## 6. Pseudocode

```python
import json
import pandas as pd

def compute_exposure_analytics(detections_path, gap_tolerance_sec=1.0):
    df = pd.read_csv(detections_path)
    
    results = []
    
    for logo_class, group in df.groupby("logo_class"):
        group = group.sort_values("timestamp_sec").reset_index(drop=True)
        timestamps = group["timestamp_sec"].tolist()
        
        # Compute segments
        segments = compute_segments(timestamps, gap_tolerance_sec)
        total_duration = sum(s["duration_sec"] for s in segments)
        
        results.append({
            "sponsor": logo_class,
            "total_detections": len(group),
            "total_exposure_sec": round(total_duration, 2),
            "avg_screen_coverage_pct": round(group["bbox_area_ratio"].mean() * 100, 3),
            "max_screen_coverage_pct": round(group["bbox_area_ratio"].max() * 100, 3),
            "avg_confidence": round(group["confidence"].mean(), 4),
            "exposure_segments": segments,
            "num_segments": len(segments),
            "longest_segment_sec": round(max(s["duration_sec"] for s in segments), 2),
            "first_appearance_sec": timestamps[0],
            "last_appearance_sec": timestamps[-1]
        })
    
    # Save
    with open("data/outputs/exposure_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    pd.json_normalize(results, "exposure_segments", 
                      meta=["sponsor", "total_detections", 
                            "total_exposure_sec", "avg_screen_coverage_pct"]
                     ).to_csv("data/outputs/exposure_report.csv", index=False)
    
    return results


def compute_segments(timestamps, gap_tolerance):
    if not timestamps:
        return []
    
    segments = []
    start = timestamps[0]
    prev = timestamps[0]
    
    for t in timestamps[1:]:
        if (t - prev) > gap_tolerance:
            segments.append({
                "start_sec": round(start, 2),
                "end_sec": round(prev, 2),
                "duration_sec": round(prev - start, 2)
            })
            start = t
        prev = t
    
    segments.append({
        "start_sec": round(start, 2),
        "end_sec": round(prev, 2),
        "duration_sec": round(prev - start, 2)
    })
    
    return segments
```

---

## 7. Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `GAP_TOLERANCE_SEC` | `1.0` | Max gap before a new exposure segment |
| `MIN_SEGMENT_DURATION_SEC` | `0.5` | Ignore segments shorter than this |
| `ANALYTICS_OUTPUT_DIR` | `data/outputs/` | Output location |

---

## 8. Edge Cases

| Scenario | Handling |
|----------|----------|
| Zero detections for a class | Class excluded from report |
| Single detection only | One segment of duration = 0.0 s |
| All detections in one continuous block | Single segment |
| Very short gap (< 1 frame interval) | Treated as same segment (within tolerance) |

---

## 9. Visualizations (Produced in Web Layer)

- **Bar chart:** Total exposure duration per sponsor (seconds)
- **Bar chart:** Average screen coverage per sponsor (%)
- **Timeline chart:** Exposure segments over video duration (Gantt-style)
- **Pie chart:** Proportion of total exposure per sponsor

---

## 10. File Outputs

```
data/
└── outputs/
    ├── detections.json         ← from Module 03
    ├── detections.csv          ← from Module 03
    ├── exposure_report.json    ← from this module
    └── exposure_report.csv     ← from this module
```

---

## 11. Dependencies

```
pandas
numpy
json (stdlib)
```

---

## 12. Next Steps

- [ ] Implement `compute_exposure_analytics()` function
- [ ] Unit test: known detections → verify segment boundaries
- [ ] Unit test: single detection, zero detections, all-continuous detections
- [ ] Add `min_segment_duration` filter to remove noise

---

*Previous: [03_logo_detection.md](03_logo_detection.md) | Next: [05_sponsor_pricing.md](05_sponsor_pricing.md)*
