from __future__ import annotations
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import pathlib
env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"  # project_root/.env
load_dotenv(find_dotenv())

import json
import logging
import random
import time
from typing import Any, Dict, Iterable, List

try:  # Support execution via ``python src/ai_engine.py`` and ``-m src.ai_engine``
    from src.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
except ImportError:  # pragma: no cover - defensive import for script usage
    from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE  # type: ignore

try:
    from src.validators import validate_output as schema_validate_output
except ImportError:  # pragma: no cover - defensive import for script usage
    from validators import validate_output as schema_validate_output  # type: ignore

_client: OpenAI | None = None

def _initialise_client() -> OpenAI | None:
    """Create (or reuse) an OpenAI client when credentials are present."""

    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        logging.info("OpenAI client unavailable – running in mock mode.")
        return None

    try:
        _client = OpenAI(api_key=api_key)
        logging.info("OpenAI client initialised successfully.")
    except Exception as exc:  # pragma: no cover - depends on runtime environment
        logging.warning("Failed to initialise OpenAI client: %s", exc)
        _client = None

    return _client


def using_live_model() -> bool:
    """Expose whether the engine is currently backed by OpenAI."""

    return _initialise_client() is not None


def _safe_json_loads(text: str) -> Dict[str, Any]:
    """
    Try to parse JSON. If the model wrapped it in prose or code fences,
    strip and extract the first top-level {...} block.
    """
    import json
    try:
        return json.loads(text)
    except Exception:
        cleaned = text.strip()

        # Strip Markdown code fences if present
        if cleaned.startswith("```"):
            # remove leading/trailing backticks fences
            cleaned = cleaned.strip("`").strip()
        # Extract first {...}
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = cleaned[first:last+1]
            return json.loads(candidate)
        # If we get here, let the caller fall back to mock
        raise


def _mock_user_stories(epic_text: str, epic_title: str | None) -> Dict[str, Any]:
    """
    Smarter mock generator:
    - Derives story titles from the epic text
    - Produces 5 concrete stories with non-empty fields
    - Creates mapped test cases
    """
    import re
    title = (epic_title or epic_text or "Epic").strip()
    title = re.sub(r"^\s*(generate|create)\s+user\s+stories\s+for\s+", "", title, flags=re.I)[:60] or "Epic"

    # Seed defaults (switch to auth flavor if prompt mentions auth)
    seeds = [
        "Review items in cart",
        "Enter shipping & billing info",
        "Secure payment",
        "Order confirmation & receipt",
        "Order history view",
    ]
    if any(k in (epic_text or "").lower() for k in ["auth", "login", "signup", "reset"]):
        seeds = [
            "Signup with email",
            "Login with credentials",
            "Forgot/reset password",
            "Session timeout & logout",
            "Update profile",
        ]

    def mk(seed: str, sp: int) -> Dict[str, Any]:
        s = seed[0].upper() + seed[1:]
        return {
            "title": s,
            "description": f"As a user, I want to {seed.lower()} so I can complete the flow in the epic.",
            "acceptance_criteria": {
                "Given": f"The user is on the page for {seed.lower()}",
                "When":  f"The user performs the {seed.lower()} action",
                "Then":  f"The system completes {seed.lower()} and shows a clear result",
            },
            "story_points": sp,
        }

    sps = [3, 5, 8, 5, 3]
    stories = [mk(seeds[i % len(seeds)], sps[i]) for i in range(5)]

    tests = []
    for i, s in enumerate(stories, start=1):
        tests.append({
            "id": f"TC-{i:02d}",
            "objective": f"Validate: {s['title']}",
            "preconditions": "System under test is available",
            "test_steps": [
                f"Navigate to the page for {s['title'].lower()}",
                f"Perform the action: {s['title'].lower()}",
                "Verify the outcome is displayed",
            ],
            "expected_result": "Application behaves according to acceptance criteria",
        })

    return {
        "Epic": title,
        "epic_id": None,
        "description": epic_text,
        "UserStories": stories,
        "TestCases": tests,
    }

def _normalise_user_stories(raw: Dict[str, Any], epic_title: str | None, epic_id: str | None, epic_description: str | None) -> Dict[str, Any]:
    """Normalise the response from the model (or mock) into schema-compliant JSON."""

    stories = []
    for story in raw.get("UserStories", []) or []:
        if not isinstance(story, dict):
            continue
        sp = story.get("story_points", 3)
        try:
            sp = int(sp)
        except Exception:
            sp = 3
        sp = max(1, min(13, sp))

        ac = story.get("acceptance_criteria") or {}
        if isinstance(ac, list):
            # Occasionally models return a list of clauses – map heuristically.
            mapped = {"Given": "", "When": "", "Then": ""}
            for clause in ac:
                if not isinstance(clause, str):
                    continue
                lower = clause.lower()
                if "given" in lower and not mapped["Given"]:
                    mapped["Given"] = clause
                elif "when" in lower and not mapped["When"]:
                    mapped["When"] = clause
                elif "then" in lower and not mapped["Then"]:
                    mapped["Then"] = clause
            ac = mapped
        stories.append(
            {
                "title": story.get("title", "").strip(),
                "description": story.get("description", "").strip(),
                "acceptance_criteria": {
                    "Given": (ac or {}).get("Given", ""),
                    "When": (ac or {}).get("When", ""),
                    "Then": (ac or {}).get("Then", ""),
                },
                "story_points": sp,
            }
        )

    test_cases = []
    for index, case in enumerate(raw.get("TestCases", []) or [], start=1):
        if isinstance(case, str):
            case = {"objective": case}
        if not isinstance(case, dict):
            continue

        steps = case.get("test_steps") or case.get("steps") or case.get("actions") or []
        if isinstance(steps, str):
            steps = [s.strip() for s in steps.split("\n") if s.strip()]
        elif isinstance(steps, Iterable):
            steps = [str(s).strip() for s in steps if str(s).strip()]
        else:
            steps = []

        objective = case.get("objective", "").strip() or case.get("name", "").strip()
        preconditions = case.get("preconditions", "").strip()
        expected = case.get("expected_result", "").strip()

        test_cases.append(
            {
                "id": str(case.get("id") or f"TC-{index:02d}"),
                "objective": objective or "Validate critical scenario",
                "preconditions": preconditions or "System under test is available",
                "test_steps": steps or ["Execute the described scenario"],
                "expected_result": expected or "Application behaves according to acceptance criteria",
            }
        )

    result = {
        "Epic": epic_title or raw.get("Epic") or "",
        "epic_id": epic_id,
        "description": epic_description or raw.get("description") or "",
        "UserStories": stories,
        "TestCases": test_cases,
    }

    return result


