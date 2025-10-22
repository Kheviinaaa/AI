def adapt_ai_engine_epic(epic_obj: dict) -> dict:
    """
    Input shape (from your ai_engine.py mock/real):
      {
        "Epic": "Title",
        "UserStories": [{title, description, acceptance_criteria{Given,When,Then}, story_points}, ...],
        "TestCases": [{id, objective, expected_result}, ...]
      }
    Output shape (what your CSV formatter expects):
      { "title": "...", "stories": [...], "test_cases": [...] }
    """
    stories = []
    for i, s in enumerate(epic_obj.get("UserStories", []), start=1):
        stories.append({
            "story_id": f"US-{i:02d}",
            "title": s.get("title", ""),
            "description": s.get("description", ""),
            "acceptance_criteria": s.get("acceptance_criteria", {}),
            "story_points": s.get("story_points", 0),
            "test_cases": []  # keep empty for now; your engine has epic-level tests
        })
    return {
        "title": epic_obj.get("Epic", ""),
        "stories": stories,
        "test_cases": epic_obj.get("TestCases", [])
    }
