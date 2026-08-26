"""
@file calibration.py
@description Pitch calibration: compute the image->pitch homography. The
  primary path is open-source auto-calibration (No Bells, Just Whistles); a
  manual 4+ point click remains as a fallback. Homographies cache to JSON.

@status Auto-calibration adapter scaffolded; manual path fully working.
@issues NBJW homography output parsing is not finalised.
@todo
  - [ ] Finalise NBJW homography extraction (see auto_calibrate).
"""

import json
from pathlib import Path

import cv2
import numpy as np

from . import pitch

# Fixed click order. The first four (pitch corners) are required; the rest are
# optional and improve the fit. Press q to finish once the four are set.
CLICK_ORDER = [
    "near_left_corner",
    "near_right_corner",
    "far_right_corner",
    "far_left_corner",
    "centre_spot",
    "left_penalty_spot",
    "right_penalty_spot",
]
REQUIRED_CLICKS = 4
CLICK_COLOUR = (0, 200, 255)


def collect_calibration_clicks(frame) -> dict:
    """Interactively collect landmark pixel points from a still frame."""
    clicks = {}
    window_name = "Touchline calibration"

    def on_click(event, x, y, _flags, _param):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < len(CLICK_ORDER):
            name = CLICK_ORDER[len(clicks)]
            clicks[name] = (float(x), float(y))
            print(f"  clicked {name} at ({x}, {y})")

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, on_click)
    _print_instructions()

    while True:
        display = frame.copy()
        _draw_clicks(display, clicks)
        cv2.imshow(window_name, display)
        key = cv2.waitKey(20) & 0xFF
        if key == ord("q") and len(clicks) >= REQUIRED_CLICKS:
            break
        if key == 27:  # Esc aborts calibration
            cv2.destroyAllWindows()
            raise RuntimeError("Calibration cancelled.")
    cv2.destroyAllWindows()
    return clicks


def _print_instructions() -> None:
    print("Click landmarks in this order (near = camera side, bottom of image):")
    for index, name in enumerate(CLICK_ORDER):
        tag = "REQUIRED" if index < REQUIRED_CLICKS else "optional"
        print(f"  {index + 1}. {name}  [{tag}]")
    print("Press q to finish once the four required corners are set.")


def _draw_clicks(display, clicks) -> None:
    for name, point in clicks.items():
        x, y = int(point[0]), int(point[1])
        cv2.circle(display, (x, y), 6, CLICK_COLOUR, -1)
        cv2.putText(display, name, (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, CLICK_COLOUR, 1)


def compute_homography(clicks: dict) -> np.ndarray:
    """Fit the image->pitch homography from clicked landmarks."""
    landmarks = pitch.build_landmarks()
    image_points = np.array([clicks[name] for name in clicks], dtype=np.float64)
    pitch_points = np.array([landmarks[name] for name in clicks], dtype=np.float64)
    if len(image_points) < REQUIRED_CLICKS:
        raise ValueError("At least 4 landmarks are required for calibration.")
    homography, _ = cv2.findHomography(image_points, pitch_points, cv2.RANSAC)
    if homography is None:
        raise RuntimeError("Could not fit a homography from the clicked points.")
    return homography


def auto_calibrate(frame, nbjw_repo_path: str) -> np.ndarray:
    """Calibrate automatically using No Bells, Just Whistles (NBJW).

    NBJW (https://github.com/mguti97/no-bells-just-whistles) estimates the
    pitch homography from a single frame using field keypoints + lines, then
    DLT. It ships single-view weights (SV_kp, SV_lines).

    This is a scaffold: it validates the NBJW checkout and points at the exact
    integration step that remains (extracting the homography it produces). See
    `_config/integrations.md` for setup.
    """
    repo = Path(nbjw_repo_path)
    if not (repo / "inference.py").exists():
        raise FileNotFoundError(
            f"NBJW not found at {nbjw_repo_path}. Clone it and download the "
            "SV_kp / SV_lines weights — see _config/integrations.md.")
    # Integration point: run NBJW inference.py on `frame` (its documented CLI:
    # python inference.py --weights_kp SV_kp --weights_line SV_lines
    #   --input_path <frame> --input_type image --save_path <out>),
    # then convert its estimated homography into our image->pitch matrix.
    raise NotImplementedError(
        "NBJW auto-calibration is scaffolded but its homography output is not "
        "yet parsed. Use manual calibration for now, or finalise "
        "touchline/calibration.py:auto_calibrate.")


def save_calibration(path: str, homography: np.ndarray) -> None:
    """Write the homography to JSON so re-runs do not re-click."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"homography": homography.tolist()}, handle)


def load_calibration(path: str) -> np.ndarray:
    """Load a previously saved homography."""
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return np.array(data["homography"], dtype=np.float64)
