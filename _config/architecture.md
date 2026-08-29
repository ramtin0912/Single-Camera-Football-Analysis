# Architecture

## Shape
Touchline is a **linear pipeline** (no server, no UI, no database). It reads one
match video and writes one analysis report. This matches the "post-match, run a
script, get output" goal. A desktop app will later wrap this pipeline, so the
pipeline is kept as a plain Python package with a CLI.

Touchline is **open-source-first**: it adopts published, purpose-built components
(SoccerNet, Ultralytics YOLO + ByteTrack, No Bells Just Whistles) rather than
building models or trackers from scratch. See `_config/integrations.md`.

## Data flow
```
phone video (mp4)
  -> video_io: read frames
  -> calibration: pitch homography (NBJW auto, manual click fallback; cached JSON)
  -> detection: YOLOv8 -> player + ball boxes per frame
  -> tracking: ByteTrack (ultralytics) -> track IDs
  -> projection: box feet -> pitch metres (via homography)
  -> team_assignment: jersey colour k-means -> team 0 / team 1
  -> metrics: territory, possession, heatmaps, distance/speed
  -> events: SoccerNet action spotting (Tier 3, adapter written)
  -> report: report.json + report.html (+ heatmap PNGs)
```

## Module boundaries
| Module | Responsibility |
|---|---|
| `video_io.py` | Open video, yield frames |
| `calibration.py` | Auto (NBJW) or manual click -> homography; cache JSON |
| `detection.py` | Run YOLO, detect + ByteTrack, return typed detections |
| `projection.py` | Feet point, pixel -> pitch metres |
| `team_assignment.py` | Colour centroids + team label |
| `pitch.py` | Pitch landmarks, drawing canvas |
| `metrics/*` | Pure functions: detections in -> numbers out |
| `action_spotting.py` | Run the SoccerNet action-spotting model (glue) |
| `report.py` | Serialise metrics to JSON + HTML |
| `pipeline.py` | Orchestration loop |
| `__main__.py` | CLI entry |

## Invariants
- Metrics modules are pure: they take arrays/records and return dicts. They do
  not touch video, models, or files. This keeps them testable and reusable by
  the future desktop app.
- All pixel->pitch projection uses the **feet point** (bottom centre of a box),
  never box centre — the feet lie on the ground plane the homography maps.
- Calibration is cached so re-runs do not re-click.
- Tracking comes from ByteTrack inside `detection.py`; there is no hand-rolled
  tracker in the project.

## Concurrency
None. Single-threaded, deterministic, easy to debug. If speed becomes a problem,
frame sampling (`--frame-step`) is the first lever, not threads.
