A small Flask app that turns Jira epics (or free-text prompts) into Agile user stories and test cases, with JSON export and a simple Chat-style UI. It can run fully offline (mock mode) or with live OpenAI + Jira if credentials are provided.

# Quick start (Mock Mode — no credentials)
-Works entirely offline. Good for a quick demo and for marking.
# Create & activate a virtual environment
```
Windows (PowerShell):
  cd <path-to>\AI
  python -m venv .venv
  .venv\Scripts\activate
macOS/Linux (bash/zsh):
  cd /path/to/AI
  python3 -m venv .venv
source .venv/bin/activate
```
# Install dependencies
` pip install -r requirements.txt `
# Run the Flask server (development)
```
  python -m src.backend.app
  You should see:
    * Running on http://127.0.0.1:5000
```
# Open the UI
```
  Go to http://127.0.0.1:5000/
  You’ll land on the Chat interface (home page).
  Type a prompt like:
    “Generate user stories for an e-commerce checkout with payment and receipt.”
In mock mode the assistant returns schema-valid stories and test cases.
```
# Running tests (VS Code or terminal)
Unit tests
```
  pytest test/unit/test_adapter.py -v
  pytest test/unit/test_ai_engine.py -v
  pytest test/unit/test_chat_agent.py -v
  pytest test/unit/test_exports_csv.py -v
  pytest test/unit/test_validators.py -v
```
# Integration tests
Start the server first in another terminal:
python -m src.backend.app
` python test/integration/evaluation_runner.py `

































