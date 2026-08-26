"""
@file pitch.py
@description Pitch geometry: named landmark coordinates (origin at centre, in
  metres) plus a pitch drawing canvas for heatmap overlays.

@status None
@issues None
@todo None
"""

import cv2
import numpy as np

from . import config

# Pitch line dimensions (metres, FIFA)
PENALTY_AREA_DEPTH_M = 16.5
PENALTY_AREA_HALF_WIDTH_M = 20.16
GOAL_AREA_DEPTH_M = 5.5
GOAL_AREA_HALF_WIDTH_M = 9.16
PENALTY_SPOT_DISTANCE_M = 11.0
CENTRE_CIRCLE_RADIUS_M = 9.15

PITCH_LINE_COLOUR = (255, 255, 255)
PITCH_GRASS_COLOUR = (34, 74, 36)


def build_landmarks(length_m=config.PITCH_LENGTH_M, width_m=config.PITCH_WIDTH_M):
    """Return named landmark coordinates in metres, origin at centre.

    Convention: x runs along the pitch length (left -> right in the image),
    y runs across the width. The near touchline is y = -width/2 (bottom of the
    image, camera side); the far touchline is y = +width/2 (top of the image).
    """
    half_l, half_w = length_m / 2.0, width_m / 2.0
    return {
        "near_left_corner": (-half_l, -half_w),
        "near_right_corner": (half_l, -half_w),
        "far_right_corner": (half_l, half_w),
        "far_left_corner": (-half_l, half_w),
        "near_halfway": (0.0, -half_w),
        "far_halfway": (0.0, half_w),
        "centre_spot": (0.0, 0.0),
        "left_penalty_spot": (-half_l + PENALTY_SPOT_DISTANCE_M, 0.0),
        "right_penalty_spot": (half_l - PENALTY_SPOT_DISTANCE_M, 0.0),
    }


def draw_pitch_canvas(width_px, height_px):
    """Return a BGR canvas (width_px x height_px) with white pitch lines.

    Near touchline is drawn at the bottom of the image, far at the top, matching
    the landmark convention used by `build_landmarks`.
    """
    canvas = np.full((height_px, width_px, 3), PITCH_GRASS_COLOUR, dtype=np.uint8)
    half_l = config.PITCH_LENGTH_M / 2.0
    half_w = config.PITCH_WIDTH_M / 2.0

    def to_px(x, y):
        px = int(round((x + half_l) / (2 * half_l) * width_px))
        py = int(round((half_w - y) / (2 * half_w) * height_px))
        return px, py

    def line(x1, y1, x2, y2, thickness=2):
        cv2.line(canvas, to_px(x1, y1), to_px(x2, y2),
                 PITCH_LINE_COLOUR, thickness)

    def circle(centre, radius_m, thickness=2):
        cv2.circle(canvas, to_px(*centre),
                   int(round(radius_m / (2 * half_w) * height_px)),
                   PITCH_LINE_COLOUR, thickness)

    # Boundary, halfway line, centre circle and spot
    line(-half_l, -half_w, half_l, -half_w)
    line(-half_l, half_w, half_l, half_w)
    line(-half_l, -half_w, -half_l, half_w)
    line(half_l, -half_w, half_l, half_w)
    line(0, -half_w, 0, half_w)
    circle((0, 0), CENTRE_CIRCLE_RADIUS_M)
    cv2.circle(canvas, to_px(0, 0), 3, PITCH_LINE_COLOUR, -1)

    # Penalty and goal areas, penalty spots
    for side in (-1, 1):
        goal_x = side * half_l
        penalty_near_x = goal_x - side * PENALTY_AREA_DEPTH_M
        goal_near_x = goal_x - side * GOAL_AREA_DEPTH_M
        _draw_box_lines(canvas, to_px, goal_x, penalty_near_x,
                        PENALTY_AREA_HALF_WIDTH_M)
        _draw_box_lines(canvas, to_px, goal_x, goal_near_x,
                        GOAL_AREA_HALF_WIDTH_M)
        cv2.circle(canvas, to_px(goal_x - side * PENALTY_SPOT_DISTANCE_M, 0),
                   3, PITCH_LINE_COLOUR, -1)
    return canvas


def _draw_box_lines(canvas, to_px, goal_x, near_x, half_width):
    """Draw the three visible edges of a goal/penalty box for one end."""
    cv2.line(canvas, to_px(goal_x, -half_width), to_px(near_x, -half_width),
             PITCH_LINE_COLOUR, 2)
    cv2.line(canvas, to_px(goal_x, half_width), to_px(near_x, half_width),
             PITCH_LINE_COLOUR, 2)
    cv2.line(canvas, to_px(near_x, -half_width), to_px(near_x, half_width),
             PITCH_LINE_COLOUR, 2)
