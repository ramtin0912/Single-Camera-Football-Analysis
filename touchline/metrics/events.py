"""
@file metrics/events.py
@description Event detection (passes, shots, goals, corners). Tier 3 — the
  hardest stage.

  Primary path: adopt an open-source SoccerNet action-spotting model
  (lRomul/ball-action-spotting or its 2024 fork). `scripts/action_spotting.py`
  runs the model and emits raw events; this module maps those timestamps onto
  our pitch coordinates so each event carries a ball position.

@status Raw-event -> pitch mapping implemented; model glue lives in the
  action_spotting modules.
@issues Open-source action-spotting models are trained on broadcast footage;
  domain shift to a fixed sideline camera must be evaluated.
@todo None
"""

import numpy as np


def attach_pitch_positions(raw_events, frame_records, fps: float) -> list[dict]:
    """Attach the nearest detected ball position to each raw event timestamp."""
    if not raw_events or not frame_records:
        return []
    positions_by_frame = {record.frame_index: record.ball
                          for record in frame_records if record.ball is not None}
    if not positions_by_frame:
        return []
    frame_indexes = np.array(sorted(positions_by_frame), dtype=np.float64)
    events = []
    for raw in raw_events:
        target_frame = round(float(raw["position_ms"]) / 1000.0 * fps)
        nearest = int(frame_indexes[np.argmin(np.abs(frame_indexes - target_frame))])
        ball = positions_by_frame[nearest]
        events.append({
            "label": raw["label"],
            "position_ms": int(raw["position_ms"]),
            "confidence": round(float(raw["confidence"]), 4),
            "frame_index": nearest,
            "ball": [round(ball[0], 2), round(ball[1], 2)],
        })
    return events


def detect_events(frame_records, fps: float, raw_events=None) -> dict:
    """Return events with pitch positions; empty when no model was run."""
    events = attach_pitch_positions(raw_events or [], frame_records, fps)
    return {"events": events}
