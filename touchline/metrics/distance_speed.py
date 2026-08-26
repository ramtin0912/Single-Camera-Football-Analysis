"""
@file metrics/distance_speed.py
@description Distance covered and average speed per tracklet and per team.

@status None
@issues IoU tracklet fragmentation can inflate team distance totals.
@todo None
"""

import numpy as np


def compute_distance_speed(frame_records, fps: float) -> dict:
    """Return per-tracklet and per-team distance/speed summaries."""
    tracklets = _group_by_track(frame_records)
    summaries = [_summarise_tracklet(track_id, samples, fps)
                 for track_id, samples in tracklets.items()]
    return {"tracklets": summaries, "teams": _team_totals(summaries)}


def _group_by_track(frame_records) -> dict:
    grouped = {}
    for record in frame_records:
        for player in record.players:
            if player.track_id < 0:
                continue
            grouped.setdefault(player.track_id, []).append((record.frame_index, player))
    return grouped


def _summarise_tracklet(track_id: int, samples: list, fps: float) -> dict:
    ordered = sorted(samples, key=lambda item: item[0])
    positions = np.array([[player.x, player.y] for _, player in ordered],
                         dtype=np.float64)
    distance = float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum())
    duration = _tracklet_duration(ordered, fps)
    speed = distance / duration if duration > 0 else 0.0
    return {
        "track_id": track_id,
        "distance_m": round(distance, 2),
        "duration_s": round(duration, 2),
        "avg_speed_ms": round(speed, 2),
        "team_id": _majority_team([player.team_id for _, player in ordered]),
        "samples": len(ordered),
    }


def _tracklet_duration(ordered, fps: float) -> float:
    if len(ordered) < 2:
        return 0.0
    return (ordered[-1][0] - ordered[0][0]) / fps


def _majority_team(team_ids) -> int:
    values = [team_id for team_id in team_ids if team_id >= 0]
    if not values:
        return -1
    return max(set(values), key=values.count)


def _team_totals(summaries) -> dict:
    totals = {"team_0_distance_m": 0.0, "team_1_distance_m": 0.0}
    for summary in summaries:
        key = f"team_{summary['team_id']}_distance_m" if summary["team_id"] >= 0 else None
        if key:
            totals[key] += summary["distance_m"]
    return {key: round(value, 2) for key, value in totals.items()}
