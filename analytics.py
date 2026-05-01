# analytics stuff - trajectory plots, heatmaps, movement stats etc.
# runs after the main tracking is done

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend
import matplotlib.pyplot as plt
from collections import Counter
import os
import config
from utils import get_color


def plot_trajectories(history, frame_shape, save_path=None):
    # draw all the tracked paths on a black background
    h, w = frame_shape[:2]
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    for tid, records in history.items():
        color = get_color(tid)
        pts = [(int(r["center"][0]), int(r["center"][1])) for r in records]
        if len(pts) < 2:
            continue
        for i in range(1, len(pts)):
            cv2.line(canvas, pts[i - 1], pts[i], color, config.TRAJ_LINE_THICKNESS, cv2.LINE_AA)
        # mark start and end
        cv2.circle(canvas, pts[0], 5, (0, 255, 0), -1)
        cv2.circle(canvas, pts[-1], 5, (0, 0, 255), -1)
        # label
        mid = pts[len(pts) // 2]
        cv2.putText(canvas, str(tid), mid, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    if save_path is None:
        save_path = os.path.join(config.OUTPUT_DIR, "trajectories.png")
    cv2.imwrite(save_path, canvas)
    print(f"[+] Trajectory map saved  ->  {save_path}")
    return canvas


def generate_heatmap(history, frame_shape, save_path=None):
    # TODO: maybe try a different colormap, JET is kinda ugly
    h, w = frame_shape[:2]
    accum = np.zeros((h, w), dtype=np.float32)

    for tid, records in history.items():
        for r in records:
            cx, cy = int(r["center"][0]), int(r["center"][1])
            if 0 <= cx < w and 0 <= cy < h:
                accum[cy, cx] += 1.0

    # blur it so it doesnt look all pixelated
    ksize = config.HEATMAP_BLUR
    if ksize % 2 == 0:
        ksize += 1
    accum = cv2.GaussianBlur(accum, (ksize, ksize), 0)

    # normalize to 0-255
    if accum.max() > 0:
        accum = (accum / accum.max() * 255).astype(np.uint8)
    else:
        accum = accum.astype(np.uint8)

    heatmap = cv2.applyColorMap(accum, cv2.COLORMAP_JET)

    if save_path is None:
        save_path = os.path.join(config.OUTPUT_DIR, "heatmap.png")
    cv2.imwrite(save_path, heatmap)
    print(f"[+] Heatmap saved  ->  {save_path}")
    return heatmap


def plot_object_count(frame_counts, fps, save_path=None):
    # simple line chart showing how many people are visible over time
    if not frame_counts:
        return

    times = [i / max(fps, 1) for i in range(len(frame_counts))]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, frame_counts, linewidth=1.2, color="#2196F3")
    ax.fill_between(times, frame_counts, alpha=0.15, color="#2196F3")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Active subjects")
    ax.set_title("Detected Subject Count Over Time")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if save_path is None:
        save_path = os.path.join(config.OUTPUT_DIR, "object_count.png")
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"[+] Object count plot saved  ->  {save_path}")


def compute_movement_stats(history, fps):
    # calculate distance + speed for each tracked person
    # note: these are pixel values, not real-world meters
    stats = {}
    for tid, records in history.items():
        pts = [r["center"] for r in records]
        if len(pts) < 2:
            stats[tid] = {"distance_px": 0, "avg_speed_px_s": 0, "num_frames": len(pts)}
            continue

        total_dist = 0.0
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i - 1][0]
            dy = pts[i][1] - pts[i - 1][1]
            total_dist += np.sqrt(dx * dx + dy * dy)

        duration = len(pts) / max(fps, 1)
        avg_speed = total_dist / max(duration, 0.001)

        stats[tid] = {
            "distance_px": round(float(total_dist), 1),
            "avg_speed_px_s": round(float(avg_speed), 1),
            "num_frames": len(pts),
        }
    return stats


def save_stats_report(stats, save_path=None):
    if save_path is None:
        save_path = os.path.join(config.OUTPUT_DIR, "movement_stats.txt")

    lines = ["Track ID | Distance (px) | Avg Speed (px/s) | Frames Tracked"]
    lines.append("-" * 65)

    for tid in sorted(stats.keys()):
        s = stats[tid]
        lines.append(
            f"  {tid:>5}  |  {s['distance_px']:>10}  |  {s['avg_speed_px_s']:>13}  |  {s['num_frames']:>6}"
        )

    lines.append(f"\nTotal unique subjects tracked: {len(stats)}")

    with open(save_path, "w") as f:
        f.write("\n".join(lines))
    print(f"[+] Stats report saved  ->  {save_path}")


def run_all_analytics(history, frame_shape, fps, frame_counts):
    print("\n--- Running post-processing analytics ---")
    plot_trajectories(history, frame_shape)
    generate_heatmap(history, frame_shape)
    plot_object_count(frame_counts, fps)
    stats = compute_movement_stats(history, fps)
    save_stats_report(stats)
    print("--- Analytics complete ---\n")
    return stats
