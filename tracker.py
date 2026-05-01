# tracker - wraps yolov8's built-in tracking (bytetrack)
# stores history of each person's positions for trails + analytics

from ultralytics import YOLO
from collections import defaultdict
import config


class MultiObjectTracker:

    def __init__(self, weights=None):
        self.weights = weights or config.MODEL_WEIGHTS
        self.model = YOLO(self.weights)
        # track_id -> list of per-frame records
        self.history = defaultdict(list)
        self._fidx = 0
        print(f"[*] Tracker ready  ->  {self.weights}  ({config.TRACKER_CONFIG})")

    def update(self, frame):
        # feed next frame, get back list of active tracks
        results = self.model.track(
            frame,
            persist=True,
            conf=config.CONF_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            classes=config.TARGET_CLASSES,
            tracker=config.TRACKER_CONFIG,
            verbose=False,
        )

        active = []
        r = results[0]

        if r.boxes is not None and r.boxes.id is not None:
            boxes = r.boxes.xyxy.cpu().numpy()
            ids = r.boxes.id.int().cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()

            for bbox, tid, conf in zip(boxes, ids, confs):
                x1, y1, x2, y2 = bbox
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                self.history[int(tid)].append({
                    "frame": self._fidx,
                    "center": (cx, cy),
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                })

                active.append({
                    "id": int(tid),
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                    "conf": float(conf),
                    "center": (cx, cy),
                })

        self._fidx += 1
        return active

    def get_trail(self, track_id, length=None):
        length = length or config.TRAIL_LENGTH
        pts = self.history.get(track_id, [])
        centers = [(int(p["center"][0]), int(p["center"][1])) for p in pts]
        return centers[-length:]

    def get_all_history(self):
        return dict(self.history)

    def unique_count(self):
        return len(self.history)

    def reset(self):
        self.history.clear()
        self._fidx = 0
        self.model = YOLO(self.weights)
