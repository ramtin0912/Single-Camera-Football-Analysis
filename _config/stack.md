# Stack

## Language & runtime
- Python 3.10+ (developed against 3.11).
- Standard library for CLI (`argparse`) and file I/O.

## Core dependencies (see `requirements.txt`)
- `opencv-python` — video I/O, homography, drawing, colour clustering (k-means).
- `numpy` — arrays, geometry, histograms.
- `ultralytics` — YOLOv8 detection + ByteTrack tracking (also pulls in `torch`).

## Open-source components adopted (not built ourselves)
- **Ultralytics YOLOv8** — player + ball detection.
- **Ultralytics ByteTrack** — tracking.
- **No Bells, Just Whistles** (`mguti97/no-bells-just-whistles`) — auto pitch
  calibration (separate checkout).
- **SoccerNet action spotting** (`lRomul/ball-action-spotting` or `sn-spotting`) —
  events (Tier 3, separate checkout).

Setup for the separate checkouts is in `_config/integrations.md`.

## Deliberately NOT used / NOT built
- No hand-rolled tracker — ByteTrack is used.
- No hand-rolled event heuristics — SoccerNet action spotting is used.
- No custom training in this phase — pretrained weights only.
- No per-player identity (jersey number OCR) — out of scope for now.

## Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
First run downloads the YOLOv8 weights (default `yolov8n.pt`) automatically.
NBJW and SoccerNet action spotting use their own separate environments.
