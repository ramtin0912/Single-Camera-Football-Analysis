"""
@file pipeline.py
@description Orchestrates the full analysis: read video, calibrate, detect,
  assign teams, track, compute metrics, and write the report.

@status None
@issues None
@todo None
"""

from pathlib import Path

from . import (calibration, config, detection, projection, team_assignment,
               tracking, video_io)
from .metrics import distance_speed, events, heatmaps, possession, territory
from .records import FrameRecord, PlayerRecord


class AnalysisPipeline:
    """Runs the end-to-end match analysis and writes the report."""

    def __init__(self, video_path: str, out_dir: str,
                 model_name: str = config.DEFAULT_MODEL,
                 frame_step: int = config.DEFAULT_FRAME_STEP,
                 calibration_path: str | None = None,
                 include_events: bool = False):
        self.video_path = video_path
        self.out_dir = Path(out_dir)
        self.model_name = model_name
        self.frame_step = frame_step
        self.calibration_path = calibration_path
        self.include_events = include_events

    def run(self) -> dict:
        """Run the pipeline and return the metrics dict written to disk."""
        video = video_io.MatchVideo(self.video_path)
        fps = video.fps
        homography = self._resolve_calibration(video)
        detector = detection.Detector(self.model_name)
        frame_records, colour_features = self._process_frames(
            video, detector, homography)
        video.release()
        centroids = team_assignment.compute_team_centroids(colour_features)
        self._assign_teams(frame_records, centroids)
        metrics = self._compute_metrics(fps, frame_records)
        heatmap_paths = self._write_heatmaps(frame_records)
        report_paths = self._write_report(metrics, heatmap_paths)
        metrics["report_paths"] = report_paths
        return metrics

    def _resolve_calibration(self, video):
        if self.calibration_path and Path(self.calibration_path).exists():
            return calibration.load_calibration(self.calibration_path)
        frame = video.read_frame(0)
        clicks = calibration.collect_calibration_clicks(frame)
        homography = calibration.compute_homography(clicks)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        calibration.save_calibration(str(self.out_dir / "calibration.json"),
                                     homography)
        return homography

    def _process_frames(self, video, detector, homography):
        frame_records = []
        colour_features = []
        tracker = tracking.TrackletTracker()
        for frame_index, frame in video.frames(step=self.frame_step):
            players, player_boxes, ball = self._detect_players_and_ball(
                frame, detector, homography, colour_features)
            track_ids = tracker.update(player_boxes, frame_index)
            for player, track_id in zip(players, track_ids):
                player.track_id = track_id
            frame_records.append(FrameRecord(frame_index=frame_index,
                                             ball=ball, players=players))
        return frame_records, colour_features

    def _detect_players_and_ball(self, frame, detector, homography,
                                 colour_features):
        players = []
        player_boxes = []
        ball = None
        ball_confidence = -1.0
        for detection in detector.detect(frame):
            point = projection.project_points(
                projection.feet_point(detection.box), homography)[0]
            if detection.is_person:
                feature = team_assignment.colour_feature(
                    team_assignment.torso_crop(frame, detection.box))
                if len(colour_features) < config.TEAM_COLOUR_SAMPLE_LIMIT:
                    colour_features.append(feature)
                players.append(PlayerRecord(x=float(point[0]), y=float(point[1]),
                                            colour_ab=tuple(feature)))
                player_boxes.append(detection.box)
            elif detection.is_ball and detection.confidence > ball_confidence:
                ball_confidence = detection.confidence
                ball = (float(point[0]), float(point[1]))
        return players, player_boxes, ball

    def _assign_teams(self, frame_records, centroids) -> None:
        for record in frame_records:
            for player in record.players:
                player.team_id = team_assignment.assign_team(
                    player.colour_ab, centroids)

    def _compute_metrics(self, fps: float, frame_records) -> dict:
        detected_events = events.detect_events(frame_records, fps) \
            if self.include_events else {"events": []}
        return {
            "video": {
                "path": self.video_path,
                "fps": round(fps, 2),
                "frames_processed": len(frame_records),
                "frame_step": self.frame_step,
            },
            "territory": territory.compute_territory(frame_records),
            "possession": possession.compute_possession(frame_records),
            "distance": distance_speed.compute_distance_speed(frame_records, fps),
            "events": detected_events,
        }

    def _write_heatmaps(self, frame_records) -> dict:
        paths = {}
        for team_id in (0, 1):
            histogram = heatmaps.compute_team_heatmap(frame_records, team_id)
            path = self.out_dir / f"heatmap_team_{team_id}.png"
            heatmaps.render_heatmap_png(histogram, str(path))
            paths[f"team_{team_id}"] = str(path)
        return paths

    def _write_report(self, metrics, heatmap_paths) -> dict:
        from . import report
        return report.write_report(self.out_dir, metrics, heatmap_paths)
