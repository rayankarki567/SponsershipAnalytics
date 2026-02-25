# Module 02 — Frame Extraction

> **Document type:** Module Reference  
> **Module path:** `src/frame_extraction/frame_extractor.py`  
> **Last updated:** February 2026  
> **Depends on:** [Module 01 — Video Preprocessing](01_video_preprocessing.md)  
> **Feeds into:** [Module 03 — Logo Detection](03_logo_detection.md)

---

## 1. Purpose

The frame extraction module **decomposes the preprocessed video into individual image frames** at a defined sampling rate. This reduces the number of images passed to the detection model (and thus computation time) while retaining enough temporal resolution to accurately measure sponsorship exposure duration.

---

## 2. Position in Pipeline

```
[Video Preprocessing] → ▶ FRAME EXTRACTION ◀ → [Logo Detection]
```

---

## 3. Sampling Strategy

### Why Not Extract Every Frame?
- A 30 fps, 90-minute match contains **162,000 frames**
- Running YOLOv8 on every frame at ~30 ms/frame = ~81 minutes of inference
- Most logo exposures last several seconds — 2 fps provides sufficient temporal resolution

### Sampling Rate
- **Default:** 2 frames per second
- Configurable via `SAMPLE_FPS` in `.env`
- Frame selection: every `N = int(video_fps / sample_fps)` frames

### Temporal Accuracy
At 2 fps, the minimum measurable exposure unit is **0.5 seconds**. The expected minimum logo exposure in broadcast footage is typically ≥ 1 second, so 2 fps is acceptable.

---

## 4. Frame Indexing & Timestamping

Each extracted frame is:
1. **Saved** to disk as `frame_{index:05d}.jpg` (e.g., `frame_00042.jpg`)
2. **Indexed** with an integer `frame_id` (sequential, starting at 0)
3. **Timestamped** with `timestamp_sec = frame_number_in_video / video_fps`

### Metadata CSV Schema

`data/frames/frames_metadata.csv`:

```csv
frame_id,timestamp_sec,file_path,video_frame_number
0,0.0,data/frames/frame_00000.jpg,0
1,0.5,data/frames/frame_00001.jpg,15
2,1.0,data/frames/frame_00002.jpg,30
...
```

---

## 5. Input / Output Contract

### Input
| Item | Type | Description |
|------|------|-------------|
| `video_path` | `str` | Path to preprocessed `.mp4` |
| `output_dir` | `str` | Directory to save frame images |
| `sample_fps` | `float` | Frames to extract per second (default: 2) |

### Output
| Item | Type | Description |
|------|------|-------------|
| Frame images | `JPEG` files | Stored in `data/frames/` |
| `frames_metadata.csv` | `CSV` file | frame_id, timestamp_sec, file_path |
| `total_frames_extracted` | `int` | Count of successfully extracted frames |

---

## 6. Pseudocode

```python
def extract_frames(video_path, output_dir, sample_fps=2.0):
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    sample_interval = int(video_fps / sample_fps)  # e.g., 30 / 2 = every 15th frame
    
    records = []
    frame_id = 0
    video_frame_number = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if video_frame_number % sample_interval == 0:
            timestamp_sec = video_frame_number / video_fps
            file_name = f"frame_{frame_id:05d}.jpg"
            file_path = os.path.join(output_dir, file_name)
            
            cv2.imwrite(file_path, frame)
            
            records.append({
                "frame_id": frame_id,
                "timestamp_sec": round(timestamp_sec, 3),
                "file_path": file_path,
                "video_frame_number": video_frame_number
            })
            frame_id += 1
        
        video_frame_number += 1
    
    cap.release()
    
    # Save metadata CSV
    df = pd.DataFrame(records)
    metadata_path = os.path.join(output_dir, "frames_metadata.csv")
    df.to_csv(metadata_path, index=False)
    
    return metadata_path, frame_id
```

---

## 7. Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SAMPLE_FPS` | `2.0` | Sampling rate in frames per second |
| `FRAME_FORMAT` | `jpg` | Image format (`jpg` or `png`) |
| `FRAME_QUALITY` | `95` | JPEG quality (1–100) |
| `FRAMES_OUTPUT_DIR` | `data/frames/` | Output directory for frame images |

---

## 8. Storage Estimate

| Video Length | Frames at 2fps | Avg JPEG size | Total Storage |
|-------------|----------------|---------------|---------------|
| 5 minutes | 600 | ~150 KB | ~90 MB |
| 30 minutes | 3,600 | ~150 KB | ~540 MB |
| 90 minutes | 10,800 | ~150 KB | ~1.6 GB |

> Consider enabling automatic frame cleanup after detection is complete.

---

## 9. Error Handling

| Error | Action |
|-------|--------|
| Video can't be opened | Raise exception, return error |
| Zero frames extracted | Abort pipeline, log error |
| Disk write failure | Raise `IOError` with directory path |

---

## 10. File Outputs

```
data/
└── frames/
    ├── frame_00000.jpg
    ├── frame_00001.jpg
    ├── ...
    └── frames_metadata.csv
```

---

## 11. Dependencies

```
opencv-python
pandas
numpy
```

---

## 12. Next Steps (After Implementation)

- [ ] Unit test: verify timestamp accuracy ±0.1s
- [ ] Unit test: verify correct number of frames extracted from a known video
- [ ] Add optional cleanup function to delete frames after detection

---

*Previous: [01_video_preprocessing.md](01_video_preprocessing.md) | Next: [03_logo_detection.md](03_logo_detection.md)*
