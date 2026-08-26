# Touchline

Turn sideline phone footage of a football (soccer) match into simple, useful
analysis data: possession and territory, team heatmaps, distance and speed, and
later events (shots, goals, corners).

Built for a coach and a team analyst working with a single phone camera on the
touchline. Post-match: record, run the pipeline, read the report.

Football means soccer (FIFA rules). Nothing here relates to American football.

Open-source-first: detection and tracking come from Ultralytics YOLOv8 +
ByteTrack, auto pitch calibration from No Bells Just Whistles, and events from
SoccerNet action spotting — Touchline writes the glue, not new models.

## What it does
- Reads a match video (`.mp4`, `.mov`, etc.).
- Calibrates the pitch once (click 4+ known points) and caches it.
- Detects players and the ball, splits teams by jersey colour.
- Outputs `report.json` (machine-readable) and `report.html` (human-readable)
  with territory %, possession %, team heatmaps, and distance/speed.

## Setup
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
First run downloads the YOLOv8 nano weights automatically.

## Run
```
python -m touchline path/to/match.mp4 --out output/match1
```On first run you will click calibration points on a still frame:
near-left corner, near-right corner, far-right corner, far-left corner (near =
the camera side). Press `q` to finish early once 4 points are set; optional
extra points (centre spot, penalty spots) improve accuracy.

Useful options:
- `--frame-step 2` — process every 2nd frame (faster; fine for territory/heatmaps).
- `--model yolov8n.pt` — use a different YOLO model.
- `--calibration output/match1/calibration.json` — reuse a saved calibration.
- `--auto-calibrate /path/to/no-bells-just-whistles` — auto pitch calibration
  via the NBJW open-source model (see `_config/integrations.md`); manual click
  is the fallback.

## Test the metric core (no video needed)
```
python scripts/smoke_test.py
```
Builds synthetic frame records and checks territory, possession, and
distance/speed. All four checks should print PASS.

## Output (in the `--out` directory)
- `report.json` — all metrics as structured data (the stable contract).
- `report.html` — self-contained view of the same data.
- `heatmap_team_0.png`, `heatmap_team_1.png` — team heatmaps on a pitch.

## Framing tips for the camera
- Keep the camera still and wide enough to see most of the pitch.
- Ideally all four corners are visible; at minimum the two touchline corners on
  your side plus two far-side points (penalty-area or halfway-line landmarks).
- Higher frame rate improves distance/speed accuracy; territory/possession are
  robust at lower rates.

## Project docs
- `plan.md` — full plan and difficulty ladder.
- `_config/architecture.md` — data flow and module boundaries.
- `_config/decisions.md` — why each choice was made.
