"""
@file __main__.py
@description Command-line entry point: python -m touchline VIDEO --out DIR.

@status None
@issues None
@todo None
"""

import argparse
import sys

from . import config, pipeline


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="touchline",
        description="Analyse sideline football footage into simple match data.")
    parser.add_argument("video", help="path to the match video")
    parser.add_argument("--out", default="output", help="output directory")
    parser.add_argument("--model", default=config.DEFAULT_MODEL,
                        help="YOLO model name")
    parser.add_argument("--frame-step", type=int, default=config.DEFAULT_FRAME_STEP,
                        help="process every Nth frame")
    parser.add_argument("--calibration", help="reuse a saved calibration.json")
    parser.add_argument("--auto-calibrate", metavar="NBJW_REPO",
                        help="auto-calibrate using the No Bells, Just Whistles "
                             "checkout at this path")
    parser.add_argument("--include-events", action="store_true",
                        help="include event detection (not yet implemented)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Run the pipeline from parsed command-line arguments."""
    args = _parse_args(argv)
    runner = pipeline.AnalysisPipeline(
        video_path=args.video,
        out_dir=args.out,
        model_name=args.model,
        frame_step=args.frame_step,
        calibration_path=args.calibration,
        auto_calibration_repo=args.auto_calibrate,
        include_events=args.include_events,
    )
    runner.run()
    print(f"Report written to {args.out}/report.json and {args.out}/report.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
