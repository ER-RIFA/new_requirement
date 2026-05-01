"""
Config file - all tunable params in one place.
Adjust these based on your video resolution and hardware.
"""

import os

# --- paths ---
OUTPUT_DIR = "output"
SCREENSHOTS_DIR = "screenshots"

# --- detection model ---
MODEL_WEIGHTS = "yolov8m.pt"   # medium model; swap to yolov8n.pt for speed
CONF_THRESHOLD = 0.3
IOU_THRESHOLD = 0.45
TARGET_CLASSES = [0]           # COCO class 0 = person

# --- tracker ---
TRACKER_CONFIG = "bytetrack.yaml"   # alt: botsort.yaml
TRACK_BUFFER = 30                   # frames to keep lost tracks alive

# --- visualization ---
TRAIL_LENGTH = 40
BOX_THICKNESS = 2
FONT_SCALE = 0.55
FONT_THICKNESS = 2

# --- analytics ---
HEATMAP_BLUR = 25
TRAJ_LINE_THICKNESS = 2

# make sure output folders exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
