# Plan — Touchline

Turn sideline phone footage of a football (soccer) match into simple, useful
analysis data for a coach and a team analyst. Football means soccer (FIFA).

## Problem
A grassroots team has one phone filming from the touchline. They want analysis
but have no budget for multi-camera rigs or GPS. One fixed sideline camera is
the key simplification: it does not pan/zoom, so the pitch-to-image mapping
(homography) is nearly constant — the whole problem becomes tractable with
simple computer vision.

## Users
- **Coach** — team-level insight: territory, possession, shape, work rate.
- **Team analyst** — same numbers, but also wants exportable data.

## Scope (this phase)
A Python pipeline of scripts/algorithms: `video in -> report out`. No GUI.
The desktop app is **Tier 4, delegated** — the pipeline is built as a plain
package so a desktop app can wrap it later without rewrite.

**Open-source-first:** adopt published tools (SoccerNet action spotting,
Ultralytics YOLO + ByteTrack, No Bells Just Whistles) rather than building
models, trackers, or event detectors ourselves. We write the glue.

## Non-goals
- No desktop app / mobile app UI (later).
- No building our own complex models or stats — use open-source ones instead.
- No per-player identity (jersey-number OCR). Team-level only for now.
- No live/streaming analysis. Post-match only.

## Tech stack
Python 3.10+, OpenCV, NumPy, ultralytics (YOLOv8). See `_config/stack.md`.

## Difficulty ladder (build order — easiest first)

### Tier 0 — Foundation (prerequisites, not analytics yet)
1. Video ingestion — read phone footage, yield frames.
2. Pitch calibration + homography — NBJW auto (open source), manual 4+ click
   fallback -> pixels to pitch metres.
3. Player + ball detection — YOLOv8, filter to person + sports-ball.
4. Team assignment — jersey colour k-means -> team 0 / team 1.
5. Projection — box feet point -> pitch coordinates.

### Tier 1 — Easiest analytics
6. **Territory** — % time the ball is in each third / half (ball position only).
7. **Possession** — which team has the ball (ball + nearest player's team).
8. **Team heatmaps & shape** — where each team's players are.

### Tier 2 — Medium
9. Tracking — ByteTrack via ultralytics (open source).
10. **Distance & speed** — per team, and per tracklet (proxy for a player).

### Tier 3 — Hardest
11. **Events** — passes, shots, goals, corners via SoccerNet action spotting
    (open source; lRomul/ball-action-spotting or sn-spotting).

### Tier 4 — Delegated (not in this phase)
12. Desktop app wrapping the pipeline.
13. Auto pitch detection (replace manual calibration).
14. Fine-tuned football detector + real per-player identity.

## Build sections
> Status: S2-S5 are written and **verified in the Debian 12 Docker container**:
> the metric smoke test passes 5/5, YOLOv8n + ByteTrack detection is verified
> on a real image, and the pipeline runs end-to-end (video -> calibration ->
- [x] S1 — Project base: docs, config, structure, CLI skeleton
- [x] S2 — Tier 0 + Tier 1: calibration, detection, team split, territory,
      possession, heatmaps (working end-to-end)
- [x] S3 — Tier 2: tracking -> distance & speed
- [x] S4 — Tier 3: events adapter (action-spotting glue + pitch mapping)
- [x] S5 — Metric smoke test script (`scripts/smoke_test.py`)

## Acceptance criteria (per section)
- S2: `python -m touchline sample.mp4` produces territory %, possession %,
  and team heatmap PNGs in `output/`.
- S3: report includes per-team distance and per-tracklet distance/speed.
- S4: report includes detected events with timestamps and pitch positions.
- S5: `python scripts/smoke_test.py` reproduces known territory/possession/
  distance values and all checks pass.

## Risks / unknowns
- Ball detection is the weak point (small, fast, occluded). Mitigation: COCO
  "sports ball" now, fine-tune later; tolerate "unknown" possession.
- One camera cannot see all four pitch corners in tight shots — calibration
  requires wide-enough framing. Mitigation: document framing guidance.
- Open-source models (NBJW, action spotting) are trained on broadcast footage;
  a fixed sideline camera is a domain shift. Mitigation: validate on real
  sideline clips, keep manual-calibration fallback.
- k=2 colour clustering can absorb the referee. Mitigation: note as known issue,
  filter near-black/referee colours later.
