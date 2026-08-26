"""
@file video_io.py
@description Open a match video and yield frames; expose fps, size, and count.

@status None
@issues None
@todo None
"""

import cv2


class MatchVideo:
    """Reads a video file frame by frame for the analysis pipeline."""

    def __init__(self, path: str):
        self.path = path
        self._capture = cv2.VideoCapture(path)
        if not self._capture.isOpened():
            raise ValueError(f"Cannot open video: {path}")

    @property
    def fps(self) -> float:
        return self._capture.get(cv2.CAP_PROP_FPS) or 25.0

    @property
    def width(self) -> int:
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        return int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def frame_count(self) -> int:
        return int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def read_frame(self, index: int):
        """Read a single frame by index (used for calibration)."""
        self._capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = self._capture.read()
        if not ok:
            raise RuntimeError(f"Could not read frame {index}")
        return frame

    def frames(self, step: int = 1):
        """Yield (frame_index, frame) pairs, stepping `step` frames."""
        self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        index = 0
        while True:
            ok, frame = self._capture.read()
            if not ok:
                break
            if index % step == 0:
                yield index, frame
            index += 1

    def release(self) -> None:
        self._capture.release()
