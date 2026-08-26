# TODO — Touchline

Track current work. Sections follow `plan.md`.

## Done
- [x] S1 Project base: docs, `_config/`, git, requirements, structure
- [x] S2 Tier 0 + Tier 1 code: calibration, detection, team split, territory,
      possession, heatmaps (written, compiles; run pending deps)
- [x] S3 Tier 2 code: tracking -> distance & speed (written, compiles)
- [x] S5 smoke test script (`scripts/smoke_test.py`) written

## In progress
- [ ] S4 Tier 3: events (passes, shots, goals, corners) — stubbed in
      `touchline/metrics/events.py`

## Next (on your machine, after `pip install -r requirements.txt`)
- [ ] Run `python scripts/smoke_test.py` — expect 4 PASS
- [ ] Run `python -m touchline sample.mp4 --out output/match1` on a real clip
- [ ] Fine-tune ball detector (football images) if COCO "sports ball" is weak

## Later (delegated)
- [ ] Desktop app wrapping the pipeline (Tier 4)
- [ ] Auto pitch detection (replace manual calibration)
- [ ] Per-player identity (jersey numbers)
