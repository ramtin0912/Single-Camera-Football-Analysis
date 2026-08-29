"""
@file smoke_test.py
@description Synthetic smoke test for the metric core (no video or model
  needed): builds FrameRecords with known motion and checks territory,
  possession, and distance/speed behave as expected.

@status None
@issues None
@todo None

Run (after `pip install -r requirements.txt`):
    python scripts/smoke_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from touchline.metrics import distance_speed, events, possession, territory
from touchline.records import FrameRecord, PlayerRecord

FPS = 25.0
FRAME_STEP = 2
FRAME_COUNT = 100
DRIFT_PER_FRAME = 0.04


def build_frame_records() -> list[FrameRecord]:
    """Build synthetic frames: team 0 in the left third, team 1 in the right,
    ball shadowing team 0's first player."""
    player_specs = [
        (0, -35.0, 0.0), (0, -30.0, 10.0), (0, -28.0, -10.0),
        (0, -25.0, 15.0), (0, -22.0, -15.0),
        (1, 30.0, 0.0), (1, 35.0, 10.0), (1, 28.0, -10.0),
        (1, 32.0, 15.0), (1, 26.0, -15.0),
    ]
    records = []
    for frame_index in range(0, FRAME_COUNT * FRAME_STEP, FRAME_STEP):
        drift = DRIFT_PER_FRAME * frame_index
        players = [
            PlayerRecord(x=base_x + drift, y=base_y,
                         team_id=team_id, track_id=track_id)
            for track_id, (team_id, base_x, base_y) in enumerate(player_specs)
        ]
        ball = (-35.0 + drift + 0.5, 0.5)
        records.append(FrameRecord(frame_index=frame_index, ball=ball,
                                   players=players))
    return records


def check(condition: bool, label: str) -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    return condition


def main() -> int:
    records = build_frame_records()
    territory_result = territory.compute_territory(records)
    possession_result = possession.compute_possession(records)
    distance_result = distance_speed.compute_distance_speed(records, FPS)

    print("Territory thirds:", territory_result["thirds"])
    print("Possession fractions:", possession_result["fractions"])
    print("Distance per team:", distance_result["teams"])

    results = [
        check(territory_result["thirds"]["left"] > 0.9,
              "ball stays in the left third"),
        check(possession_result["fractions"]["team_0"] > 0.9,
              "team 0 holds possession"),
        check(distance_result["teams"]["team_0_distance_m"] > 0,
              "team 0 distance is non-zero"),
        check(len(distance_result["tracklets"]) == 10,
              "all ten players were tracked"),
    ]

    raw_events = [{"label": "SHOT", "position_ms": 2000, "confidence": 0.9}]
    event_list = events.attach_pitch_positions(raw_events, records, FPS)
    print("Events:", event_list)
    results.append(check(
        len(event_list) == 1 and event_list[0]["frame_index"] == 50,
        "event timestamp mapped to a frame with a ball position"))

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
