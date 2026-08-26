"""
@file metrics/events.py
@description Event detection (passes, shots, goals, corners). Tier 3 — the
  hardest stage.

  Primary plan: adopt an open-source SoccerNet action-spotting model instead
  of hand-rolled heuristics. Candidates:
    - lRomul/ball-action-spotting (12 classes: Pass, Shot, Goal, Header,
      Cross, Throw In, etc.)
    - SoccerNet/sn-spotting baselines (CALF / NetVLAD), with pretrained weights.

  See _config/integrations.md for setup.

@status Not implemented — returns an empty result so the pipeline runs.
@issues Open-source action-spotting models are trained on broadcast footage;
  domain shift to a fixed sideline camera must be evaluated.
@todo
  - [ ] Run an action-spotting model on the match video (see integrations.md)
  - [ ] Map its event timestamps onto our pitch coordinates
  - [ ] Keep heuristic fallback only as a comparison baseline
"""


def detect_events(frame_records, fps: float) -> dict:
    """Detect match events from processed frame records.

    Not implemented yet. Returns an empty result so the pipeline still runs.
    """
    return {"events": [], "note": "event detection not yet implemented"}
