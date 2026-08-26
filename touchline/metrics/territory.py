"""
@file metrics/territory.py
@description Ball territory: fraction of time the ball spends in each third and
  each half of the pitch. Tier 1 — needs only the ball position.

@status None
@issues None
@todo None
"""

import numpy as np

from .. import config

THIRD_HALF_WIDTH_M = config.PITCH_LENGTH_M / 6.0  # half of one third


def compute_territory(frame_records) -> dict:
    """Return territory fractions from processed frame records."""
    xs = np.array([record.ball[0] for record in frame_records
                   if record.ball is not None], dtype=np.float64)
    if xs.size == 0:
        return {"samples": 0, "thirds": {}, "halves": {}}
    thirds = {
        "left": _fraction(xs < -THIRD_HALF_WIDTH_M),
        "middle": _fraction(np.abs(xs) <= THIRD_HALF_WIDTH_M),
        "right": _fraction(xs > THIRD_HALF_WIDTH_M),
    }
    halves = {
        "left": _fraction(xs < 0),
        "right": _fraction(xs >= 0),
    }
    return {"samples": int(xs.size), "thirds": thirds, "halves": halves}


def _fraction(mask) -> float:
    count = int(np.count_nonzero(mask))
    total = int(mask.size)
    return round(count / total, 4) if total else 0.0
