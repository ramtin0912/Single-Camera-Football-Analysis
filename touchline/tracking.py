"""
@file tracking.py
@description Minimal IoU tracker: associates player boxes across frames into
  tracklets so distance and speed can be computed per tracklet.

@status None
@issues Tracklet fragmentation on overlaps can inflate team distance totals.
@todo Consider ByteTrack if per-player accuracy is ever required.
"""

import numpy as np

from . import config


def intersection_over_union(box_a, box_b) -> float:
    """Return the IoU of two boxes [x1, y1, x2, y2]."""
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    return intersection / (area_a + area_b - intersection + 1e-6)


class TrackletTracker:
    """Greedy IoU association of player boxes into persistent tracklets."""

    def __init__(self, min_iou: float = config.TRACK_MIN_IOU,
                 max_gap: int = config.TRACK_MAX_GAP_FRAMES):
        self._min_iou = min_iou
        self._max_gap = max_gap
        self._next_id = 0
        self._tracks = {}  # track_id -> {"box": np.ndarray, "last_seen": int}

    def update(self, boxes, frame_index: int) -> list[int]:
        """Return a track id for each box detected in this frame."""
        boxes = [np.asarray(box, dtype=np.float64) for box in boxes]
        self._prune_stale(frame_index)
        matched = self._match(boxes)
        return self._finalize(boxes, frame_index, matched)

    def _prune_stale(self, frame_index: int) -> None:
        stale = [track_id for track_id, track in self._tracks.items()
                 if frame_index - track["last_seen"] > self._max_gap]
        for track_id in stale:
            del self._tracks[track_id]

    def _match(self, boxes) -> dict:
        matched = {}
        unmatched = set(range(len(boxes)))
        for track_id in list(self._tracks):
            best_iou, best_index = self._min_iou, -1
            for index in unmatched:
                iou = intersection_over_union(self._tracks[track_id]["box"], boxes[index])
                if iou > best_iou:
                    best_iou, best_index = iou, index
            if best_index >= 0:
                matched[best_index] = track_id
                unmatched.discard(best_index)
        return matched

    def _finalize(self, boxes, frame_index: int, matched: dict) -> list[int]:
        result = []
        for index, box in enumerate(boxes):
            track_id = matched.get(index)
            if track_id is None:
                track_id = self._next_id
                self._next_id += 1
            self._tracks[track_id] = {"box": box, "last_seen": frame_index}
            result.append(track_id)
        return result
