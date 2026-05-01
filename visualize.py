# all the drawing / annotation stuff goes here

import cv2
import numpy as np
from utils import get_color
import config


def draw_tracks(frame, tracks, tracker, show_trail=True, show_conf=False):
    # draw boxes, ids, and the motion trail lines on the frame
    for t in tracks:
        tid = t["id"]
        x1, y1, x2, y2 = t["bbox"]
        color = get_color(tid)

        # bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, config.BOX_THICKNESS)

        # label background
        label = f"ID {tid}"
        if show_conf:
            label += f" {t['conf']:.2f}"
        (tw, th), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE, config.FONT_THICKNESS
        )
        # filled rectangle behind text
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
        cv2.putText(
            frame, label, (x1 + 3, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE,
            (255, 255, 255), config.FONT_THICKNESS, cv2.LINE_AA,
        )

        # draw the trail behind each person
        if show_trail:
            trail = tracker.get_trail(tid)
            if len(trail) > 1:
                for i in range(1, len(trail)):
                    alpha = i / len(trail)  # older = thinner
                    thick = max(1, int(alpha * 3))
                    cv2.line(frame, trail[i - 1], trail[i], color, thick, cv2.LINE_AA)

    return frame


def draw_frame_info(frame, frame_idx, total_frames, active_count, unique_count, fps=None):
    # info bar at the top of the frame
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 42), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    info = f"Frame {frame_idx}/{total_frames}  |  Active: {active_count}  |  Total IDs: {unique_count}"
    if fps is not None:
        info += f"  |  FPS: {fps:.1f}"

    cv2.putText(
        frame, info, (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA,
    )
    return frame


def save_screenshot(frame, path):
    cv2.imwrite(path, frame)
