"""
@file action_spotting.py
@description Run the open-source SoccerNet action-spotting model on a match
  video and return its raw events (label + position_ms + confidence).

@status Adapter wired to scripts/action_spotting.py; not executed here (GPU).
@issues None
@todo None
"""

import json
import subprocess
import sys
from pathlib import Path


def run_action_spotting(video_path: str, repo_path: str, experiment: str,
                        out_dir, fold: int = 0, device: str = "cuda:0",
                        prepare: bool = False) -> list[dict]:
    """Run the action-spotting model and return its raw event dicts."""
    repo = Path(repo_path)
    if not (repo / "src" / "predictors.py").exists():
        raise FileNotFoundError(
            f"Action-spotting repo not found at {repo_path}. Clone "
            "lRomul/ball-action-spotting (or the 2024 fork) and download its "
            "weights — see _config/integrations.md.")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw_events.json"
    script = Path(__file__).resolve().parent.parent / "scripts" / "action_spotting.py"
    command = [sys.executable, str(script),
               "--repo", str(repo),
               "--experiment", experiment,
               "--video", video_path,
               "--out", str(raw_path),
               "--fold", str(fold),
               "--device", device]
    if prepare:
        command.append("--prepare")
    subprocess.run(command, cwd=str(repo), check=True)
    with open(raw_path, "r", encoding="utf-8") as handle:
        return json.load(handle)["events"]
