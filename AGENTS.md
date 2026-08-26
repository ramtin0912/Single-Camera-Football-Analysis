# Touchline — Agent Orientation

## Project
Touchline turns sideline phone footage of a football (soccer) match into simple
analysis data: possession/territory, team heatmaps, distance/speed, and later
events. Football means soccer (FIFA rules). Never American football (NFL).

## Navigation
- `touchline/` — the Python analysis package (pipeline + metrics)
- `scripts/` — helper scripts (metric smoke test, etc.)
- `_config/` — stable project rules (architecture, stack, decisions, integrations)
- `output/` — runtime analysis output (gitignored)
- `plan.md` / `TODO.md` — current plan and task state

## Non-negotiables
- Prefer the smallest change that solves the task.
- Open-source-first: adopt published tools (SoccerNet, Ultralytics YOLO +
  ByteTrack, No Bells Just Whistles); do not build models or trackers ourselves.
- Football terminology only (touchline, half, penalty area, goal — never NFL terms).
- Read `CONTEXT.md` before routing work.
- Follow `_config/coding-conventions.md` (file/function size limits, file headers).
- No implicit persistence: every write traces to an explicit user action.

## Start here
Read `CONTEXT.md` for task routing, then `plan.md` for current state.
