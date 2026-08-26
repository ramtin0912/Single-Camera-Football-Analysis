# Stack

## Language & runtime
- Python 3.10+ (developed against 3.11).
- Standard library for CLI (`argparse`) and file I/O.

## Core dependencies (see `requirements.txt`)
- `opencv-python` — video I/O, homography, drawing, color clustering (k-means).
- `numpy` — arrays, geometry, histograms.
- `ultralytics` — YOLOv8 for player + ball detection (also pulls in `torch`).

No other dependencies. Tracking is a hand-written IoU tracker (no extra lib).
Events are heuristics, not models.

## Deliberately NOT used
- No deep-learning tracking (ByteTrack/SORT) — hand-written IoU tracker is enough
  for team-level distance/speed and keeps the stack simple.
- No ML model for events — heuristic rules only.
- No per-player identity (jersey number OCR) — out of scope for now.

## Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
First run downloads the YOLOv8 weights (default `yolov8n.pt`) automatically.
