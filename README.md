# Touchline

Sideline phone footage of a football (soccer) match → simple analysis data:
territory %, possession %, team heatmaps, distance/speed, and events
(passes, shots, goals). Record the match, run the pipeline, read the report.

Open-source-first: player/ball detection and tracking come from Ultralytics
YOLOv8 + ByteTrack, auto pitch calibration from No Bells Just Whistles (NBJW),
and events from a SoccerNet action-spotting model. Touchline only glues them
together. Football means soccer (FIFA rules).

---

## 1. Set up after a `git pull`

### Windows (native — double-click, no `make`)

You only need **Python 3.10+** (install from
https://www.python.org/downloads/ and tick **"Add Python to PATH"**). The
optional auto-calibration and events extras also need **Git for Windows**
(https://git-scm.com/download/win).

**Step 1 — set up** — double-click **`setup.bat`**.

It creates the `.venv` environment, installs the dependencies (OpenCV, NumPy,
Ultralytics YOLOv8 + torch), and pre-downloads the YOLOv8n weights. Wait for
"Setup complete" — the first install takes a few minutes.

**Step 2 — analyse a match video** — double-click **`run.bat`** and drag your
video onto it, or open a terminal (cmd / PowerShell) in the project folder:

```bat
run.bat "C:\path\to\match.mp4"
```

`run.bat` runs setup automatically if you skipped Step 1, then runs the
pipeline. Extra options pass straight through:

```bat
run.bat "C:\path\to\match.mp4" --frame-step 4 --out output\match1
```

**Step 3 — read the results** in `output\` (or your `--out` folder):

- `report.html` — human-readable report
- `report.json` — the same data as structured JSON (the stable contract)
- `heatmap_team_0.png`, `heatmap_team_1.png` — team heatmaps on a pitch

No video handy? Double-click **`smoke-test.bat`** — it verifies the metric core
(expect 5 PASS).

### Linux / macOS (one-command, via `make`)

```bash
make setup
make run VIDEO=path/to/match.mp4
```

`make setup` creates `.venv`, installs dependencies, and pre-downloads the
YOLOv8n weights. `make run` runs the pipeline (auto-running setup first).

<details>
<summary>Manual setup (no make)</summary>

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The YOLOv8 nano weights download automatically on the first run.

</details>

### First run: pitch calibration

The first run shows a still frame and asks you to click the four pitch corners
in order: **near-left, near-right, far-right, far-left** (near = the camera
side, bottom of the frame). Press `q` once the four points are set. The
calibration is saved, so later runs won't ask again.

## 2. Auto calibration (no clicking)

Replaces Step 2's manual clicking with the NBJW pitch-detection model.

**One-time setup** — one command:

```bash
make setup-nbjw
```

(Windows: double-click **`setup-nbjw.bat`** — needs Git for Windows.)

This clones NBJW into `third_party/no-bells-just-whistles/` and downloads the
**`SV_kp`** and **`SV_lines`** weights into it (the adapter expects files named
exactly `SV_kp` and `SV_lines` in the repo root). No extra Python packages:
torch, OpenCV, numpy, yaml and Pillow are the same ones YOLO already pulled in.

<details>
<summary>Manual alternative</summary>

1. `git clone https://github.com/mguti97/no-bells-just-whistles`
2. Download the **`SV_kp`** and **`SV_lines`** weights from that repo's
   Releases page and save them inside the cloned folder.

</details>

**Run**

```bash
make run VIDEO=path/to/match.mp4 EXTRA="--auto-calibrate third_party/no-bells-just-whistles"
```

or, with the venv activated:

```bash
python -m touchline path/to/match.mp4 --out output \
  --auto-calibrate third_party/no-bells-just-whistles
```

Windows:

```bat
run.bat "C:\path\to\match.mp4" --auto-calibrate third_party\no-bells-just-whistles
```

No window, no clicking — the homography is computed from the first frame. If it
fails on your footage (unusual angles, tight framing), drop the flag and
re-run: you get the manual click window instead.

## 3. Auto events (passes, shots, goals)

Adds event timestamps to the report, detected by a SoccerNet action-spotting
model. Needs an **NVIDIA GPU** and the model's own environment. On Windows the
Docker steps below run inside WSL2 (Docker Desktop).

**One-time setup**

1. Clone the model repo — one command (into `third_party/ball-action-spotting/`):
   ```bash
   make setup-events
   ```
   (Windows: double-click **`setup-events.bat`** — needs Git for Windows.)
2. Download the trained weights from the Google Drive link in that repo's
   README and unpack them so this folder exists:
   ```
   third_party/ball-action-spotting/data/ball_action/experiments/sampling_weights_001/fold_0/
   ```
   (This step can't be scripted: the weights live on Google Drive. You only
   need the `sampling_weights_001` experiment — Touchline's default.)
3. Run the model inside its own Docker container — the author's recommended
   setup and effectively required, because the model code looks for its data
   at the hardcoded `/workdir` path (which `make run` mounts for you):
   ```bash
   cd third_party/ball-action-spotting
   make
   ```
4. The container only mounts this repo folder, so give it access to your
   Touchline checkout and your match video:
   ```bash
   make stop
   make run OPTIONS="-v /path/to/touchline:/touchline -v /path/to/videos:/videos"
   ```

**Run** (inside the container):

```bash
pip install -r /touchline/requirements.txt
cd /touchline
python -m touchline /videos/match.mp4 --out /videos/match1 \
  --include-events \
  --action-spotting-repo /workdir \
  --action-spotting-prepare
```

`--action-spotting-prepare` resamples the video to the model's input format
(1280x736 @ 25 fps) with ffmpeg — leave it out if your video already matches.
Events land in `report.json` / `report.html` with timestamps, pitch positions
and confidence scores. Override the experiment with
`--action-spotting-experiment` if you use another one. For a richer class set
(Shot, Goal, Corner, Header, …), the 2024 fork `recokick/ball-action-spotting`
works with the same steps.

*No Docker? Clone the repo to `/workdir` instead, install a CUDA build of torch
plus `timm kornia pytorch-argus scipy` into your Touchline environment, put the
weights under `/workdir/data/ball_action/experiments/…`, and run the command
above without the container.*

## Options cheat sheet

| Option | What it does |
|---|---|
| `--out DIR` | Output directory (default `output/`) |
| `--frame-step N` | Process every Nth frame — higher is faster, fine for territory/heatmaps |
| `--model NAME` | YOLO model (default `yolov8n.pt`) |
| `--calibration FILE` | Reuse a saved calibration instead of re-clicking |
| `--auto-calibrate DIR` | Auto pitch calibration via NBJW (section 2) |
| `--include-events` | Run action spotting (section 3) |
| `--action-spotting-repo DIR` | Path to the ball-action-spotting checkout |
| `--action-spotting-experiment NAME` | Trained experiment to use (default `sampling_weights_001`) |
| `--action-spotting-device` | Device for the model (default `cuda:0`) |
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

## Why setup can't be fully automatic

The `setup*` scripts (`make setup*` on Linux/macOS, `setup*.bat` on Windows) get
a fresh checkout to a working state in one step, but a truly zero-step setup is
impossible:

- **The virtualenv is per-machine state.** `.venv` contains machine-specific
  binaries and paths and is gitignored — it can never come from `git pull`.
  Every machine builds its own.
- **Model weights are large binaries hosted externally** (GitHub Releases,
  Google Drive), not in this repo — so they can't be pulled, only downloaded
  once per machine. YOLOv8n and the NBJW weights are scripted; the
  action-spotting weights sit on Google Drive, so that one step stays manual.
- **The eventer needs an NVIDIA GPU + Docker** — hardware and a container the
  model author provides; no script can supply them.
- **OS differences** — Linux/macOS use `make`; Windows uses the double-click
  `.bat` scripts (or WSL). Both paths do the same thing.
