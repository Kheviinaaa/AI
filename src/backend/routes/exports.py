from flask import Blueprint, jsonify, Response
import json
import os
import csv
import io
from typing import Dict, Any, List

bp = Blueprint("exports", __name__)

RUNS_DIR = "runs_data"

def _ensure_runs_dir():
    os.makedirs(RUNS_DIR, exist_ok=True)

def _load_run(run_id: str) -> Dict[str, Any] | None:
    _ensure_runs_dir()
    path = os.path.join(RUNS_DIR, f"{run_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _list_runs() -> List[Dict[str, Any]]:
    _ensure_runs_dir()
    items = []
    for fname in sorted(os.listdir(RUNS_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(RUNS_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items.append({
                "run_id": data.get("run_id") or fname[:-5],
                "project_name": data.get("project_name"),
                "mtime": os.path.getmtime(path),
            })
        except Exception:
            # skip corrupt files
            continue
    # most recent first
    items.sort(key=lambda r: r["mtime"], reverse=True)
    return items

def _get_flat_rows(output: Dict[str, Any]) -> List[List[str]]:
    """
    Normalize output into rows for CSV. Supports either:
      output["stories"] = [{ epic_id, stories: [...], test_cases: [...] }]
      or a future shape:
      output["epics"]   = [{ epic_id, title, stories: [{title,...}], test_cases: [...] }]
    Returns rows as [epic_id, story, test_case].
    """
    rows: List[List[str]] = []

    # Primary shape used by your backend today
    stories_list = output.get("stories") or []

    # Fallback if you later save full objects under "epics"
    if not stories_list and isinstance(output.get("epics"), list):
        for e in output["epics"]:
            epic_id = e.get("epic_id", "")
            story_titles = [s.get("title", "") for s in (e.get("stories") or [])]
            tests = [t.get("id", "") if isinstance(t, dict) else str(t) for t in (e.get("test_cases") or [])]
            max_len = max(len(story_titles), len(tests), 1)
            for i in range(max_len):
                rows.append([
                    epic_id,
                    story_titles[i] if i < len(story_titles) else "",
                    tests[i] if i < len(tests) else "",
                ])
        return rows

    # Current shape (simple strings)
    for epic_data in stories_list:
        epic_id = (epic_data or {}).get("epic_id", "")
        stories = (epic_data or {}).get("stories") or []
        tests   = (epic_data or {}).get("test_cases") or []
        max_len = max(len(stories), len(tests), 1)
        for i in range(max_len):
            rows.append([
                epic_id,
                stories[i] if i < len(stories) else "",
                tests[i] if i < len(tests) else "",
            ])

    return rows

def to_csv(output: Dict[str, Any]) -> str:
    """
    Simple CSV formatter: (Epic ID, Story, Test Case) per row.
    Adds UTF-8 BOM to play nicely with Excel.
    """
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerow(["Epic ID", "Story", "Test Case"])

    for row in _get_flat_rows(output):
        writer.writerow(row)

    return "\ufeff" + buf.getvalue()  # BOM for Excel

@bp.get("/")
def list_runs():
    """List all runs (for your 'All Runs' page or debugging)."""
    return jsonify({"runs": _list_runs()})

@bp.get("/<run_id>/json")
def get_json(run_id: str):
    data = _load_run(run_id)
    if not data:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(data)

@bp.get("/<run_id>/csv")
def get_csv(run_id: str):
    data = _load_run(run_id)
    if not data:
        return jsonify({"error": "Run not found"}), 404
    csv_content = to_csv(data.get("output") or {})
    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={run_id}.csv"}
    )
