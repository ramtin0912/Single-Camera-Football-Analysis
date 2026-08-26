"""
@file team_assignment.py
@description Split players into two teams by jersey colour: Lab (a, b) k-means.
  No identity — only team 0 vs team 1.

@status None
@issues A referee (black/yellow kit) can be absorbed by a colour cluster.
@todo Filter obvious referee colours later if it skews results.
"""

import cv2
import numpy as np

from . import config


def torso_crop(frame, box, fraction: float = config.TEAM_CROP_FRACTION):
    """Crop the lower `fraction` of a box (torso, below the head)."""
    x1, y1, x2, y2 = [int(value) for value in box]
    top = int(y1 + (y2 - y1) * (1.0 - fraction))
    return frame[top:y2, x1:x2]


def colour_feature(crop) -> np.ndarray:
    """Return the mean Lab (a, b) of a crop; luminance is ignored."""
    if crop.size == 0:
        return np.zeros(2, dtype=np.float64)
    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2Lab).reshape(-1, 3).astype(np.float64)
    return lab[:, 1:].mean(axis=0)


def compute_team_centroids(colour_features) -> np.ndarray:
    """Cluster sampled (a, b) features into two sorted colour centroids."""
    features = np.asarray(colour_features, dtype=np.float32).reshape(-1, 2)
    if len(features) < 2:
        raise ValueError("Need at least two player crops to split teams.")
    _, _, centroids = cv2.kmeans(
        features, 2, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
        3, cv2.KMEANS_PP_CENTERS,
    )
    # Sort by the a-channel so team ids are stable across runs.
    return centroids[np.argsort(centroids[:, 0])]


def assign_team(colour_feature_value, centroids) -> int:
    """Assign a player's (a, b) feature to the nearest centroid (0 or 1)."""
    feature = np.asarray(colour_feature_value, dtype=np.float32).reshape(2)
    distances = np.linalg.norm(centroids - feature, axis=1)
    return int(np.argmin(distances))
