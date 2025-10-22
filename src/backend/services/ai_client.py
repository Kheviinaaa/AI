# src/services/ai_client.py
import uuid
import datetime
from models.schemas import GenerateRequest
import ai_engine # ✅ imported from your uploaded ai_engine.py


def generate_from_payload(payload):
    """
    Takes the incoming JSON payload, validates it with Pydantic,
    sends each epic to the AI engine, and combines the results.
    """
    # Validate input structure
    req = GenerateRequest(**payload)

    all_outputs = []

    # Loop through each epic in the request
    for epic in req.epics:
        # Combine title + description into a single text block for AI
        epic_text = f"{epic.title}: {epic.description or ''}"

        # Call AI engine to generate user stories + test cases
        ai_output = ai_engine.generate_user_stories(epic_text)

        # Optional: run validation to ensure correct structure
        if not ai_engine.validate_output(ai_output):
            print(f"⚠️ Validation failed for epic: {epic.title}")

        all_outputs.append(ai_output)

    # Post-process to clean duplicates
    final_output = ai_engine.post_process(all_outputs)

    # Package as a backend run record
    return {
        "run_id": str(uuid.uuid4()),
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "output": {
            "epics": final_output
        }
    }
