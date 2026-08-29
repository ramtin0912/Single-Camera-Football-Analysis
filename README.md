# Touchline

Turn sideline phone footage of a football (soccer) match into simple analysis
data: territory %, possession %, team heatmaps, distance/speed, and events
(passes, shots, goals). Record a match → run one command → read the report.

Detection/tracking use Ultralytics YOLOv8 + ByteTrack, auto pitch calibration
uses No Bells Just Whistles (NBJW), and events use a SoccerNet action-spotting
model. Touchline only glues them together. Football means soccer (FIFA rules).

---

## Quick start — you only need Docker

No Python, no venv, no `make`. Windows: install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(with the WSL2 backend, the default). macOS/Linux: install Docker.

**1. Get the code**

```bash
git clone git@github.com:ramtin0912/Single-Camera-Football-Analysis.git
cd Single-Camera-Football-Analysis
```

(Already have it? `git pull`.)

**2. Build once** (a few minutes the first time; runs a 5-check self-test)

```bash
docker build -t touchline .
```

**3. Run on your match video** — put `match.mp4` in this folder first:

PowerShell (Windows):

```powershell
docker run --rm -v "$PWD/match.mp4:/videos/match.mp4:ro" -v "$PWD/output:/app/output" touchline /videos/match.mp4 --out /app/output
```

bash (macOS/Linux — same command):

```bash
docker run --rm -v "$PWD/match.mp4:/videos/match.mp4:ro" -v "$PWD/output:/app/output" touchline /videos/match.mp4 --out /app/output
```

**4. Read the report** in `output/`:

- `report.html` — human-readable report (open in a browser)
- `report.json` — the same data as structured JSON
- `heatmap_team_0.png`, `heatmap_team_1.png` — team heatmaps on a pitch

> First run downloads the YOLO weights (~6 MB, automatic). Manual pitch
> calibration needs a click window, so inside Docker it doesn't apply — use the
> all-features image below, which calibrates automatically.

---

## All features — auto calibration (no clicking) + events

**1. Build the all-features image** (adds NBJW auto-calibration + the events
model; weights for NBJW download during the build)

```bash
docker build --build-arg WITH_NBJW=1 --build-arg WITH_EVENTS=1 -t touchline:all .
```

**2. Download the event weights once** — the only manual step. Open the
[Trained models](https://github.com/lRomul/ball-action-spotting) link in the
ball-action-spotting README (Google Drive), download and unpack it so this
folder exists next to `match.mp4`:

```
weights/sampling_weights_001/fold_0/
```

(The weights are on Google Drive, so the build can't fetch them. You only need
the `sampling_weights_001` experiment — Touchline's default.)

**3. Run with everything** — needs an **NVIDIA GPU**:

PowerShell (Windows):

```powershell
docker run --rm --gpus all -v "$PWD/match.mp4:/videos/match.mp4:ro" -v "$PWD/output:/app/output" -v "$PWD/weights:/workdir/data/ball_action/experiments:ro" touchline:all /videos/match.mp4 --out /app/output --auto-calibrate /nbjw --include-events --action-spotting-repo /workdir --action-spotting-prepare
```

bash (macOS/Linux — same command):

```bash
docker run --rm --gpus all \
  -v "$PWD/match.mp4:/videos/match.mp4:ro" \
  -v "$PWD/output:/app/output" \
  -v "$PWD/weights:/workdir/data/ball_action/experiments:ro" \
  touchline:all /videos/match.mp4 --out /app/output \
  --auto-calibrate /nbjw \
  --include-events --action-spotting-repo /workdir --action-spotting-prepare
```

What each flag does:

- `--auto-calibrate /nbjw` — pitch calibration from the first frame, no clicking
- `--include-events` + `--action-spotting-repo /workdir` — detect passes/drives
- `--action-spotting-prepare` — resamples your video to the model's input
  format (1280x736 @ 25 fps); drop it if your video already matches

Events land in `report.json` / `report.html` with timestamps, pitch positions,
and confidence scores.

**No GPU?** Run the same command without the events flags (or use `touchline`
instead of `touchline:all`):

```bash
docker run --rm -v "$PWD/match.mp4:/videos/match.mp4:ro" -v "$PWD/output:/app/output" touchline:all /videos/match.mp4 --out /app/output --auto-calibrate /nbjw
```

> GPU on Windows: Docker Desktop needs the WSL2 backend (default) + the
> [NVIDIA driver for WSL](https://www.nvidia.com/en-us/software/nvidia-drivers/).
> Linux: install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

---

## No Docker? (Linux/macOS only)

<details>
<summary>Native setup via make</summary>

```bash
make setup                # core: venv + deps + YOLO weights
make setup-nbjw           # + auto calibration (clones NBJW + weights)
make setup-events         # + events repo (weights still manual, see above)
make run VIDEO=match.mp4  # run the pipeline (auto-runs setup first)
```

Auto calibration:

```bash
make run VIDEO=match.mp4 EXTRA="--auto-calibrate third_party/no-bells-just-whistles"
```

Events (native) need the model's hardcoded `/workdir` path to point at the
checkout plus a few extra Python packages:

```bash
sudo ln -s "$PWD/third_party/ball-action-spotting" /workdir
pip install timm kornia pytorch-argus scipy
python -m touchline match.mp4 --out output --include-events --action-spotting-repo /workdir --action-spotting-prepare
```

</details>

---

## Options cheat sheet

| Option | What it does |
|---|---|
| `--out DIR` | Output directory (default `output/`) |
| `--frame-step N` | Process every Nth frame — higher is faster, fine for territory/heatmaps |
| `--model NAME` | YOLO model (default `yolov8n.pt`) |
| `--calibration FILE` | Reuse a saved calibration instead of clicking/auto-calibrating |
| `--auto-calibrate DIR` | Auto pitch calibration via NBJW (no clicking) |
| `--include-events` | Run action spotting (needs `--action-spotting-repo`) |
| `--action-spotting-repo DIR` | Path to the ball-action-spotting checkout (in the image: `/workdir`) |
| `--action-spotting-experiment NAME` | Trained experiment to use (default `sampling_weights_001`) |
| `--action-spotting-device` | Device for the events model (default `cuda:0`) |
| `--action-spotting-prepare` | Resample video to 1280x736 @ 25 fps first (needs ffmpeg) |

## Filming tips

- Keep the camera still and wide enough to see most of the pitch — ideally all
  four corners, or at least the two touchline corners plus two far-side points.
- Higher frame rate improves distance/speed accuracy; territory and possession
  are robust at lower rates.

## Docs

- `plan.md` — roadmap and difficulty ladder
- `_config/architecture.md` — how the pipeline fits together
- `_config/integrations.md` — the open-source models used, in detail
