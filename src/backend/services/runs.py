import json, os
OUT_DIR = os.getenv("EXPORT_DIR", "./runs_data")
os.makedirs(OUT_DIR, exist_ok=True)

def store(run):
    path = os.path.join(OUT_DIR, f"{run['run_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2)
    return path

def get(run_id):
    path = os.path.join(OUT_DIR, f"{run_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)