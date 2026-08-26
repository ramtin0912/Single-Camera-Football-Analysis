"""
@file detection.py
@description Run YOLOv8 over a frame and return typed player + ball detections.
  Tracking uses ultralytics' built-in ByteTrack rather than a hand-rolled
  tracker.

@status None
@issues None
@todo Fine-tune on football images if the COCO "sports ball" class is weak.
"""

from dataclasses import dataclass

import numpy as np

from . import config


@dataclass
class Detection:
    """A single detection with a pixel box, confidence, class id, and track id."""
    box: np.ndarray          # [x1, y1, x2, y2] in pixels
    confidence: float
    class_id: int
    track_id: int = -1       # -1 when not tracked

    @property
    def is_person(self) -> bool:
        return self.class_id == config.PERSON_CLASS_ID

    @property
    def is_ball(self) -> bool:
        return self.class_id == config.SPORTS_BALL_CLASS_ID


class Detector:
    """Wraps a YOLO model; returns person + ball detections, optionally tracked."""

    def __init__(self, model_name: str = config.DEFAULT_MODEL,
                 confidence: float = config.DEFAULT_CONFIDENCE):
        from ultralytics import YOLO  # lazy import keeps non-CV tooling fast
        self._model = YOLO(model_name)
        self._confidence = confidence

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Run detection on one BGR frame, filtered to person + ball."""
        return self._run(frame, track=False)

    def track(self, frame: np.ndarray) -> list[Detection]:
        """Run detection + ByteTrack tracking on one BGR frame."""
        return self._run(frame, track=True)

    def _run(self, frame: np.ndarray, track: bool) -> list[Detection]:
        """Run inference and convert results into Detection records."""
        if track:
            results = self._model.track(frame, conf=self._confidence,
                                        persist=True, verbose=False)
        else:
            results = self._model.predict(frame, conf=self._confidence,
                                          verbose=False)
        detections = []
        for result in results:
            for index, box in enumerate(result.boxes):
                class_id = int(box.cls[0])
                if class_id not in (config.PERSON_CLASS_ID, config.SPORTS_BALL_CLASS_ID):
                    continue
                track_id = self._track_id(result, index, track)
                detections.append(Detection(
                    box=box.xyxy[0].cpu().numpy(),
                    confidence=float(box.conf[0]),
                    class_id=class_id,
                    track_id=track_id,
                ))
        return detections

    def _track_id(self, result, index: int, track: bool) -> int:
        if not track or result.boxes.id is None:
            return -1
        return int(result.boxes.id[index])
