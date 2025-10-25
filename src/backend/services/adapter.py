def adapt_ai_engine_epic(epic_obj: dict) -> dict:
    """
    Input shape (from your ai_engine.py mock/real):
      {
        "Epic": "Title",
        "UserStories": [{title, description, acceptance_criteria{Given,When,Then}, story_points}, ...],
        "TestCases": [{id, objective, expected_result}, ...]
      }
    Output shape (what your CSV formatter expects):
       {
        "epic_id": str,
        "title": str,
        "stories": [...],
        "test_cases": [...]
      }
    """
    stories = []
    for i, s in enumerate(epic_obj.get("UserStories", []), start=1):
        ac = s.get("acceptance_criteria", {}) if isinstance(s, dict) else {}
        stories.append(
            {
                "story_id": f"US-{i:02d}",
                "title": s.get("title", "") if isinstance(s, dict) else str(s),
                "description": s.get("description", "") if isinstance(s, dict) else "",
                "acceptance_criteria": {
                    "Given": ac.get("Given", ""),
                    "When": ac.get("When", ""),
                    "Then": ac.get("Then", ""),
                },
                "story_points": s.get("story_points", 0) if isinstance(s, dict) else 0,
            }
        )

    tests = []
    for case in epic_obj.get("TestCases", []):
        steps = case.get("test_steps", []) if isinstance(case, dict) else []
        if isinstance(steps, str):
            steps = [steps]
        tests.append(
            {
                "id": case.get("id", "") if isinstance(case, dict) else str(case),
                "objective": case.get("objective", "") if isinstance(case, dict) else "",
                "preconditions": case.get("preconditions", "") if isinstance(case, dict) else "",
                "test_steps": steps,
                "expected_result": case.get("expected_result", "") if isinstance(case, dict) else "",
            }
        )

    return {
        "epic_id": epic_obj.get("epic_id"),
        "title": epic_obj.get("Epic", ""),
        "stories": stories,
        "test_cases": tests,
    }
