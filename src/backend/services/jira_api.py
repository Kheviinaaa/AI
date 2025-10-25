# src/backend/services/jira_api.py
from __future__ import annotations
import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Any, Dict, List, Optional

class JiraAPI:
    """
    Thin wrapper over Jira Cloud REST API using basic auth (email + API token).
    Only read scopes are needed for listing projects/issues.
    """

    def __init__(self,
                 base_url: Optional[str] = None,
                 email: Optional[str] = None,
                 api_token: Optional[str] = None) -> None:
        self.base_url = (base_url or os.getenv("JIRA_BASE_URL", "")).rstrip("/")
        self.email = email or os.getenv("JIRA_EMAIL", "")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN", "")
        if not (self.base_url and self.email and self.api_token):
            raise RuntimeError("Jira credentials missing: set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.headers = {"Accept": "application/json"}

    # -------- Utilities --------
    def _get(self, path: str, **params) -> Dict[str, Any] | List[Any]:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self.headers, auth=self.auth, params=params or None, timeout=20)
        resp.raise_for_status()
        return resp.json()

    # -------- Endpoints you actually need --------
    def list_projects(self) -> List[Dict[str, Any]]:
        # Prefer the paginated endpoint
        data = self._get("/rest/api/3/project/search")
        # Jira returns {"maxResults":..., "values":[...]}
        values = data.get("values") if isinstance(data, dict) else None
        if isinstance(values, list):
            return values
        # fallback to old non-paginated result ([] or list)
        if isinstance(data, list):
            return data
        return []

    def search_issues(self, jql: str, max_results: int = 50) -> Dict[str, Any]:
        return self._get("/rest/api/3/search", jql=jql, maxResults=max_results)

    def list_epics_for_project(self, project_key: str) -> List[Dict[str, Any]]:
        # JQL: type = Epic in that project
        data = self.search_issues(f'project = "{project_key}" AND issuetype = Epic ORDER BY created DESC',
                                  max_results=100)
        issues = data.get("issues", [])
        epics = []
        for it in issues:
            fields = it.get("fields", {}) if isinstance(it, dict) else {}
            epics.append({
                "epic_id": it.get("key"),
                "title": fields.get("summary", ""),
                "description": fields.get("description") if fields.get("description") else "",
            })
        return epics
