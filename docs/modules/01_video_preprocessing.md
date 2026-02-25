# Module 01 — Video Preprocessing

> **Document type:** Module Reference  
> **Module path:** `src/preprocessing/video_preprocessor.py`  
> **Last updated:** February 2026  
> **Depends on:** None (first stage)  
> **Feeds into:** [Module 02 — Frame Extraction](02_frame_extraction.md)

---

## 1. Purpose

The preprocessing module **standardizes the input video** before it enters the detection pipeline. Raw user-uploaded videos may vary in resolution, frame rate, encoding, and quality. This module ensures that all downstream modules receive a **consistent, clean video stream**.

---

## 2. Position in Pipeline

```
[Video Upload] → [Input Validation] → ▶ VIDEO PREPROCESSING ◀ → [Frame Extraction]
```

---

## 3. Operations

### 3.1 Resolution Normalization
- **Target resolution:** 1280 × 720 (720p)
- If the input is higher (e.g., 4K), it is **downscaled** to 720p to reduce frame file size and speed up detection
- If input is lower than 360p, the video is **rejected** at the validation layer
- Scaling uses `cv2.resize()` with `INTER_AREA` interpolation for downscaling

### 3.2 Frame Rate Standardization
- **Target FPS:** 30
- Videos with non-standard FPS (e.g., 24, 60, 120) are re-encoded to 30 fps
- This ensures frame extraction downstream uses a predictable temporal grid
- Uses `ffmpeg` (via `subprocess`) or OpenCV writer

### 3.3 Format Conversion
- **Target format:** `.mp4` (H.264 codec)
- Supported input: `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`
- Conversion invoked via `ffmpeg` if codec is not H.264
- Output stored to `data/processed/`

### 3.4 Corrupted Frame Removal
- Frames where `ret == False` from `cv2.VideoCapture.read()` are skipped
- Frames with all-black or all-white pixel values (variance < threshold) are flagged and excluded
- A log of removed frame indices is written to `data/processed/corruption_log.txt`

---

## 4. Input / Output Contract

### Input
| Item | Type | Description |
|------|------|-------------|
| `video_path` | `str` | Absolute path to uploaded video |
| `output_dir` | `str` | Directory to save processed video |
| `target_resolution` | `tuple` | `(width, height)`, default `(1280, 720)` |
| `target_fps` | `int` | Default `30` |

### Output
| Item | Type | Description |
|------|------|-------------|
| `processed_video_path` | `str` | Path to standardized `.mp4` file |
| `metadata` | `dict` | `{original_fps, original_res, duration_sec, frames_removed}` |

---

## 5. Pseudocode

```python
def preprocess_video(video_path, output_dir, target_res=(1280, 720), target_fps=30):
    cap = cv2.VideoCapture(video_path)
    
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_path = os.path.join(output_dir, "processed_video.mp4")
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'),
                             target_fps, target_res)
    
    frames_removed = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip corrupted (black/white) frames
        if is_corrupted(frame):
            frames_removed += 1
            continue
        
        # Resize if needed
        if (original_width, original_height) != target_res:
            frame = cv2.resize(frame, target_res, interpolation=cv2.INTER_AREA)
        
        writer.write(frame)
    
    cap.release()
    writer.release()
    
    return output_path, {
        "original_fps": original_fps,
        "original_res": (original_width, original_height),
        "frames_removed": frames_removed
    }

def is_corrupted(frame, variance_threshold=10):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray.var() < variance_threshold
```

---

## 6. Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TARGET_RESOLUTION` | `(1280, 720)` | Output frame dimensions |
| `TARGET_FPS` | `30` | Output frame rate |
| `VARIANCE_THRESHOLD` | `10` | Below this → frame is corrupted |
| `MAX_FILE_SIZE_MB` | `500` | Reject files above this limit |

These are set in `.env` and loaded via `config.py`.

---

## 7. Error Handling

| Error | Action |
|-------|--------|
| File not found | Raise `FileNotFoundError`, return error to UI |
| Unsupported format | Attempt `ffmpeg` conversion; if fails, reject with message |
| All frames corrupted | Abort pipeline, return error report |
| Duration < 5 seconds | Reject at validation layer before this module |

---

## 8. File Outputs

```
data/
└── processed/
    ├── processed_video.mp4       ← standardized video
    └── corruption_log.txt        ← list of removed frame indices
```

---

## 9. Dependencies

```
opencv-python
ffmpeg (system binary, called via subprocess)
numpy
```

---

## 10. Next Steps (After Implementation)

- [ ] Write unit tests: test with corrupt frames, different resolutions, different FPS
- [ ] Benchmark preprocessing time for a 10-min 1080p video
- [ ] Add progress callback for the UI progress bar

---

*Next module: [02_frame_extraction.md](02_frame_extraction.md)*
