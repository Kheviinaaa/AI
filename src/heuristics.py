# ---------------------------------------------------------
# heuristics.py
# Compute evaluation metrics for AI output
# ---------------------------------------------------------
def compute_metrics(data):
    """Compute completeness, risk coverage, and consistency metrics."""
    metrics = {
        "Story Count Completeness": 0.0,
        "Test Case Coverage": 0.0,
        "Acceptance Criteria Quality": 0.0,
        "Overall Consistency Score": 0.0,
    }

    # Handle array or single object
    epics = data if isinstance(data, list) else [data]
    if not epics:
        return metrics

    # Completeness → checks if user stories exist
    total_stories = sum(len(epic.get("UserStories", [])) for epic in epics)
    metrics["Story Count Completeness"] = 100.0 if total_stories >= 3 else (total_stories / 3) * 100

    # Risk Coverage → placeholder (no risk field in JSON)
    total_tests = sum(len(epic.get("TestCases", [])) for epic in epics)
    metrics["Test Case Coverage"] = 100.0 if total_tests >= total_stories else (
        (total_tests / total_stories) * 100 if total_stories else 0.0
    )

    # Acceptance criteria quality – percentage of stories with all three clauses filled.
    if total_stories:
        ac_complete = 0
        for epic in epics:
            for story in epic.get("UserStories", []):
                ac = story.get("acceptance_criteria", {})
                if all(ac.get(part, "").strip() for part in ("Given", "When", "Then")):
                    ac_complete += 1
        metrics["Acceptance Criteria Quality"] = (ac_complete / total_stories) * 100

    # Consistency Score → derived average
    metrics["Overall Consistency Score"] = round(
        (
            metrics["Story Count Completeness"] * 0.4
            + metrics["Test Case Coverage"] * 0.3
            + metrics["Acceptance Criteria Quality"] * 0.3
        ),
        1,
    )

    return metrics
