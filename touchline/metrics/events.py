"""
@file metrics/events.py
@description Event detection (passes, shots, goals, corners). Tier 3 — the
  hardest stage. Planned as heuristics over ball + player trajectories.

@status Not implemented — returns an empty result so the pipeline runs.
@issues None
@todo
  - [ ] Shot: ball velocity spike toward goal + location in the attacking third
  - [ ] Goal: ball crosses the goal line between the posts after a shot
  - [ ] Corner: ball crosses the goal line outside the goal, last touched by a player
  - [ ] Pass: ball moves between two same-team players with a velocity dip
"""


def detect_events(frame_records, fps: float) -> dict:
    """Detect match events from processed frame records.

    Not implemented yet. Returns an empty result so the pipeline still runs.
    """
    return {"events": [], "note": "event detection not yet implemented"}
