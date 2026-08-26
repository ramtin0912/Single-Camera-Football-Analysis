# Open-source integrations

Touchline is open-source-first: it adopts existing, published components instead
of building models, trackers, or event detectors from scratch. This file records
what each component does, where it lives, and how to set it up.

## Detection + tracking — Ultralytics YOLOv8 + ByteTrack
- Repo: https://github.com/ultralytics/ultralytics
- What: player + ball detection (COCO "person" / "sports ball") and ByteTrack
  tracking via `model.track(persist=True)`.
- Setup: already a dependency — `pip install -r requirements.txt`.
- Used in: `touchline/detection.py`.

## Pitch calibration (auto) — No Bells, Just Whistles
- Repo: https://github.com/mguti97/no-bells-just-whistles
- What: single-view football pitch homography from field keypoints + lines,
  then DLT. CVPRW 2024. Minimalist / geometric ("no bells, just whistles").
- Setup:
  1. `git clone https://github.com/mguti97/no-bells-just-whistles`
  2. Install its requirements (its README suggests a conda env `NBJWCalib`).
  3. Download single-view weights `SV_kp` and `SV_lines` from its Releases page.
- Used in: `touchline/calibration.py`, which calls
  `scripts/nbjw_homography.py` (the glue that reuses NBJW's own model code and
  writes a Touchline-format homography). Manual click is the fallback.
- Status: adapter implemented, written against NBJW's `inference.py`; not yet
  executed end-to-end — needs the NBJW environment + torch.

## Action spotting (events) — SoccerNet
- Repos:
  - https://github.com/SoccerNet/sn-spotting (dev kit, 17 event classes)
  - https://github.com/lRomul/ball-action-spotting (12 ball-action classes:
    Pass, Shot, Goal, Header, Cross, Throw In, etc.)
- What: pretrained action-spotting models output event labels + timestamps.
- Setup: clone the repo, download its pretrained weights, follow its README.
- Used in: `touchline/metrics/events.py` (Tier 3, not yet wired).
- Status: planned — run on the match video, then map event timestamps onto our
  pitch coordinates.

## Team split — jersey colour k-means
- No external model: a standard OpenCV k-means on Lab (a, b) jersey colour. This
  is a classic, non-learned technique (not a model we build), kept because no
  general off-the-shelf "team labeler" exists for arbitrary kits.
- Used in: `touchline/team_assignment.py`.

## Domain-shift note
NBJW and the SoccerNet action-spotting models are trained on broadcast footage
(main camera, pan/tilt/zoom). Our input is a fixed sideline phone camera. This is
a simpler camera for calibration, but accuracy must still be checked on real
sideline clips; the manual-calibration fallback exists for that reason.
