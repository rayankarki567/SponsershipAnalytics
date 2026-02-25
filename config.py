"""
config.py — Central configuration loader for the Sponsorship Analytics System.
All modules import constants from here rather than reading .env individually.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── YOLOv8 Detection ──────────────────────────────────────────────────────────
MODEL_PATH             = os.getenv("MODEL_PATH", "models/yolov8/best.pt")
CONFIDENCE_THRESHOLD   = float(os.getenv("CONFIDENCE_THRESHOLD", 0.25))
IOU_THRESHOLD          = float(os.getenv("IOU_THRESHOLD", 0.45))

# ── Video Preprocessing ───────────────────────────────────────────────────────
TARGET_WIDTH           = int(os.getenv("TARGET_WIDTH", 1280))
TARGET_HEIGHT          = int(os.getenv("TARGET_HEIGHT", 720))
TARGET_FPS             = int(os.getenv("TARGET_FPS", 30))
TARGET_RESOLUTION      = (TARGET_WIDTH, TARGET_HEIGHT)
MAX_FILE_SIZE_MB       = int(os.getenv("MAX_FILE_SIZE_MB", 500))
VARIANCE_THRESHOLD     = int(os.getenv("VARIANCE_THRESHOLD", 10))

# ── Frame Extraction ──────────────────────────────────────────────────────────
SAMPLE_FPS             = float(os.getenv("SAMPLE_FPS", 2.0))
FRAMES_OUTPUT_DIR      = os.getenv("FRAMES_OUTPUT_DIR", "data/frames/")

# ── Exposure Analytics ────────────────────────────────────────────────────────
GAP_TOLERANCE_SEC         = float(os.getenv("GAP_TOLERANCE_SEC", 1.0))
MIN_SEGMENT_DURATION_SEC  = float(os.getenv("MIN_SEGMENT_DURATION_SEC", 0.5))

# ── Sponsor Pricing ───────────────────────────────────────────────────────────
WEIGHT_DURATION        = float(os.getenv("WEIGHT_DURATION", 0.40))
WEIGHT_COVERAGE        = float(os.getenv("WEIGHT_COVERAGE", 0.30))
WEIGHT_CONFIDENCE      = float(os.getenv("WEIGHT_CONFIDENCE", 0.15))
WEIGHT_FREQUENCY       = float(os.getenv("WEIGHT_FREQUENCY", 0.15))

BASE_VALUE_USD         = float(os.getenv("BASE_VALUE_USD", 5000))
MAX_DURATION_SEC       = float(os.getenv("MAX_DURATION_SEC", 300))
MAX_COVERAGE_PCT       = float(os.getenv("MAX_COVERAGE_PCT", 10.0))
MAX_FREQUENCY          = float(os.getenv("MAX_FREQUENCY", 600))

# ── Currency Conversion ───────────────────────────────────────────────────────
STATIC_NPR_RATE        = float(os.getenv("STATIC_NPR_RATE", 135.00))
EXCHANGE_RATE_API_KEY  = os.getenv("EXCHANGE_RATE_API_KEY", "")

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_VIDEO_DIR          = "data/raw/"
PROCESSED_VIDEO_DIR    = "data/processed/"
FRAMES_DIR             = "data/frames/"
OUTPUTS_DIR            = "data/outputs/"
DATASET_DIR            = "data/dataset/"

# Validate weights sum to 1.0
_weight_sum = WEIGHT_DURATION + WEIGHT_COVERAGE + WEIGHT_CONFIDENCE + WEIGHT_FREQUENCY
assert abs(_weight_sum - 1.0) < 1e-6, (
    f"Pricing weights must sum to 1.0, currently sum to {_weight_sum:.4f}"
)
