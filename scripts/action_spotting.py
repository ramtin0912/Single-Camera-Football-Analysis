"""
@file action_spotting.py
@description Adapter: run a SoccerNet ball-action-spotting model on a match
  video and write normalized raw events (label + position_ms + confidence).

  Reuses the model code from an action-spotting checkout (lRomul/
  ball-action-spotting or its 2024 fork) rather than re-implementing it. The
  video is prepared to the model's input resolution/fps first. Run inside that
  repo's environment:

    python scripts/action_spotting.py --repo /path/to/ball-action-spotting \
      --experiment sampling_weights_001 --video match.mp4 --out raw_events.json \
      --prepare

@status Written against the repo's predict.py; not executed here (needs GPU).
@issues None
@todo None
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import torch

INDEX_SAVE_ZONE = 1
TTA = True


def parse_args():
    parser = argparse.ArgumentParser(description="Action spotting -> raw events")
    parser.add_argument("--repo", required=True,
                        help="path to the ball-action-spotting checkout")
    parser.add_argument("--experiment", required=True,
                        help="experiment name under data/ball_action/experiments")
    parser.add_argument("--video", required=True, help="match video")
    parser.add_argument("--out", required=True, help="output raw events JSON")
    parser.add_argument("--fold", type=int, default=0)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--prepare", action="store_true",
                        help="resize to 1280x736 and resample to 25fps first")
    return parser.parse_args()


def import_repo(repo: str):
    """Add the action-spotting checkout to sys.path; return its symbols."""
    sys.path.insert(0, repo)
    from src.predictors import MultiDimStackerPredictor
    from src.ball_action import constants
    from src.ball_action.annotations import raw_predictions_to_actions
    from src.utils import get_best_model_path
    return MultiDimStackerPredictor, constants, raw_predictions_to_actions, get_best_model_path


def prepare_video(video_path: Path, out_path: Path, fps: float = 25.0,
                  height: int = 736) -> Path:
    """Resize/resample the video with ffmpeg to the model's expected format."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required for --prepare; install it first.")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path),
         "-vf", f"scale=-2:{height},fps={fps}",
         "-c:v", "libx264", "-preset", "fast", str(out_path)],
        check=True, capture_output=True,
    )
    return out_path


def get_raw_predictions(predictor, video_path: Path, frame_count: int):
    """Fetch frames with OpenCV and collect per-frame predictions."""
    indexes_generator = predictor.indexes_generator
    min_index = indexes_generator.clip_index(0, frame_count, INDEX_SAVE_ZONE)
    max_index = indexes_generator.clip_index(frame_count, frame_count, INDEX_SAVE_ZONE)
    frame_index2prediction = {}
    predictor.reset_buffers()
    capture = cv2.VideoCapture(str(video_path))
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        grayscale = torch.from_numpy(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        prediction, predict_index = predictor.predict(grayscale, index)
        if predict_index >= min_index and prediction is not None:
            frame_index2prediction[predict_index] = prediction.cpu().numpy()
        index += 1
        if predict_index == max_index:
            break
    capture.release()
    predictor.reset_buffers()
    frame_indexes = sorted(frame_index2prediction)
    raw_predictions = np.stack([frame_index2prediction[i] for i in frame_indexes])
    return frame_indexes, raw_predictions


def to_raw_events(frame_indexes, raw_predictions, raw_predictions_to_actions,
                  video_fps: float) -> list[dict]:
    """Post-process predictions and convert to normalized event dicts."""
    class2actions = raw_predictions_to_actions(frame_indexes, raw_predictions)
    events = []
    for label, (action_indexes, confidences) in class2actions.items():
        for frame_index, confidence in zip(action_indexes, confidences):
            events.append({
                "label": label,
                "position_ms": round(frame_index / video_fps * 1000),
                "confidence": float(confidence),
            })
    events.sort(key=lambda event: event["position_ms"])
    return events


def main():
    args = parse_args()
    (MultiDimStackerPredictor, constants, raw_predictions_to_actions,
     get_best_model_path) = import_repo(args.repo)
    video_path = Path(args.video)
    if args.prepare:
        with tempfile.TemporaryDirectory() as tmp:
            video_path = prepare_video(video_path, Path(tmp) / "prepared.mp4")
            run_spotting(video_path, args, constants, MultiDimStackerPredictor,
                         raw_predictions_to_actions, get_best_model_path)
    else:
        run_spotting(video_path, args, constants, MultiDimStackerPredictor,
                     raw_predictions_to_actions, get_best_model_path)
    print(f"Wrote raw events to {args.out}")


def run_spotting(video_path, args, constants, MultiDimStackerPredictor,
                 raw_predictions_to_actions, get_best_model_path):
    capture = cv2.VideoCapture(str(video_path))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    capture.release()
    if abs(fps - constants.video_fps) > 0.1:
        raise RuntimeError(
            f"Video is {fps:.1f} fps; the model expects {constants.video_fps} fps. "
            "Pass --prepare to resample.")
    experiment_dir = constants.experiments_dir / args.experiment / f"fold_{args.fold}"
    model_path = get_best_model_path(experiment_dir)
    predictor = MultiDimStackerPredictor(model_path, device=args.device, tta=TTA)
    frame_indexes, raw = get_raw_predictions(predictor, video_path, frame_count)
    events = to_raw_events(frame_indexes, raw, raw_predictions_to_actions,
                           constants.video_fps)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump({"events": events}, handle, indent=2)


if __name__ == "__main__":
    main()
