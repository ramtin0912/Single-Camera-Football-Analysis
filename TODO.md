# TODO — Touchline

Track current work. Sections follow `plan.md`.

## Done
- [x] S1 Project base: docs, `_config/`, git, requirements, structure
- [x] S2 Tier 0 + Tier 1 code: calibration, detection, team split, territory,
      possession, heatmaps (written, compiles; run pending deps)
- [x] S3 Tier 2 code: tracking -> distance & speed (ByteTrack, not hand-rolled)
- [x] S5 smoke test script (`scripts/smoke_test.py`) written
- [x] Re-architecture to open-source-first: ByteTrack, NBJW auto-calibration,
      SoccerNet action-spotting plan; CLAUDE.md -> AGENTS.md
- [x] NBJW auto-calibration adapter (`scripts/nbjw_homography.py`) — implemented
      against NBJW inference.py; not yet executed (needs torch)

## In progress
- [ ] S4 Tier 3: events via SoccerNet action spotting (lRomul/ball-action-spotting
      or sn-spotting) — `touchline/metrics/events.py`

## Next (on your machine, after `pip install -r requirements.txt`)
- [ ] Run `python scripts/smoke_test.py` — expect 4 PASS
- [ ] Run `python -m touchline sample.mp4 --out output/match1` on a real clip
- [ ] Fine-tune ball detector (football images) if COCO "sports ball" is weak

## Later (delegated)
- [ ] Desktop app wrapping the pipeline (Tier 4)
- [ ] Per-player identity (jersey numbers)
