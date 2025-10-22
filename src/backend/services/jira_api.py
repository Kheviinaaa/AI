import requests
from typing import List, Dict
from src.config import Config

class JiraAPI:
    def __init__(self):
        self.base = Config.JIRA_BASE_URL.rstrip("/")
        self.auth = (Config.JIRA_EMAIL, Config.JIRA_API_TOKEN)
        self.headers = {"Accept": "application/json"}

    def search_epics(self, project_key: str, max_results: int = 25) -> List[Dict]:
        """
        Returns a list of epics with epic_id/title/description.
        """
        jql = f'project = "{project_key}" AND issuetype = Epic ORDER BY created DESC'
        url = f"{self.base}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,description"
        }
        r = requests.get(url, headers=self.headers, params=params, auth=self.auth, timeout=20)
        r.raise_for_status()
        data = r.json()
        epics = []
        for issue in data.get("issues", []):
            key = issue.get("key", "")
            fields = issue.get("fields", {}) or {}
            title = fields.get("summary") or key
            # Description can be rich text; we try simple fallback:
            desc = ""
            d = fields.get("description")
            if isinstance(d, str):
                desc = d
            elif isinstance(d, dict):
                # Jira Cloud "atlaskit" doc format—extract plain text roughly
                desc = _extract_plain_text(d)
            epics.append({"epic_id": key, "title": title, "description": desc})
        return epics

def _extract_plain_text(doc: dict) -> str:
    # Very rough extractor for Atlassian "doc" JSON
    text_parts = []
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text" and "text" in node:
                text_parts.append(node["text"])
            for k, v in node.items():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)
    walk(doc)
    return " ".join(text_parts).strip()
