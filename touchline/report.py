"""
@file report.py
@description Serialise pipeline metrics to report.json (the stable contract)
  and a self-contained report.html view.

@status None
@issues None
@todo Add an SVG pitch with territory shading to the HTML report.
"""

import base64
import json
from pathlib import Path

import numpy as np


def write_report(out_dir, metrics: dict, heatmap_paths: dict) -> dict:
    """Write report.json and report.html; return their paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "report.json"
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, default=_json_default)
    html_path = out_dir / "report.html"
    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write(_render_html(metrics, heatmap_paths))
    return {"json": str(json_path), "html": str(html_path)}


def _json_default(value):
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    raise TypeError(f"Unsupported type for JSON: {type(value)}")


def _render_html(metrics: dict, heatmap_paths: dict) -> str:
    video = metrics.get("video", {})
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Match report</title><style>
:root{{color-scheme:dark}}
body{{font:16px/1.5 system-ui,sans-serif;background:#0d1117;color:#e6edf3;
max-width:960px;margin:auto;padding:32px 20px}}
h1{{font-size:28px;margin:0 0 4px}}h2{{font-size:20px;margin:32px 0 12px;
border-bottom:1px solid #30363d;padding-bottom:6px}}
.muted{{color:#8b949e;font-size:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:16px;margin:16px 0}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}}
.bar{{height:14px;background:#21262d;border-radius:7px;overflow:hidden;margin:6px 0}}
.fill{{height:100%}}
.t0{{background:#58a6ff}}.t1{{background:#f85149}}.ctx{{background:#8b949e}}
img{{width:100%;border:1px solid #30363d;border-radius:8px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{text-align:left;padding:8px;border-bottom:1px solid #30363d}}
</style></head><body>
<h1>Match report</h1>
<p class="muted">{video.get('path', '')} · {video.get('fps', 0)} fps ·
{video.get('frames_processed', 0)} frames processed</p>
{_possession_section(metrics.get('possession', {}))}
{_territory_section(metrics.get('territory', {}))}
{_distance_section(metrics.get('distance', {}))}
{_heatmap_section(heatmap_paths)}
</body></html>"""


def _possession_section(possession: dict) -> str:
    fractions = possession.get("fractions", {})
    if not fractions:
        return "<h2>Possession</h2><p class='muted'>No data.</p>"
    return f"""<h2>Possession</h2>
<div class="card">
{_bar("team_0", "Team 0", fractions.get("team_0", 0))}
{_bar("team_1", "Team 1", fractions.get("team_1", 0))}
{_bar("ctx", "Contested", fractions.get("contested", 0))}
<p class="muted">No ball detected: {_percent(fractions.get('no_ball', 0))}</p>
</div>"""


def _territory_section(territory: dict) -> str:
    thirds = territory.get("thirds", {})
    if not thirds:
        return "<h2>Territory</h2><p class='muted'>No data.</p>"
    return f"""<h2>Territory (ball position)</h2>
<div class="card">
{_bar("t0", "Left third", thirds.get("left", 0))}
{_bar("ctx", "Middle third", thirds.get("middle", 0))}
{_bar("t1", "Right third", thirds.get("right", 0))}
</div>"""


def _distance_section(distance: dict) -> str:
    teams = distance.get("teams", {})
    if not teams:
        return "<h2>Distance covered</h2><p class='muted'>No data.</p>"
    tracklets = distance.get("tracklets", [])
    rows = "".join(
        f"<tr><td>{t['track_id']}</td><td>Team {t['team_id']}</td>"
        f"<td>{t['distance_m']} m</td><td>{t['duration_s']} s</td>"
        f"<td>{t['avg_speed_ms']} m/s</td></tr>"
        for t in tracklets[:20]
    )
    return f"""<h2>Distance covered</h2>
<div class="card">
<p>Team 0: <strong>{teams.get('team_0_distance_m', 0)} m</strong> ·
Team 1: <strong>{teams.get('team_1_distance_m', 0)} m</strong></p>
</div>
<table><tr><th>Track</th><th>Team</th><th>Distance</th><th>Duration</th>
<th>Avg speed</th></tr>{rows}</table>"""


def _heatmap_section(heatmap_paths: dict) -> str:
    images = ""
    for label, path in heatmap_paths.items():
        data_uri = _image_data_uri(path)
        images += f"<div class='card'><h3>{label}</h3><img src='{data_uri}'></div>"
    return f"<h2>Team heatmaps</h2><div class='grid'>{images}</div>"


def _bar(css_class: str, label: str, fraction) -> str:
    width = round(float(fraction) * 100, 1)
    return (f"<div>{label} — {width}%</div>"
            f"<div class='bar'><div class='fill {css_class}' "
            f"style='width:{width}%'></div></div>")


def _percent(fraction) -> str:
    return f"{round(float(fraction) * 100, 1)}%"


def _image_data_uri(path: str) -> str:
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
