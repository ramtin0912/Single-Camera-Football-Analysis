"""
@file metrics/possession.py
@description Estimate which team has the ball per frame: the nearest player to
  the ball within a radius; otherwise the frame is contested.

@status None
@issues Ball misdetection propagates into possession.
@todo Smooth over time (hold possession until a clear change) later.
"""

import numpy as np

from .. import config


def compute_possession(frame_records) -> dict:
    """Return possession counts and fractions from processed frame records."""
    counts = {"team_0": 0, "team_1": 0, "contested": 0, "no_ball": 0}
    for record in frame_records:
        if record.ball is None:
            counts["no_ball"] += 1
            continue
        team = _nearest_player_team(record.ball, record.players)
        if team is None:
            counts["contested"] += 1
        elif team == 0:
            counts["team_0"] += 1
        else:
            counts["team_1"] += 1
    return {"counts": counts, "fractions": _as_fractions(counts)}


def _nearest_player_team(ball, players):
    """Return the team of the nearest player to the ball, or None if too far."""
    if not players:
        return None
    positions = np.array([[player.x, player.y] for player in players],
                         dtype=np.float64)
    distances = np.linalg.norm(positions - np.asarray(ball, dtype=np.float64), axis=1)
    nearest = int(np.argmin(distances))
    if distances[nearest] > config.POSSESSION_RADIUS_M:
        return None
    return players[nearest].team_id


def _as_fractions(counts) -> dict:
    total = sum(counts.values())
    return {key: round(value / total, 4) if total else 0.0
            for key, value in counts.items()}
