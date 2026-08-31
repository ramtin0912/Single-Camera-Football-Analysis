"""
@file nbjw_homography.py
@description Adapter: run No Bells, Just Whistles (NBJW) single-image pitch
  calibration and write a Touchline-format image->pitch homography JSON.

  Reuses NBJW's own modules (imported from --nbjw-repo) rather than
  re-implementing its model. Run inside the NBJW environment:

    python scripts/nbjw_homography.py --nbjw-repo /path/to/NBJW \
      --weights_kp SV_kp --weights_line SV_lines \
      --input frame.png --out calibration.json

@status Verified end-to-end on CPU against the v1.0.0 checkout + weights
  (SV_kp / SV_lines); writes a Touchline-format homography.
@issues NBJW's single-frame calibration is only as good as its keypoint/line
  detections on that frame — sparse detections yield degenerate homographies.
@todo None
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torchvision.transforms as T
import torchvision.transforms.functional as F
import yaml
from PIL import Image

# The four pitch corners in SoccerNet's centred world frame (length, width).
CORNER_WORLD = np.array([[-52.5, -34.0], [52.5, -34.0], [52.5, 34.0], [-52.5, 34.0]])

# The same corners in Touchline's image-relative convention: near = bottom of
# the image, far = top, left/right = image left/right.
CORNER_PITCH = np.array([[-52.5, -34.0], [52.5, -34.0], [52.5, 34.0], [-52.5, 34.0]])

MODEL_INPUT_WIDTH = 960
MODEL_INPUT_HEIGHT = 540


def parse_args():
    parser = argparse.ArgumentParser(description="NBJW -> Touchline homography")
    parser.add_argument("--nbjw-repo", required=True,
                        help="path to the No Bells, Just Whistles checkout")
    parser.add_argument("--weights_kp", required=True)
    parser.add_argument("--weights_line", required=True)
    parser.add_argument("--input", required=True, help="single frame image")
    parser.add_argument("--out", required=True, help="output calibration JSON")
    parser.add_argument("--device", default="auto",
                        help="torch device (auto = cuda if available)")
    parser.add_argument("--kp_threshold", type=float, default=0.1486)
    parser.add_argument("--line_threshold", type=float, default=0.3880)
    return parser.parse_args()


def import_nbjw(repo: str):
    """Add the NBJW checkout to sys.path and return its helper symbols."""
    sys.path.insert(0, repo)
    from model.cls_hrnet import get_cls_net
    from model.cls_hrnet_l import get_cls_net as get_cls_net_l
    from utils.utils_calib import FramebyFrameCalib
    from utils.utils_heatmap import (complete_keypoints, coords_to_dict,
                                     get_keypoints_from_heatmap_batch_maxpool,
                                     get_keypoints_from_heatmap_batch_maxpool_l)
    return (get_cls_net, get_cls_net_l, FramebyFrameCalib,
            get_keypoints_from_heatmap_batch_maxpool,
            get_keypoints_from_heatmap_batch_maxpool_l,
            complete_keypoints, coords_to_dict)


def build_models(repo, weights_kp, weights_line, device, get_cls_net, get_cls_net_l):
    """Load NBJW's keypoint and line models with their configs and weights."""
    cfg = yaml.safe_load(open(Path(repo) / "config" / "hrnetv2_w48.yaml"))
    cfg_l = yaml.safe_load(open(Path(repo) / "config" / "hrnetv2_w48_l.yaml"))
    model = get_cls_net(cfg)
    model.load_state_dict(torch.load(weights_kp, map_location=device))
    model.to(device)
    model.eval()
    model_l = get_cls_net_l(cfg_l)
    model_l.load_state_dict(torch.load(weights_line, map_location=device))
    model_l.to(device)
    model_l.eval()
    return model, model_l


def projection_from_cam_params(final_params_dict):
    """Replicates NBJW's projection_from_cam_params: 3x4 camera matrix P."""
    cam_params = final_params_dict["cam_params"]
    x_focal = cam_params["x_focal_length"]
    y_focal = cam_params["y_focal_length"]
    principal = np.array(cam_params["principal_point"])
    position = np.array(cam_params["position_meters"])
    rotation = np.array(cam_params["rotation_matrix"])
    translation = np.eye(4)[:-1]
    translation[:, -1] = -position
    intrinsic = np.array([[x_focal, 0, principal[0]],
                          [0, y_focal, principal[1]],
                          [0, 0, 1]])
    return intrinsic @ (rotation @ translation)


