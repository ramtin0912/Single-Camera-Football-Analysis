# Decisions & Rationale

One line per decision, so future changes are deliberate.

1. **Python, not JS/TS.** CV ecosystem (OpenCV, YOLO) is Python-native. A desktop
   app can later call this pipeline as a subprocess or embed it.
2. **Manual calibration first, auto pitch detection later.** Clicking 4+ known
   pitch points is ~30 seconds and reliable. Auto-detecting the pitch from
   arbitrary sideline angles is a research problem — do it later, behind the same
   `calibration.py` interface.
3. **YOLOv8n (nano) as the detector.** Small, fast, runs on CPU acceptably, and
   COCO already has a "sports ball" class. Fine-tuning on football images is a
   later upgrade, not a prerequisite.
4. **Jersey colour k-means for teams, not identity.** Two colour clusters split
   teams cheaply and reliably. It does not identify *who* a player is — that
   (jersey numbers) is out of scope.
5. **Hand-written IoU tracker, not ByteTrack/SORT.** Team-level distance/speed
   tolerates some tracklet fragmentation, so a simple tracker is enough and keeps
   dependencies minimal. Swap for ByteTrack only if per-player accuracy is needed.
6. **Heuristic events, not models.** Shots/goals/corners are detected from ball
   trajectory + pitch zones with rules, matching "no complex models".
7. **Metrics are pure functions.** They consume plain records so the desktop app
   and tests can reuse them without the video stack.
8. **JSON is the source of truth; HTML is a view.** The report.json is the stable
   contract a future app consumes; report.html is for immediate human reading.
9. **Origin at pitch centre, x along length, metres.** Thirds fall out as simple
   x-bands; attacking direction is handled later (per-half), not baked in now.
10. **No implicit persistence.** Calibration/report writes only happen because the
    user ran the pipeline, never in the background.
