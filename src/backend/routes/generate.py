# src/backend/routes/generate.py  (REAL GENERATOR VERSION)
from flask import Blueprint, request, jsonify
import uuid, json, os
from src.ai_engine import generate_user_stories

bp = Blueprint("generate", __name__)

@bp.post("")
def generate():
    try:
        body = request.get_json(silent=True) or {}

        # Accept either array or {epics:[...]}
        if isinstance(body, list):
            epics = body
            project_name = "AI Jira Project"
        else:
            epics = body.get("epics") or []
            project_name = body.get("project_name", "AI Jira Project")

        run_id = str(uuid.uuid4())
        output = {"stories": []}

        for e in epics:
            epic_id = (e or {}).get("epic_id") or ""
            title   = (e or {}).get("title") or ""
            desc    = (e or {}).get("description") or ""

            print(">> Calling AI for:", title, "|", desc)

            ai_obj = generate_user_stories(desc, title)  # -> {"Epic","UserStories","TestCases"}
            user_stories = ai_obj.get("UserStories") or []
            test_cases   = ai_obj.get("TestCases") or []

            print(">> AI returned:", len(user_stories), "stories;", len(test_cases), "tests")

            output["stories"].append({
                "epic_id": epic_id or title or "EPIC",
                "stories": [ (s or {}).get("title","") for s in user_stories ],
                "test_cases": [
                    ((t or {}).get("id") or (t or {}).get("objective") or "").strip()
                    if isinstance(t, dict) else str(t)
                    for t in test_cases
                ]
            })
        
        mode = "real" if os.getenv("OPENAI_API_KEY") else "mock"

        run_data = {
            "run_id": run_id,
            "project_name": project_name,
            "mode": mode,
            "epics": epics,
            "output": output
        }

        os.makedirs("runs_data", exist_ok=True)
        with open(f"runs_data/{run_id}.json", "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)

        print(">> Saved run:", run_id, "items:", len(output["stories"]))  # DEBUG
        return jsonify({
            "status": "success",
            "run_id": run_id,
            "message": f"Generated {len(epics)} epic(s)",
            "links": {
                "json": f"/api/runs/{run_id}/json",
                "csv":  f"/api/runs/{run_id}/csv"
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