def run_inference(frame_bgr, cam, model, model_l, device, kp_threshold,
                  line_threshold, kp_func, line_func, coords_to_dict,
                  complete_keypoints):
    """Run NBJW inference on one BGR frame; return its calibration params."""
    tensor = _preprocess(frame_bgr).to(device)
    _, _, height, width = tensor.size()
    with torch.no_grad():
        heatmaps = model(tensor)
        heatmaps_l = model_l(tensor)
    kp_coords = kp_func(heatmaps[:, :-1])
    line_coords = line_func(heatmaps_l[:, :-1])
    kp_dict = coords_to_dict(kp_coords, threshold=kp_threshold)
    lines_dict = coords_to_dict(line_coords, threshold=line_threshold)
    final_dict = complete_keypoints(kp_dict, lines_dict, w=width, h=height,
                                    normalize=True)
    cam.update(final_dict[0])
    return cam.heuristic_voting()


def _preprocess(frame_bgr):
    """Convert a BGR frame to the (1, 3, 540, 960) tensor NBJW expects."""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    tensor = F.to_tensor(Image.fromarray(frame_rgb)).float().unsqueeze(0)
    if tensor.size()[-1] != MODEL_INPUT_WIDTH:
        tensor = T.Resize((MODEL_INPUT_HEIGHT, MODEL_INPUT_WIDTH))(tensor)
    return tensor


def world_to_image_homography(projection):
    """Drop the Z column of P to get the pitch(X, Y, 1) -> image homography."""
    homography = projection[:, [0, 1, 3]]
    return homography / homography[-1, -1]


def project_points(homography, points):
    """Project 2D points through a 3x3 homography."""
    reshaped = np.asarray(points, dtype=np.float64).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(reshaped, homography).reshape(-1, 2)


def fit_touchline_homography(h_world_to_image):
    """Re-orient NBJW's world->image homography to Touchline's image-relative
    convention (near = bottom, far = top) and return image->pitch."""
    pixels = project_points(h_world_to_image, CORNER_WORLD)
    near = pixels[np.argsort(pixels[:, 1])[-2:]]
    far = pixels[np.argsort(pixels[:, 1])[:2]]
    near_left, near_right = sorted(near, key=lambda point: point[0])
    far_left, far_right = sorted(far, key=lambda point: point[0])
    image_points = np.array([near_left, near_right, far_right, far_left],
                            dtype=np.float64)
    homography, _ = cv2.findHomography(image_points, CORNER_PITCH, cv2.RANSAC)
    if homography is None:
        raise RuntimeError("Could not fit Touchline homography from NBJW corners.")
    return homography


def resolve_device(device: str) -> str:
    """Map 'auto' to cuda when available, otherwise cpu."""
    if device != "auto":
        return device
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def main():
    args = parse_args()
    device = resolve_device(args.device)
    (get_cls_net, get_cls_net_l, FramebyFrameCalib, kp_func, line_func,
     complete_keypoints, coords_to_dict) = import_nbjw(args.nbjw_repo)
    model, model_l = build_models(args.nbjw_repo, args.weights_kp,
                                  args.weights_line, device,
                                  get_cls_net, get_cls_net_l)
    frame = cv2.imread(args.input)
    if frame is None:
        raise RuntimeError(f"Could not read image: {args.input}")
    cam = FramebyFrameCalib(iwidth=frame.shape[1], iheight=frame.shape[0],
                            denormalize=True)
    final_params = run_inference(frame, cam, model, model_l, device,
                                 args.kp_threshold, args.line_threshold,
                                 kp_func, line_func, coords_to_dict,
                                 complete_keypoints)
    if final_params is None:
        raise RuntimeError("NBJW did not produce a calibration for this frame.")
    projection = projection_from_cam_params(final_params)
    homography = fit_touchline_homography(world_to_image_homography(projection))
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump({"homography": homography.tolist()}, handle)
    print(f"Wrote Touchline homography to {args.out}")


if __name__ == "__main__":
    main()
