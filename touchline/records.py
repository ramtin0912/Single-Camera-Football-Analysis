"""
@file records.py
@description Plain data records produced by the pipeline and consumed by the
  metrics. Dataclasses only, so metrics stay pure and UI-agnostic.

@status None
@issues None
@todo None
"""

from dataclasses import dataclass, field


@dataclass
class PlayerRecord:
    """A detected player projected to pitch metres, with team and track labels."""
    x: float
    y: float
    team_id: int = -1
    track_id: int = -1
    colour_ab: tuple | None = None   # Lab (a, b) jersey colour for team assignment


@dataclass
class FrameRecord:
    """Everything detected in one processed frame."""
    frame_index: int
    ball: tuple | None = None        # (x, y) metres; None when no ball detected
    players: list[PlayerRecord] = field(default_factory=list)
