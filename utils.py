"""
Small helper functions used across the project.
"""

import cv2
import numpy as np


def generate_colors(n=50):
    """Build a palette of visually distinct colors via HSV rotation."""
    palette = []
    for i in range(n):
        hue = int(i * 180 / n)
        bgr = cv2.cvtColor(
            np.uint8([[[hue, 220, 230]]]), cv2.COLOR_HSV2BGR
        )[0][0]
        palette.append(tuple(int(c) for c in bgr))
    return palette


# pre-generate once
_COLORS = generate_colors(50)


def get_color(track_id):
    """Return a consistent color for the given track ID."""
    return _COLORS[int(track_id) % len(_COLORS)]


def get_video_info(path):
    """Read basic props from a video file."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {path}")

    info = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }
    info["duration_sec"] = info["total_frames"] / max(info["fps"], 1)
    cap.release()
    return info


def resize_frame(frame, max_dim=1280):
    """Scale down if either dimension exceeds max_dim."""
    h, w = frame.shape[:2]
    if max(h, w) <= max_dim:
        return frame, 1.0
    scale = max_dim / max(h, w)
    resized = cv2.resize(frame, (int(w * scale), int(h * scale)))
    return resized, scale
