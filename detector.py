# yolov8 detection wrapper
# not directly used in main pipeline anymore (tracker handles it)
# but keeping it for standalone testing

from ultralytics import YOLO
import numpy as np
import config


class ObjectDetector:

    def __init__(self, weights=None):
        self.weights = weights or config.MODEL_WEIGHTS
        self.model = YOLO(self.weights)
        print(f"[*] Detector ready  ->  {self.weights}")

    def detect(self, frame):
        results = self.model.predict(
            frame,
            conf=config.CONF_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            classes=config.TARGET_CLASSES,
            verbose=False,
        )

        detections = []
        for r in results:
            if r.boxes is None or len(r.boxes) == 0:
                continue
            boxes = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy().astype(int)

            for bbox, conf, cls in zip(boxes, confs, classes):
                detections.append({
                    "bbox": tuple(bbox.astype(int)),
                    "conf": float(conf),
                    "cls": cls,
                })
        return detections

    def warmup(self):
        # run a blank image through to warm up cuda
        blank = np.zeros((640, 640, 3), dtype=np.uint8)
        self.model.predict(blank, verbose=False)
        print("[*] Warmup complete")
