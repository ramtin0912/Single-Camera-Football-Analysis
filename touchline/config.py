"""
@file config.py
@description Central constants for Touchline: pitch dimensions, detection
  classes, thresholds, and defaults. No magic numbers anywhere else.

@status None
@issues None
@todo None
"""

# Pitch dimensions (FIFA standard, metres)
PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0

# YOLO COCO class IDs we care about
PERSON_CLASS_ID = 0
SPORTS_BALL_CLASS_ID = 32

# Detection
DEFAULT_MODEL = "yolov8n.pt"
DEFAULT_CONFIDENCE = 0.25

# Pipeline
DEFAULT_FRAME_STEP = 2

# Team assignment (jersey colour)
TEAM_COLOUR_SAMPLE_LIMIT = 200   # max player crops sampled for k-means
TEAM_CROP_FRACTION = 0.5         # lower half of a box = torso, below the head

# Possession
POSSESSION_RADIUS_M = 3.0        # ball->player max distance to count possession

# Tracking
TRACK_MAX_GAP_FRAMES = 5
TRACK_MIN_IOU = 0.2

# Heatmaps
HEATMAP_CELL_M = 2.0             # grid cell size in metres
