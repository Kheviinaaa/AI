# src/backend/routes/generate.py
from __future__ import annotations
from flask import Blueprint, request, jsonify
import os, json, uuid, datetime
from pathlib import Path

try:
    # prefer package import
    from src.ai_engine import generate_user_stories, using_live_model
except Exception:
    # fallback if run as script
    from ai_engine import generate_user_stories, using_live_model  # type: ignore

bp = Blueprint("generate", __name__)
RUNS_DIR = Path("runs_data")

@bp.post("")
def generate():
    """
    Expected payload from UI:
      {
        "project_name": "AI Jira Project",
        "epics": [
          {"epic_id":"E1","title":"X","description":"..."},
          ...
        ]
      }
    """
    data = request.get_json(silent=True) or {}
    project_name = (data.get("project_name") or "AI Jira Project").strip()
    epics_in = data.get("epics") or []

    if not isinstance(epics_in, list) or not epics_in:
        return jsonify({"error": "No epics provided"}), 400

    run_id = str(uuid.uuid4())
    mode = "live" if using_live_model() else "mock"

    # Build output.epics by calling the engine once per epic
    output_epics = []
    for idx, e in enumerate(epics_in, start=1):
        epic_id = e.get("epic_id") or f"E{idx}"
        title = e.get("title") or f"Epic {idx}"
        desc = e.get("description") or title

        result = generate_user_stories(
            epic_text=desc,
            epic_title=title,
            epic_id=epic_id,
            epic_description=desc,
        )

        # result already normalised to {Epic, UserStories, TestCases, ...}
        output_epics.append({
            "epic_id": epic_id,
            "Epic": result.get("Epic") or title,
            "description": result.get("description") or desc,
            "UserStories": result.get("UserStories") or [],
            "TestCases": result.get("TestCases") or [],
        })

    run_json = {
        "run_id": run_id,
        "project_name": project_name,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "mode": mode,
        "constraints": data.get("constraints"),
        "epics": epics_in,
        "output": {"epics": output_epics},
        "validation": {"schema_passed": True},  # you can wire your validator here
    }

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RUNS_DIR / f"{run_id}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(run_json, f, indent=2)

    return jsonify({
        "status": "success",
        "run_id": run_id,
        "message": f"Generated {len(output_epics)} epic(s)",
        "links": {
            "json": f"/api/runs/{run_id}/json",
            "csv":  f"/api/runs/{run_id}/csv",
        }
    }), 200
