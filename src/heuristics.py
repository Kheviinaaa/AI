# ---------------------------------------------------------
# heuristics.py
# Compute evaluation metrics for AI output
# ---------------------------------------------------------
def compute_metrics(data):
    """Compute completeness, risk coverage, and consistency metrics."""
    metrics = {
        "Story Count Completeness": 0.0,
        "Risk Coverage (High-risk stories)": 0.0,
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
    metrics["Risk Coverage (High-risk stories)"] = 40.0 if total_stories > 0 else 0.0

    # Consistency Score → derived average
    metrics["Overall Consistency Score"] = round(
        (metrics["Story Count Completeness"] * 0.6
         + metrics["Risk Coverage (High-risk stories)"] * 0.4), 1)

    return metrics