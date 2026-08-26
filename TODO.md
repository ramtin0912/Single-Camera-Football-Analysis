# TODO — Touchline

Track current work. Sections follow `plan.md`.

## Done
- [x] S1 Project base: docs, `_config/`, git, requirements, structure
- [x] S2 Tier 0 + Tier 1: calibration, detection, team split, territory,
      possession, heatmaps
- [x] S3 Tier 2: tracking -> distance & speed

## In progress
- [ ] S4 Tier 3: events (passes, shots, goals, corners) — stubbed in
      `touchline/metrics/events.py`

## Next
- [ ] S5 Synthetic test footage (`scripts/make_synthetic_match.py`) + smoke test
- [ ] Install deps locally and run end-to-end on a real clip
- [ ] Fine-tune ball detector (football images) if COCO "sports ball" is weak

## Later (delegated)
- [ ] Desktop app wrapping the pipeline (Tier 4)
- [ ] Auto pitch detection (replace manual calibration)
- [ ] Per-player identity (jersey numbers)
