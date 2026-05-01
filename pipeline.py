# main pipeline - reads video, runs tracker, writes output
# also handles screenshots and analytics if enabled

import cv2
import time
import os
import config
from tracker import MultiObjectTracker
from visualize import draw_tracks, draw_frame_info, save_screenshot
from analytics import run_all_analytics
from utils import get_video_info


class Pipeline:

    def __init__(self, video_path, output_path=None):
        self.video_path = video_path
        self.output_path = output_path or os.path.join(
            config.OUTPUT_DIR, "tracked_output.mp4"
        )
        self.tracker = MultiObjectTracker()
        self.frame_counts = []     # active count per frame

    def run(self, show_preview=False, save_screenshots=True, run_analytics=True):
        vinfo = get_video_info(self.video_path)
        fps = vinfo["fps"]
        total = vinfo["total_frames"]
        w, h = vinfo["width"], vinfo["height"]

        print(f"\n{'='*55}")
        print(f"  Input  : {self.video_path}")
        print(f"  Size   : {w}x{h} @ {fps:.1f} FPS")
        print(f"  Frames : {total}  ({vinfo['duration_sec']:.1f}s)")
        print(f"  Output : {self.output_path}")
        print(f"{'='*55}\n")

        cap = cv2.VideoCapture(self.video_path)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(self.output_path, fourcc, fps, (w, h))

        frame_idx = 0
        t_start = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            tracks = self.tracker.update(frame)
            self.frame_counts.append(len(tracks))

            draw_tracks(frame, tracks, self.tracker, show_trail=True)
            draw_frame_info(
                frame, frame_idx, total, len(tracks),
                self.tracker.unique_count(), fps=None,
            )

            writer.write(frame)

            # save a few sample screenshots
            if save_screenshots and frame_idx in self._screenshot_frames(total):
                spath = os.path.join(config.SCREENSHOTS_DIR, f"frame_{frame_idx:05d}.png")
                save_screenshot(frame, spath)

            if show_preview:
                preview = cv2.resize(frame, (min(w, 1280), min(h, 720)))
                cv2.imshow("Tracking Preview", preview)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("[!] Preview closed by user")
                    break

            frame_idx += 1
            if frame_idx % 100 == 0:
                elapsed = time.time() - t_start
                proc_fps = frame_idx / max(elapsed, 0.001)
                pct = frame_idx / max(total, 1) * 100
                print(f"  [{pct:5.1f}%]  frame {frame_idx}/{total}   ({proc_fps:.1f} fps)")

        cap.release()
        writer.release()
        if show_preview:
            cv2.destroyAllWindows()

        elapsed = time.time() - t_start
        print(f"\nDone! Processed {frame_idx} frames in {elapsed:.1f}s")
        print(f"  Output video  ->  {self.output_path}")
        print(f"  Unique IDs    ->  {self.tracker.unique_count()}")

        if run_analytics:
            history = self.tracker.get_all_history()
            run_all_analytics(history, (h, w), fps, self.frame_counts)

        return self.tracker.get_all_history()

    def _screenshot_frames(self, total):
        if total <= 0:
            return set()
        step = max(total // 6, 1)  # ~5 screenshots spread out
        return {step, step * 2, step * 3, step * 4, step * 5}
