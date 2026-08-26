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

## In progress
(none)

## Next (on your machine)
- [ ] `pip install -r requirements.txt`, then `python scripts/smoke_test.py` —
      expect 5 PASS
- [ ] Run `python -m touchline sample.mp4 --out output/match1` on a real clip
- [ ] Clone NBJW + download `SV_kp`/`SV_lines`, then `--auto-calibrate` on a clip
- [ ] Clone ball-action-spotting + download weights (GPU), then
      `--include-events --action-spotting-repo /path/to/repo`
- [ ] Fine-tune ball detector if COCO "sports ball" is weak

## Later (delegated)
- [ ] Desktop app wrapping the pipeline (Tier 4)
- [ ] Per-player identity (jersey numbers)
