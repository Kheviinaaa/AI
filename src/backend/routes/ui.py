from __future__ import annotations
from flask import Blueprint, abort, render_template
import json
from pathlib import Path

bp = Blueprint("ui", __name__, template_folder="../templates")

RUNS_DIR = Path("runs_data")


def _load_run(run_id: str):
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    

def _adapt_for_results_template(run_json: dict):
    out = run_json.get("output") or {}
    items = out.get("epics") or (out if isinstance(out, list) else [])

    meta_lookup = {e.get("epic_id"): e for e in run_json.get("epics", [])}

    epics = []
    for idx, item in enumerate(items if isinstance(items, list) else [], start=1):
        epic_id = (item.get("epic_id") or f"EPC-{idx:03d}")
        meta = meta_lookup.get(epic_id) or {}
        stories = []
        for sidx, story in enumerate(item.get("UserStories", []) or [], start=1):
            ac = story.get("acceptance_criteria", {}) or {}
            stories.append({
                "story_id": f"US-{idx:02d}-{sidx:02d}",
                "title": story.get("title", ""),
                "description": story.get("description", ""),
                "acceptance_criteria": {
                    "Given": ac.get("Given", ""),
                    "When": ac.get("When", ""),
                    "Then": ac.get("Then", ""),
                },
                "story_points": story.get("story_points"),
            })

        tests = []
        for case in item.get("TestCases", []) or []:
            steps = case.get("test_steps", [])
            if isinstance(steps, str):
                steps = [steps]
            tests.append(
                {
                    "id": case.get("id", ""),
                    "objective": case.get("objective", ""),
                    "preconditions": case.get("preconditions", ""),
                    "test_steps": steps,
                    "expected_result": case.get("expected_result", ""),
                }
            )

        epics.append(
            {
                "epic_id": epic_id,
                "title": item.get("Epic") or meta.get("title") or epic_id,
                "description": meta.get("description") or item.get("description", ""),
                "stories": stories,
                "test_cases": tests,
            }
        )

    adapted = dict(run_json)
    adapted.setdefault("output", {})
    adapted["output"]["epics"] = epics
    adapted.setdefault("mode", run_json.get("mode") or run_json.get("output", {}).get("mode"))
    return adapted

# ---------- HOME = CHAT ----------
@bp.get("/")
def home():
    return render_template("chat.html")

# (Optional: keep a direct /chat route too)
@bp.get("/chat")
def chat_page():
    return render_template("chat.html")

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
                "generated_at": data.get("generated_at"),
                "mode": data.get("mode"),
            })
        except Exception:
            pass
    return render_template("runs_list.html", runs=runs)

@bp.get("/runs/<run_id>")
def run_detail(run_id: str):
    data = _load_run(run_id)
    if not data:
        abort(404)
    vm = _adapt_for_results_template(data)
    return render_template("results.html", run=vm)