def generate_user_stories(
    epic_text: str,
    epic_title: str | None = None,
    *,
    epic_id: str | None = None,
    epic_description: str | None = None,
) -> Dict[str, Any]:
    """Generate user stories and test cases for an epic.

    The return value always matches ``output.schema.json`` (a list element) so
    that downstream code can directly run schema validation.
    """

    client = _initialise_client()
    if client is None:
        logging.info("Using deterministic mock output for epic: %s", epic_title or epic_text)
        raw = _mock_user_stories(epic_text, epic_title)
        return _normalise_user_stories(raw, epic_title, epic_id, epic_description)

    prompt = USER_PROMPT_TEMPLATE.format(epic=epic_text)
    last_error: Exception | None = None

    for attempt in range(1, 4):  # simple retry with backoff
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            raw = _safe_json_loads(content)
            raw.setdefault("UserStories", [])
            raw.setdefault("TestCases", [])
            return _normalise_user_stories(raw, epic_title, epic_id, epic_description)
        except Exception as exc:  # pragma: no cover - network dependent
            last_error = exc
            sleep_time = 0.6 * attempt + random.uniform(0, 0.2)
            logging.warning("OpenAI call failed (attempt %s): %s", attempt, exc)
            time.sleep(sleep_time)

    logging.error("Falling back to mock output after OpenAI errors: %s", last_error)
    raw = _mock_user_stories(epic_text, epic_title)
    return _normalise_user_stories(raw, epic_title, epic_id, epic_description)


# ---------------------------------------------------------
# 5. Helper Function: validate_output()
#    - Checks that required fields exist in user stories and test cases
# ---------------------------------------------------------
def validate_output(data: Any) -> bool:
    """Validate generated data against the JSON schema bundle."""

    payload: List[Dict[str, Any]]
    if isinstance(data, dict):
        payload = [data]
    else:
        payload = list(data)

    is_valid, _errors = schema_validate_output(payload)
    return bool(is_valid)

# ---------------------------------------------------------
# 6. Helper Function: post_process()
#    - Removes duplicate epics and cleans data
# ---------------------------------------------------------
def post_process(all_outputs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[str] = set()
    cleaned: List[Dict[str, Any]] = []
    for epic_data in all_outputs:
        epic_id = str(epic_data.get("epic_id") or "").lower()
        title = str(epic_data.get("Epic") or "").strip().lower()
        key = epic_id or title
        if not key:
            cleaned.append(epic_data)
            continue
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(epic_data)
    return cleaned

# ---------------------------------------------------------
# Simulated Jira Integration (for demo)
# ---------------------------------------------------------
def fetch_epics_from_jira(project_key: str = "ECOM") -> List[Dict[str, str]]:
    """
    Simulated Jira fetch function for demonstration.
    In a real system, this would use Jira's REST API to retrieve epics.
    """
    print(f"🔹 Simulated Jira fetch for project: {project_key}")
    epics = [
        {"title": "E-Commerce Checkout System",
         "description": "Build checkout flow with payment gateway."},
        {"title": "User Authentication",
         "description": "Add secure login and signup functionality."},
        {"title": "Order Management",
         "description": "Enable users to view and manage their orders."}
    ]
    return epics

# ---------------------------------------------------------
# 7. Main Program: handles multi-epic batching,
#    post-processing, and validation.
# ---------------------------------------------------------
if __name__ == "__main__":
    # a) Define multiple epics for batch processing
    epics = fetch_epics_from_jira("ECOM")

    all_outputs = []

    # b) Loop through each epic and generate results
    for epic in epics:
        print(f" Processing epic: {epic['title']} ...")
        result = generate_user_stories(
            epic["description"],
            epic.get("title"),
            epic_id=epic.get("epic_id"),
            epic_description=epic.get("description"),
        )
        all_outputs.append(result)

    # c) Run post-processing and validation
    print("\n Running post-processing and validation checks...")
    cleaned_outputs = post_process(all_outputs)
    validation_results = []

    for epic_data in cleaned_outputs:
        ok = validate_output(epic_data)
        validation_results.append({"Epic": epic_data.get("Epic"), "Valid": ok})

    # d) Save all outputs and validation summary
    base_dir = os.path.dirname(__file__)
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "sample_output.json"), "w", encoding="utf-8") as f:
        json.dump(cleaned_outputs, f, indent=2)

    with open(os.path.join(out_dir, "validation_report.json"), "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2)

    print(" Post-processing complete. Validation results saved to validation_report.json.")
    print(" All epics processed successfully! Output saved to sample_output.json.")
