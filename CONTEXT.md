# Project Context — Routing Map

Where to work, given what the user wants.

## Routes
| Task | Start here |
|---|---|
| Add / change an analysis metric | `touchline/metrics/` |
| Pipeline orchestration (frame loop) | `touchline/__main__.py` |
| Detection / model changes | `touchline/detection.py` |
| Calibration / pitch mapping | `touchline/calibration.py`, `touchline/projection.py` |
| Tracking | `touchline/tracking.py` |
| Report output (JSON/HTML) | `touchline/report.py` |
| Desktop app (future) | `plan.md` — Tier 4 (delegated, not built yet) |

## Shared context
- Architecture: `_config/architecture.md`
- Stack & dependencies: `_config/stack.md`
- Decisions & rationale: `_config/decisions.md`
- Coding conventions: `_config/coding-conventions.md` (canonical limits live here)
- Full rules: `research/pi-agent-rules.md`, `research/pi-coding-conventions.md`

## Build order
Difficulty ladder lives in `plan.md`. Build easiest → hardest. Current state in `TODO.md`.
