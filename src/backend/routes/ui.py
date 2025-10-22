from flask import Blueprint, render_template, jsonify, abort
import os, json
from pathlib import Path

bp = Blueprint("ui", __name__, template_folder="../templates")

RUNS_DIR = Path("runs_data")  # where your /api/generate saves files

def _load_run(run_id: str):
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _adapt_for_results_template(run_json: dict):
    """
    Your saved runs look like:
      {
        "run_id": "...",
        "project_name": "...",
        "epics": [...],                # input epics as posted
        "output": {
          "stories": [                 # CSV-friendly list
            { "epic_id": "...", "stories": [...], "test_cases": [...] }, ...
          ]
        }
      }

    results.html expects a nested shape under run.output.epics:
      run.output.epics -> [{ title, epic_id, stories: [{story_id,title, test_cases:[{id,steps,expected_result}] }]}]
    We’ll map your simple output into that shape for display.
    """
    out = run_json.get("output") or {}
    items = out.get("stories") or []

    epics = []
    for idx, item in enumerate(items, start=1):
        epic_id = item.get("epic_id") or f"EPC-{idx:03d}"
        # build simple stories from the title strings you stored
        story_rows = []
        for i, s in enumerate(item.get("stories") or [], start=1):
            story_rows.append({
                "story_id": f"US-{i:02d}",
                "title": s,
                "test_cases": [
                    {"id": f"TC-{i:02d}", "steps": "—", "expected_result": (item.get("test_cases") or [""])[0] or ""}
                ]
            })
        epics.append({
            "epic_id": epic_id,
            "title": next((e.get("title") for e in run_json.get("epics", []) if e.get("epic_id")==epic_id), epic_id),
            "stories": story_rows
        })

    # Attach adapted epics where the template looks for them
    adapted = dict(run_json)
    adapted.setdefault("output", {})
    adapted["output"]["epics"] = epics
    return adapted

@bp.get("/")
def home():
    # Renders the landing page with textarea + button
    return render_template("index.html")

@bp.get("/runs")
def runs():
    RUNS_DIR.mkdir(exist_ok=True)
    runs = []
    for f in sorted(RUNS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with f.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            runs.append({
                "run_id": data.get("run_id"),
                "project_name": data.get("project_name"),
                "generated_at": f.stat().st_mtime  # epoch (you can format on template)
            })
        except Exception:
            pass
    # We’ll feed runs into runs_list.html dynamically
    return render_template("runs_list.html", runs=runs)

@bp.get("/runs/<run_id>")
def run_detail(run_id: str):
    run_json = _load_run(run_id)
    if not run_json:
        abort(404)
    vm = _adapt_for_results_template(run_json)
    return render_template("results.html", run=vm)
