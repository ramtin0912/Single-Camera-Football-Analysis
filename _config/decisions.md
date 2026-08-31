# Decisions & Rationale

One line per decision, so future changes are deliberate.

1. **Open-source-first.** "No complex models" means "don't invent our own" —
   adopt published, purpose-built tools (SoccerNet, Ultralytics YOLO + ByteTrack,
   No Bells Just Whistles) instead of building models, trackers, or event
   detectors from scratch. We only write the glue around them.
2. **Python, not JS/TS.** CV ecosystem (OpenCV, YOLO) is Python-native. A desktop
   app can later call this pipeline as a subprocess or embed it.
3. **Auto calibration (NBJW) is the primary path; manual click is the fallback.**
   NBJW estimates the pitch homography from a single frame. Manual 4+ point
   clicking remains for when the auto path is unavailable or the camera view is
   outside NBJW's training distribution.
4. **YOLOv8n (nano) as the detector.** Small, fast, and COCO already has a
   "sports ball" class. Fine-tuning on football images is a later upgrade, not a
   prerequisite.
5. **ByteTrack (via ultralytics) for tracking.** Purpose-built, open source, and
   better at occlusion than a hand-rolled IoU tracker. No custom tracker code.
6. **Jersey colour k-means for teams, not identity.** Two colour clusters split
   teams cheaply and reliably. It does not identify *who* a player is — that
   (jersey numbers) is out of scope.
7. **SoccerNet action spotting for events, not hand-rolled heuristics.** Pretrained
   models (lRomul/ball-action-spotting or sn-spotting) detect passes, shots,
   goals, etc. Heuristics are only a comparison baseline.
8. **Metrics are pure functions.** They consume plain records so the desktop app
   and tests can reuse them without the video stack.
9. **JSON is the source of truth; HTML is a view.** The report.json is the stable
   contract a future app consumes; report.html is for immediate human reading.
10. **Origin at pitch centre, x along length, metres.** Thirds fall out as simple
    x-bands; attacking direction is handled later (per-half), not baked in now.
11. **No implicit persistence.** Calibration/report writes only happen because the
    user ran the pipeline, never in the background.
12. **Auto-calibration tries several frames, gated by a plausibility check.** NBJW
    single-frame fits can be degenerate; the pipeline samples frames across the
    video and uses the first frame whose homography maps the pitch corners near
    the frame (finite, bounded, convex). `--calibration-frame N` forces a frame.
