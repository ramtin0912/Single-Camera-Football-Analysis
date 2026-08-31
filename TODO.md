# TODO — Touchline

Track current work. Sections follow `plan.md`.

## Done
- [x] S1 Project base: docs, `_config/`, git, requirements, structure
- [x] S2 Tier 0 + Tier 1 code: calibration, detection, team split, territory,
      possession, heatmaps (written, compiles; run pending deps)
- [x] S3 Tier 2 code: tracking -> distance & speed (ByteTrack, not hand-rolled)
- [x] S4 Tier 3 events adapter: `scripts/action_spotting.py` (glue),
      `touchline/action_spotting.py` (wrapper), `touchline/metrics/events.py`
      (timestamp -> pitch mapping); smoke test covers the mapping
- [x] S5 smoke test script (`scripts/smoke_test.py`) written
- [x] Re-architecture to open-source-first: ByteTrack, NBJW auto-calibration,
      SoccerNet action-spotting plan; CLAUDE.md -> AGENTS.md
- [x] NBJW auto-calibration adapter (`scripts/nbjw_homography.py`)
- [x] Fix NBJW adapter: swapped `coords_to_dict`/`complete_keypoints` unpacking
      crashed every auto-calibration run (TypeError); verified end-to-end
- [x] Auto-calibration frame selection: samples frames across the video with a
      plausibility gate; `--calibration-frame N` forces a specific frame
- [x] Docker-first pivot: `Dockerfile` (core + `WITH_EVENTS=1` events image),
      `.dockerignore`, README reordered Docker -> Linux/make; Windows `.bat`
      scripts removed

## Verified (Debian 12 Docker container)
- [x] `scripts/smoke_test.py` — 5/5 PASS
- [x] YOLOv8n + ByteTrack person detection on a real image (tracked IDs)
- [x] Pipeline runs end-to-end on a synthetic clip (video -> calibration ->
      detection -> metrics; stops only at the no-detections guard)
- [x] Events adapter import chain against a live ball-action-spotting checkout
      (timm 1.0.x / kornia 0.8.x / pytorch-argus 1.1.x on torch 2.13); model
      inference itself needs a GPU + Google Drive weights
- [x] NBJW adapter verified end-to-end on CPU (v1.0.0 weights): inference, camera
      solve, homography export all run; `--device auto` uses CUDA when present
- [x] NBJW sample clips (`messi_sample.png`, `iniesta_sample.mp4`) produce
      degenerate fits with the base SV models — the plausibility gate rejects
      them and the pipeline reports a clear error instead of a wrong calibration

## In progress
(none)

## Next
- [ ] Run on a real sideline clip; confirm NBJW auto-calibration plausibility on
      footage it can actually calibrate (broadcast-style wide shots)
- [ ] Ball-action-spotting weights + GPU, then
      `--include-events --action-spotting-repo /workdir` (Docker events image:
      `docker build --build-arg WITH_EVENTS=1 -t touchline:events .`)
- [ ] Fine-tune ball detector if COCO "sports ball" is weak

## Later (delegated)
- [ ] Desktop app wrapping the pipeline (Tier 4)
- [ ] Per-player identity (jersey numbers)
