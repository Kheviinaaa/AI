from flask import Blueprint, request, jsonify
from src.config import Config
from src.backend.services.jira_api import JiraAPI

bp = Blueprint("epics", __name__)

@bp.get("")  # GET /api/epics?project=ECOM
def list_epics():
    if Config.DATA_SOURCE != "jira":
        return jsonify({"error": "DATA_SOURCE is not 'jira'"}), 400

    project = request.args.get("project")
    if not project:
        return jsonify({"error": "Missing query param 'project'"}), 400

    try:
        jira = JiraAPI()
        epics = jira.search_epics(project_key=project, max_results=25)
        return jsonify({"project": project, "count": len(epics), "epics": epics})
    except Exception as e:
        return jsonify({"error": "jira_fetch_failed", "message": str(e)}), 500
