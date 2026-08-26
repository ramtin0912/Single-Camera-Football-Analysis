# Touchline — Agent Orientation

## Project
Touchline turns sideline phone footage of a football (soccer) match into simple
analysis data: possession/territory, team heatmaps, distance/speed, and later
events. Football means soccer (FIFA rules). Never American football (NFL).

## Navigation
- `touchline/` — the Python analysis package (pipeline + metrics)
- `scripts/` — helper scripts (synthetic test footage, etc.)
- `_config/` — stable project rules (architecture, stack, decisions)
- `output/` — runtime analysis output (gitignored)
- `plan.md` / `TODO.md` — current plan and task state

## Non-negotiables
- Prefer the smallest change that solves the task.
- No complex models or stats. Heuristics and simple CV only.
- Football terminology only (touchline, half, penalty area, goal — never NFL terms).
- Read `CONTEXT.md` before routing work.
- Follow `_config/coding-conventions.md` (file/function size limits, file headers).
- No implicit persistence: every write traces to an explicit user action.

## Start here
Read `CONTEXT.md` for task routing, then `plan.md` for current state.
