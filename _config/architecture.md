# Architecture

## Shape
Touchline is a **linear pipeline** (no server, no UI, no database). It reads one
match video and writes one analysis report. This matches the "post-match, run a
script, get output" goal. A desktop app will later wrap this pipeline, so the
pipeline is kept as a plain Python package with a CLI.

## Data flow
```
phone video (mp4)
  -> video_io: read frames
  -> calibration: pitch homography (manual 4+ point click, cached to JSON)
  -> detection: YOLOv8 -> player + ball boxes per frame
  -> projection: box feet -> pitch metres (via homography)
  -> team_assignment: jersey colour k-means -> team 0 / team 1
  -> tracking: IoU tracker -> track IDs
  -> metrics: territory, possession, heatmaps, distance/speed, (events: later)
  -> report: report.json + report.html (+ heatmap PNGs)
```

## Module boundaries
| Module | Responsibility |
|---|---|
| `video_io.py` | Open video, yield frames |
| `calibration.py` | Click landmarks, compute/save/load homography |
| `detection.py` | Run YOLO, return typed detections |
| `projection.py` | Feet point, pixel -> pitch metres |
| `team_assignment.py` | Colour centroids + team label |
| `tracking.py` | Frame-to-frame track IDs (IoU) |
| `pitch.py` | Pitch landmarks, SVG/canvas drawing |
| `metrics/*` | Pure functions: detections in -> numbers out |
| `report.py` | Serialise metrics to JSON + HTML |
| `__main__.py` | CLI + orchestration loop |

## Invariants
- Metrics modules are pure: they take arrays/records and return dicts. They do
  not touch video, models, or files. This keeps them testable and reusable by
  the future desktop app.
- All pixel->pitch projection uses the **feet point** (bottom centre of a box),
  never box centre — the feet lie on the ground plane the homography maps.
- Calibration is cached so re-runs do not re-click.

## Concurrency
None. Single-threaded, deterministic, easy to debug. If speed becomes a problem,
frame sampling (`--frame-step`) is the first lever, not threads.
