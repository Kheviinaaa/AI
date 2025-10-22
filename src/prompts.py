# prompts.py — AI Engineer 1
# Stores system and user prompts used by ai_engine.py

SYSTEM_PROMPT = "You are an Agile AI assistant that generates user stories and test cases."

USER_PROMPT_TEMPLATE = (
    "Given the following epic: {epic}\n"
    "Generate user stories and test cases in Agile format.\n"
    "Each story must include Title, Description, Acceptance Criteria (Given/When/Then), "
    "and Story Points (1–13). Each test case must include ID, Objective, Expected Result.\n"
    "Return valid JSON with keys 'UserStories' and 'TestCases'."
)
