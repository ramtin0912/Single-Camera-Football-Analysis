# Coding Conventions

Canonical limits and style for this project. Full rules live in
`research/pi-agent-rules.md` and `research/pi-coding-conventions.md`.

## Non-negotiable limits
| Measure | Limit |
|---|---|
| Function body | under 50 lines |
| File (code) | under 300 lines |

## Every source file starts with a header docstring
```python
"""
@file module_name.py
@description What this file does (1-3 lines)

@status None
@issues None
@todo None
"""
```
Keep `@status`/`@issues`/`@todo` current. Reset to `None` when cleared.

## Style
- Python 3.10+, type hints on all public functions.
- Descriptive names: `compute_territory` not `calc`, `player_detections` not `d`.
- `const`-like module-level UPPER_SNAKE_CASE for config values (live in `config.py`).
- No magic numbers inline — reference `touchline/config.py` constants.
- No dead/commented-out code. Delete it.
- No implicit persistence (rule: user action -> write -> confirm).
- Football terminology only: touchline, half, penalty area, goal. Never NFL terms.

## Structure
- Metrics live in `touchline/metrics/`, one file per metric, pure functions.
- Orchestration only in `__main__.py`; metrics never open files or read video.

## Verification before finishing a change
- `python -m py_compile` on every changed file.
- New metric has a pure function + is wired into the report.
- File headers current; no secrets, no hardcoded values.
