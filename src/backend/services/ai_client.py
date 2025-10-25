"""Functions that coordinate AI generation for the Flask routes."""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict

try:  # Support package imports as well as running the file directly
    from src.backend.models.schemas import GenerateRequest
    from src import ai_engine
except ImportError:  # pragma: no cover - defensive fallback for script usage
    from backend.models.schemas import GenerateRequest  # type: ignore
    import ai_engine  # type: ignore


def _epic_to_prompt(title: str, description: str | None) -> str:
    description = (description or "").strip()
    if description:
        return f"{title}\n\nDescription:\n{description}"
    return title


def generate_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the request payload, call the AI engine, and aggregate results."""

    req = GenerateRequest(**payload)

    generated = []
    for epic in req.epics:
        epic_text = _epic_to_prompt(epic.title, epic.description)
        ai_output = ai_engine.generate_user_stories(
            epic_text,
            epic_title=epic.title,
            epic_id=epic.epic_id,
            epic_description=epic.description,
        )

        if not ai_engine.validate_output(ai_output):
            # Log a warning but continue so the request succeeds with as much data
            # as possible. Schema validation errors will be reported in the run.
            print(f"⚠️ Validation failed for epic: {epic.title}")

        generated.append(ai_output)

    final_output = ai_engine.post_process(generated)
    validation_passed = ai_engine.validate_output(final_output)

    run_record = {
        "run_id": str(uuid.uuid4()),
        "project_name": req.project_name,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "mode": "live" if ai_engine.using_live_model() else "mock",
        "epics": [epic.dict() for epic in req.epics],
        "constraints": req.constraints.dict(exclude_none=True) if req.constraints else None,
        "output": {"epics": final_output},
        "validation": {"schema_passed": validation_passed},
    }

    return run_record
