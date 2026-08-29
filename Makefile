# Touchline — one-command setup and run (Linux/macOS; needs make + python3).
# Docker: build with the Dockerfile instead (see README section 1).
#
#   make setup                     # venv + deps + YOLO weights (core pipeline)
#   make setup-nbjw                # + NBJW repo + weights (enables --auto-calibrate)
#   make setup-events              # + ball-action-spotting repo (weights still manual)
#   make run VIDEO=match.mp4       # run the pipeline (auto-runs setup first)
#   make smoke-test                # verify the metric core without a video
#   make clean                     # remove venv, third-party clones and weights

PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

THIRD_PARTY := third_party
NBJW := $(THIRD_PARTY)/no-bells-just-whistles
ACTION := $(THIRD_PARTY)/ball-action-spotting

# NBJW single-view weights (v1.0.0 release assets — must keep these names).
NBJW_KP_URL := https://github.com/mguti97/No-Bells-Just-Whistles/releases/download/v1.0.0/SV_kp
NBJW_LINES_URL := https://github.com/mguti97/No-Bells-Just-Whistles/releases/download/v1.0.0/SV_lines

.PHONY: help setup setup-nbjw setup-events run smoke-test clean

help:
	@echo "Touchline targets:"
	@echo "  make setup               venv + deps + YOLO weights (core pipeline)"
	@echo "  make setup-nbjw          + NBJW repo + weights (auto calibration)"
	@echo "  make setup-events        + ball-action-spotting repo (weights manual)"
	@echo "  make run VIDEO=...       run the pipeline (auto-runs setup first)"
	@echo "  make smoke-test          verify the metric core without a video"
	@echo "  make clean               remove venv, third-party clones and weights"

# --- Core setup -----------------------------------------------------------------

setup: $(PY)
	$(PIP) install -r requirements.txt
	$(PY) -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"  # pre-fetch (cached)
	@echo ""
	@echo "Core setup complete. Run:"
	@echo "  make run VIDEO=path/to/match.mp4"
	@echo "Optional extras: make setup-nbjw (auto calibration), make setup-events (events)."

$(PY):
	$(PYTHON) -m venv $(VENV)

# --- Auto calibration: NBJW repo + weights -------------------------------------

setup-nbjw: $(NBJW)/inference.py $(NBJW)/SV_kp $(NBJW)/SV_lines
	@echo ""
	@echo "Auto calibration ready. Run:"
	@echo "  make run VIDEO=path/to/match.mp4 EXTRA=\"--auto-calibrate $(NBJW)\""

$(NBJW)/inference.py:
	mkdir -p $(THIRD_PARTY)
	git clone --depth 1 https://github.com/mguti97/no-bells-just-whistles $(NBJW)

$(NBJW)/SV_kp:
	curl -fL -o $(NBJW)/SV_kp $(NBJW_KP_URL)

$(NBJW)/SV_lines:
	curl -fL -o $(NBJW)/SV_lines $(NBJW_LINES_URL)

# --- Auto events: ball-action-spotting repo ------------------------------------

setup-events: $(ACTION)/src/predictors.py
	@echo ""
	@echo "Action-spotting repo cloned into $(ACTION)."
	@echo "Remaining manual step (weights are on Google Drive):"
	@echo "  1. Open the 'Trained models' link in $(ACTION)/README.md"
	@echo "  2. Unpack it so $(ACTION)/data/ball_action/experiments/sampling_weights_001/ exists"
	@echo "  3. Symlink it to /workdir, install timm kornia pytorch-argus scipy into"
	@echo "     the venv, then follow README section 3 (native path)."

$(ACTION)/src/predictors.py:
	mkdir -p $(THIRD_PARTY)
	git clone --depth 1 https://github.com/lRomul/ball-action-spotting $(ACTION)

# --- Run / test ----------------------------------------------------------------

OUT ?= output

run: setup
	$(PY) -m touchline $(VIDEO) --out $(OUT) $(EXTRA)

smoke-test: setup
	$(PY) scripts/smoke_test.py

clean:
	rm -rf $(VENV) $(THIRD_PARTY) yolov8n.pt
	@echo "Removed $(VENV), $(THIRD_PARTY) and downloaded weights."
