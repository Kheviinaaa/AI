# src/backend/routes/exports.py
from flask import Blueprint, jsonify, Response
import json, os, csv, io

bp = Blueprint("exports", __name__)

# Absolute path to runs_data (adjust if your folder is elsewhere)
RUNS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "runs_data"))

def _load_run(run_id: str):
    """
    Load a saved run JSON from runs_data/<run_id>.json.
    Returns (data, path). If missing, (None, path).
    """
    path = os.path.join(RUNS_DIR, f"{run_id}.json")
    if not os.path.exists(path):
        return None, path
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), path

def to_csv(output_section: dict) -> str:
    """
    Convert output into rows: Epic ID, Story, Test Case.
    Accepts either:
      - {"epics": [...]}  (normalized structure)
      - {"stories": [...]} (older/simple structure)
    """
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Epic ID", "Story", "Test Case"])

    # Prefer normalized "epics" shape: [{"epic_id":..., "stories":[...], "test_cases":[...]}]
    epics = (output_section or {}).get("epics")
    if isinstance(epics, list):
        for epic in epics:
            epic_id = (epic or {}).get("epic_id", "")
            stories = (epic or {}).get("stories") or []
            tests   = (epic or {}).get("test_cases") or []
            max_len = max(len(stories), len(tests), 1)
            for i in range(max_len):
                story = stories[i] if i < len(stories) else ""
                test  = tests[i]   if i < len(tests)   else ""
                # Story could be dict or string
                if isinstance(story, dict):
                    story = story.get("title") or story.get("description") or json.dumps(story, ensure_ascii=False)
                if isinstance(test, dict):
                    test = test.get("objective") or test.get("expected_result") or json.dumps(test, ensure_ascii=False)
                w.writerow([epic_id, story, test])
        return out.getvalue()

    # Fallback to legacy "stories" shape: [{"epic_id":..., "stories":[...], "test_cases":[...]}]
    stories_list = (output_section or {}).get("stories") or []
    for entry in stories_list:
        epic_id = (entry or {}).get("epic_id", "")
        stories = (entry or {}).get("stories") or []
        tests   = (entry or {}).get("test_cases") or []
        max_len = max(len(stories), len(tests), 1)
        for i in range(max_len):
            story = stories[i] if i < len(stories) else ""
            test  = tests[i]   if i < len(tests)   else ""
            if isinstance(story, dict):
                story = story.get("title") or story.get("description") or json.dumps(story, ensure_ascii=False)
            if isinstance(test, dict):
                test = test.get("objective") or test.get("expected_result") or json.dumps(test, ensure_ascii=False)
            w.writerow([epic_id, story, test])

    return out.getvalue()

@bp.get("/<run_id>/json")
def get_json(run_id):
    data, path = _load_run(run_id)
    if data is None:
        # Always return something (prevents "view did not return a valid response")
        return jsonify({"error": "Run not found", "path": path}), 404
    return jsonify(data), 200

@bp.get("/<run_id>/csv")
def get_csv(run_id):
    data, path = _load_run(run_id)
    if data is None:
        return jsonify({"error": "Run not found", "path": path}), 404

    # Defensive check: handle empty runs gracefully
    output_section = (data or {}).get("output") or {}
    epics = output_section.get("epics") or []
    if not epics:
        return jsonify({
            "run_id": run_id,
            "message": "No epics found in this run — nothing to export.",
            "status": "empty"
        }), 200

    csv_body = to_csv(output_section)
    return Response(
        csv_body,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={run_id}.csv"},
    )

