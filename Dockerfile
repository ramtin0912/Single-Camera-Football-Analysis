# Touchline — Docker image (Debian bookworm, Python 3.11).
#
# Core image mirrors the development environment this project is verified
# against: Debian 12 + Python 3.11 + OpenCV/Ultralytics in a .venv, with the
# two system libraries OpenCV needs (libgl1, libglib2.0-0) that slim/headless
# images lack.
#
# Build:
#   docker build -t touchline .
#
# Run (mount your video + a writable output dir):
#   docker run --rm \
#     -v "$PWD/sample.mp4:/videos/match.mp4:ro" \
#     -v "$PWD/output:/app/output" \
#     touchline /videos/match.mp4 --out /app/output
#
# Headless calibration note: there is no click GUI inside the container. Pass
# `--calibration /path/to/calibration.json` or `--auto-calibrate /path/to/nbjw`
# (see the README). A saved calibration is produced by any earlier run or by
# the manual calibration on a machine with a display.
#
# Events image (auto action spotting — needs an NVIDIA GPU at runtime):
#   docker build --build-arg WITH_EVENTS=1 -t touchline:events .
#   docker run --rm --gpus all \
#     -v "$PWD/match.mp4:/videos/match.mp4:ro" \
#     -v "$PWD/output:/app/output" \
#     -v "$PWD/weights:/workdir/data/ball_action/experiments:ro" \
#     touchline:events /videos/match.mp4 --out /app/output \
#       --include-events --action-spotting-repo /workdir --action-spotting-prepare
#
#   (weights = manual Google Drive download, see the README — the model code
#   hardcodes its data under /workdir, so the repo lives there and the weights
#   are mounted into /workdir/data/ball_action/experiments.)
#
# All-features image (auto calibration + events; events needs an NVIDIA GPU):
#   docker build --build-arg WITH_NBJW=1 --build-arg WITH_EVENTS=1 -t touchline:all .
#   docker run --rm --gpus all \
#     -v "$PWD/match.mp4:/videos/match.mp4:ro" \
#     -v "$PWD/output:/app/output" \
#     -v "$PWD/weights:/workdir/data/ball_action/experiments:ro" \
#     touchline:all /videos/match.mp4 --out /app/output \
#       --auto-calibrate /nbjw \
#       --include-events --action-spotting-repo /workdir --action-spotting-prepare
#
# CPU-only torch (smaller image, no CUDA wheels):
#   docker build --build-arg TORCH_INDEX=https://download.pytorch.org/whl/cpu -t touchline .

FROM python:3.11-slim-bookworm

ARG TORCH_INDEX=
ARG WITH_EVENTS=0
ARG WITH_NBJW=0

WORKDIR /app

# OpenCV needs libGL + libglib at runtime (classic slim-image ImportError:
# "libGL.so.1: cannot open shared object file"). Installed before any Python
# deps so pip installs land in one layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# ultralytics auto-installs `lap` (ByteTrack dep) at first import and then
# requires a restart — preinstall it so the first run "just works".
RUN python -m venv .venv \
    && if [ -n "$TORCH_INDEX" ]; then \
         .venv/bin/pip install --index-url "$TORCH_INDEX" torch torchvision; \
       fi \
    && .venv/bin/pip install -r requirements.txt \
    && .venv/bin/pip install --no-cache-dir lap>=0.5.12

COPY touchline ./touchline
COPY scripts ./scripts

# Optional events layer (WITH_EVENTS=1): action spotting needs an NVIDIA GPU
# at runtime. Adds ffmpeg (for --action-spotting-prepare), the
# lRomul/ball-action-spotting checkout at /workdir (its code hardcodes that
# path for its data), the model's Python deps in the same .venv, and a
# pre-fetched timm backbone. The trained weights stay a manual Google Drive
# download, mounted at runtime:
#   -v "$PWD/weights:/workdir/data/ball_action/experiments:ro"
RUN if [ "$WITH_EVENTS" = "1" ]; then \
      apt-get update \
        && apt-get install -y --no-install-recommends ffmpeg \
        && rm -rf /var/lib/apt/lists/* \
        && git clone --depth 1 https://github.com/lRomul/ball-action-spotting /workdir \
        && .venv/bin/pip install --no-cache-dir timm kornia pytorch-argus scipy \
        && .venv/bin/python -c "import timm; timm.create_model('tf_efficientnetv2_b0.in1k', pretrained=True)" \
        && .venv/bin/python -c "import sys; sys.path.insert(0, '/workdir'); \
             from src.predictors import MultiDimStackerPredictor; \
             from src.ball_action import constants; \
             from src.ball_action.annotations import raw_predictions_to_actions; \
             from src.utils import get_best_model_path; \
             print('action-spotting imports OK');" \
    ; fi

# Optional auto-calibration layer (WITH_NBJW=1): adds the No Bells, Just
# Whistles checkout at /nbjw with its two weights (SV_kp, SV_lines, ~265 MB
# each from GitHub Releases — scriptable, unlike the events weights). No new
# Python deps: torch/torchvision/yaml/Pillow/matplotlib/tqdm all come from the
# core install. Use with --auto-calibrate /nbjw.
RUN if [ "$WITH_NBJW" = "1" ]; then \
      git clone --depth 1 https://github.com/mguti97/no-bells-just-whistles /nbjw \
        && curl -fL -o /nbjw/SV_kp https://github.com/mguti97/No-Bells-Just-Whistles/releases/download/v1.0.0/SV_kp \
        && curl -fL -o /nbjw/SV_lines https://github.com/mguti97/No-Bells-Just-Whistles/releases/download/v1.0.0/SV_lines \
        && .venv/bin/python -c "import sys; sys.path.insert(0, '/nbjw'); \
             from model.cls_hrnet import get_cls_net; \
             from model.cls_hrnet_l import get_cls_net as get_cls_net_l; \
             from utils.utils_calib import FramebyFrameCalib; \
             print('NBJW imports OK');" \
    ; fi

# Pre-download YOLOv8n weights so the first run is instant.
RUN .venv/bin/python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Build gate: the metric-core smoke test must pass inside the image.
RUN .venv/bin/python scripts/smoke_test.py

VOLUME /app/output
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/app/.venv/bin/python", "-m", "touchline"]
CMD ["--help"]