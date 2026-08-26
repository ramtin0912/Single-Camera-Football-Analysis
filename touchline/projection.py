"""
@file projection.py
@description Map image pixels to pitch metres using the calibration homography.
  Uses the feet point (bottom centre) of a box, not the box centre, because the
  feet lie on the ground plane that the homography maps.

@status None
@issues None
@todo None
"""

import cv2
import numpy as np


def feet_point(box) -> np.ndarray:
    """Return the ground-contact point (bottom centre) of a detection box."""
    x1, y1, x2, y2 = box
    return np.array([(x1 + x2) / 2.0, float(y2)], dtype=np.float64)


def project_points(points_px, homography) -> np.ndarray:
    """Project pixel points to pitch metres via a 3x3 image->pitch homography."""
    points = np.asarray(points_px, dtype=np.float64).reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform(points, homography)
    return projected.reshape(-1, 2)
