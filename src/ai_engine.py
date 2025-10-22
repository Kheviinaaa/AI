# ---------------------------------------------------------
# AI Engineer 1 – E-Commerce Checkout System
# This module generates User Stories and Test Cases using an AI model.
# It supports multiple-epic batching, post-processing, and validation.
# If the OpenAI API key is unavailable, it uses mock data for testing/demo.
# ---------------------------------------------------------

from openai import OpenAI
import os, json

# ---------------------------------------------------------
# 1. Create a client connection to OpenAI using the environment variable key
# ---------------------------------------------------------
client = None
# ---------------------------------------------------------
# 2. Define the prompt template the AI will receive
# ---------------------------------------------------------
PROMPT = (
    "Given the epic: {epic}, generate user stories and test cases "
    "in Agile format. Each story must include Title, Description, "
    "Acceptance Criteria (Given/When/Then), and Story Points (1–13). "
    "Each test case must include ID, Objective, and Expected Result. "
    "Return the output as structured JSON."
)

# ---- helper: make model JSON safe to parse -----------------------------------
def _safe_json_loads(text: str):
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

# ---------------------------------------------------------
# 3. Function: generate_user_stories(epic_text)
#    - Sends the formatted prompt to the AI model.
#    - Returns JSON with User Stories and Test Cases.
#    - If the API is unavailable or quota exceeded, returns mock data.
# ---------------------------------------------------------
def generate_user_stories(epic_text: str, epic_title: str | None = None):
    """
    Returns: dict with keys 'Epic', 'UserStories', 'TestCases' as your schema expects.
    Uses real OpenAI if client is available; otherwise returns your mock.
    """
    # If no client (no OPENAI_API_KEY), use your existing mock
    if client is None:
        print(" API unavailable, using mock output: OpenAI client not initialized")
        return {
            "Epic": epic_title or epic_text,
            "UserStories": [
                {
                    "title": "Review Cart Items",
                    "description": "As a user, I want to review items in my cart so I can confirm my purchase before payment.",
                    "acceptance_criteria": {
                        "Given": "User has items in cart",
                        "When": "User opens the cart page",
                        "Then": "Items and prices display correctly"
                    },
                    "story_points": 5
                },
                {
                    "title": "Enter Billing and Shipping Details",
                    "description": "As a user, I want to enter billing and shipping details to complete my purchase.",
                    "acceptance_criteria": {
                        "Given": "User proceeds to checkout",
                        "When": "User fills billing and shipping info",
                        "Then": "Details are saved and validated"
                    },
                    "story_points": 8
                },
                {
                    "title": "Process Secure Payment",
                    "description": "As a user, I want to make a secure payment so my order is successfully completed.",
                    "acceptance_criteria": {
                        "Given": "User is on checkout page",
                        "When": "Valid card details are entered",
                        "Then": "System confirms payment"
                    },
                    "story_points": 8
                },
                {
                    "title": "Generate Digital Receipt",
                    "description": "As a system, I want to generate a digital receipt automatically after successful payment.",
                    "acceptance_criteria": {
                        "Given": "Payment is confirmed",
                        "When": "Order is completed",
                        "Then": "Receipt is created and emailed to user"
                    },
                    "story_points": 3
                },
                {
                    "title": "View Completed Orders",
                    "description": "As an admin, I want to view all completed orders for tracking purposes.",
                    "acceptance_criteria": {
                        "Given": "Admin logs into dashboard",
                        "When": "Admin navigates to Orders section",
                        "Then": "All completed orders are displayed"
                    },
                    "story_points": 5
                }
            ],
            "TestCases": [
                {
                    "id": "TC01",
                    "objective": "Validate cart review page",
                    "expected_result": "Items and prices display correctly"
                },
                {
                    "id": "TC02",
                    "objective": "Verify payment process",
                    "expected_result": "Payment accepted and confirmation shown"
                },
                {
                    "id": "TC03",
                    "objective": "Check receipt generation",
                    "expected_result": "Receipt is created and sent to the user after successful payment"
                }
            ]
        }

    # Real API path with retries and JSON repair
    msg = PROMPT.format(epic=epic_text)
    last_err = None
    for attempt in range(1, 4):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": msg}],
                temperature=0.4,
                response_format={"type": "json_object"},   # ✅ add this line
            )

            content = resp.choices[0].message.content

            data = _safe_json_loads(content)
            # Normalize to your schema
            data.setdefault("UserStories", [])
            data.setdefault("TestCases", [])
            # Ensure story_points numeric and clamp 1..13; ensure AC keys exist
            for s in data["UserStories"]:
                sp = s.get("story_points", 3)
                try:
                    sp = int(sp)
                except Exception:
                    sp = 3
                s["story_points"] = max(1, min(13, sp))

                ac = s.get("acceptance_criteria") or {}
                s["acceptance_criteria"] = {
                    "Given": ac.get("Given", ""),
                    "When": ac.get("When", ""),
                    "Then": ac.get("Then", "")
                }

            # Stamp Epic field
            data["Epic"] = epic_title or data.get("Epic") or epic_text
            return data

        except Exception as e:
            last_err = e
            # simple backoff
            import time, random
            time.sleep(0.6 * attempt + random.uniform(0, 0.2))

    # Fallback to your mock if all attempts fail
    print(" API unavailable, using mock output:", last_err)
    return {
        "Epic": epic_title or epic_text,
        "UserStories": [
            {
                "title": "Review Cart Items",
                "description": "As a user, I want to review items in my cart so I can confirm my purchase before payment.",
                "acceptance_criteria": {
                    "Given": "User has items in cart",
                    "When": "User opens the cart page",
                    "Then": "Items and prices display correctly"
                },
                "story_points": 5
            }
        ],
        "TestCases": [
            {"id": "TC01", "objective": "Cart page loads", "expected_result": "Items and totals render"}
        ]
    }


