"""
@file detection.py
@description Run YOLOv8 over a frame and return typed player + ball detections.

@status None
@issues None
@todo Fine-tune on football images if the COCO "sports ball" class is weak.
"""

from dataclasses import dataclass

import numpy as np

from . import config


@dataclass
class Detection:
    """A single detection with a pixel box, confidence, and class id."""
    box: np.ndarray          # [x1, y1, x2, y2] in pixels
    confidence: float
    class_id: int

    @property
    def is_person(self) -> bool:
        return self.class_id == config.PERSON_CLASS_ID

    @property
    def is_ball(self) -> bool:
        return self.class_id == config.SPORTS_BALL_CLASS_ID


class Detector:
    """Wraps a YOLO model and returns only person + ball detections."""

    def __init__(self, model_name: str = config.DEFAULT_MODEL,
                 confidence: float = config.DEFAULT_CONFIDENCE):
        from ultralytics import YOLO  # lazy import keeps non-CV tooling fast
        self._model = YOLO(model_name)
        self._confidence = confidence

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Run detection on one BGR frame, filtered to person + ball classes."""
        results = self._model.predict(frame, conf=self._confidence, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id in (config.PERSON_CLASS_ID, config.SPORTS_BALL_CLASS_ID):
                    detections.append(Detection(
                        box=box.xyxy[0].cpu().numpy(),
                        confidence=float(box.conf[0]),
                        class_id=class_id,
                    ))
        return detections
