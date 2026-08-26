"""
@file metrics/heatmaps.py
@description Per-team position heatmaps: a 2D histogram of player positions,
  rendered as a colour PNG blended over the pitch drawing.

@status None
@issues None
@todo None
"""

import cv2
import numpy as np

from .. import config
from .. import pitch


def compute_team_heatmap(frame_records, team_id: int,
                         cell_m: float = config.HEATMAP_CELL_M) -> np.ndarray:
    """Return a 2D histogram (rows=y, cols=x) of one team's player positions."""
    rows, cols = _grid_shape(cell_m)
    points = [(player.x, player.y) for record in frame_records
              for player in record.players if player.team_id == team_id]
    if not points:
        return np.zeros((rows, cols), dtype=np.float64)
    points = np.array(points, dtype=np.float64)
    histogram, _, _ = np.histogram2d(
        points[:, 1], points[:, 0], bins=[rows, cols],
        range=[[-config.PITCH_WIDTH_M / 2, config.PITCH_WIDTH_M / 2],
               [-config.PITCH_LENGTH_M / 2, config.PITCH_LENGTH_M / 2]],
    )
    return histogram


def render_heatmap_png(histogram: np.ndarray, out_path: str) -> None:
    """Write a colour heatmap blended over the pitch drawing."""
    rows, cols = histogram.shape[:2]
    # Row 0 is the near touchline; images put row 0 at the top, so flip.
    display = np.flipud(histogram)
    canvas = pitch.draw_pitch_canvas(cols, rows)
    colour = cv2.applyColorMap(_normalize(display), cv2.COLORMAP_INFERNO)
    blended = cv2.addWeighted(colour, 0.7, canvas, 0.6, 0)
    cv2.imwrite(out_path, blended)


def _normalize(histogram: np.ndarray) -> np.ndarray:
    """Scale a histogram to uint8 0..255 for colour mapping."""
    peak = histogram.max() if histogram.size else 0.0
    if peak <= 0:
        return np.zeros(histogram.shape, dtype=np.uint8)
    return (histogram / peak * 255.0).astype(np.uint8)


def _grid_shape(cell_m: float) -> tuple[int, int]:
    rows = max(1, int(round(config.PITCH_WIDTH_M / cell_m)))
    cols = max(1, int(round(config.PITCH_LENGTH_M / cell_m)))
    return rows, cols