# ---------------------------------------------------------
# 5. Helper Function: validate_output()
#    - Checks that required fields exist in user stories and test cases
# ---------------------------------------------------------
def validate_output(data):
    required_story_fields = {"title", "description", "acceptance_criteria", "story_points"}
    required_test_fields = {"id", "objective", "expected_result"}
    valid = True

    if "UserStories" in data:
        for story in data["UserStories"]:
            if not required_story_fields.issubset(story.keys()):
                valid = False

    if "TestCases" in data:
        for test in data["TestCases"]:
            if not required_test_fields.issubset(test.keys()):
                valid = False

    return valid

# ---------------------------------------------------------
# 6. Helper Function: post_process()
#    - Removes duplicate epics and cleans data
# ---------------------------------------------------------
def post_process(all_outputs):
    seen_titles = set()
    cleaned = []
    for epic_data in all_outputs:
        title = epic_data.get("Epic", "").strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            cleaned.append(epic_data)
    return cleaned

# ---------------------------------------------------------
# Simulated Jira Integration (for demo)
# ---------------------------------------------------------
def fetch_epics_from_jira(project_key="ECOM"):
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
        result = generate_user_stories(epic["description"], epic.get("title"))
        all_outputs.append(result)

    # c) Run post-processing and validation
    print("\n Running post-processing and validation checks...")
    cleaned_outputs = post_process(all_outputs)
    validation_results = []

    for epic_data in cleaned_outputs:
        ok = validate_output(epic_data)
        validation_results.append({"Epic": epic_data.get("Epic"), "Valid": ok})

    # d) Save all outputs and validation summary
    os.makedirs("out", exist_ok=True)  # create folder if missing

    with open("out/sample_output.json", "w") as f:
        json.dump(cleaned_outputs, f, indent=2)

    with open("out/validation_report.json", "w") as f:
        json.dump(validation_results, f, indent=2)

    print(" Post-processing complete. Validation results saved to validation_report.json.")
    print(" All epics processed successfully! Output saved to sample_output.json.")