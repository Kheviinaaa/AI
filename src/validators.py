# ---------------------------------------------------------
# validators.py  (FINAL FIXED VERSION)
# Handles JSON schema validation with absolute file paths.
# ---------------------------------------------------------
import json
import os
from jsonschema import validate, ValidationError, RefResolver

def load_schemas():
    """
    Loads all schema files from /src with absolute file:// paths
    so that jsonschema can resolve $ref links on Windows too.
    """
    base_dir = os.path.dirname(__file__)

   # Absolute paths to schema files
    output_path = os.path.abspath(os.path.join(base_dir, "output.schema.json"))
    story_path = os.path.abspath(os.path.join(base_dir, "story.schema.json"))
    test_path = os.path.abspath(os.path.join(base_dir, "test.schema.json"))

    # Ensure all files exist
    for path in [output_path, story_path, test_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Missing schema file: {path}")

    # Load each schema
    with open(output_path, "r", encoding="utf-8") as f:
        output_schema = json.load(f)
    with open(story_path, "r", encoding="utf-8") as f:
        story_schema = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_schema = json.load(f)

    # Map absolute file URIs to schemas for the resolver
    schema_store = {
        f"file:///{output_path.replace(os.sep, '/')}": output_schema,
        f"file:///{story_path.replace(os.sep, '/')}": story_schema,
        f"file:///{test_path.replace(os.sep, '/')}": test_schema,
    }

    resolver = RefResolver(
        base_uri=f"file:///{base_dir.replace(os.sep, '/')}/",
        referrer=output_schema,
        store=schema_store,
    )

    return output_schema, resolver


def validate_output(json_data):
    """
    Validate AI-generated JSON output against output.schema.json.
    Returns (is_valid, errors)
    """
    try:
        schema, resolver = load_schemas()
        validate(instance=json_data, schema=schema, resolver=resolver)
        return True, []
    except ValidationError as e:
        msg = f"Schema validation failed at {list(e.path)}: {e.message}"
        return False, [msg]
    except Exception as e:
        msg = f"Unexpected error during validation: {str(e)}"
        return False, [msg]
    
# ---------------------------------------------------------
# Debug / Manual Test Mode
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n--- Manual Validation Test ---")

    base_dir = os.path.dirname(__file__)
    sample_file = os.path.join(base_dir, "out", "sample_output.json")

    # Make sure the file exists
    if not os.path.exists(sample_file):
        print("⚠️  sample_output.json not found. Run ai_engine.py first.")
        input("\nPress any key to exit...")
        exit()

    # Load the sample output
    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Run validation
    is_valid, errors = validate_output(data)

    # Show result
    if is_valid:
        print("Validation Result: PASS ✅\n")
    else:
        print("Validation Result: FAIL ❌\n")
        print("Errors:")
        for e in errors:
            print(" -", e)

    input("\nPress any key to close...")