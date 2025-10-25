# ---------------------------------------------------------
# evaluation.py
# ---------------------------------------------------------
import json
import os

try:
    from src.validators import validate_output
    from src.heuristics import compute_metrics
except ImportError:  # pragma: no cover - fallback when run as script
    from validators import validate_output  # type: ignore
    from heuristics import compute_metrics  # type: ignore

def load_output(path):
    """Load JSON output from ai_engine.py."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in: {path}")
        return None


def run_evaluation():
    print("\n--- Running AI Generation Evaluation ---")

    base_dir = os.path.dirname(__file__)
    output_path = os.path.join(base_dir, "out", "sample_output.json")
    report_path = os.path.join(base_dir, "out", "evaluation_report.json")

    # Step 1: Load output
    output_data = load_output(output_path)
    if not output_data:
        print("⚠️ No valid AI output found. Run ai_engine.py first.")
        return

    print("Step 1: Loading AI output...")
    print("Step 2: Validating and computing metrics...")

    # Step 2: Validate JSON
    is_valid, errors = validate_output(output_data)
    structural_validity = 100.0 if is_valid else 0.0

    # Step 3: Compute metrics
    metrics = compute_metrics(output_data)
    metrics["Structural Validity (passes schema)"] = structural_validity

    # Step 4: Print summary
    print("\n--- Evaluation Summary ---")
    for key, value in metrics.items():
        print(f" - {key}: {value:.1f}%")
    print("---------------------------")

    # Step 5: Save results
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n✅ Evaluation complete. Report saved to: {report_path}")

    # Optional: show validation errors
    if errors:
        print("\n⚠️ Validation Errors:")
        for e in errors:
            print(" -", e)


if __name__ == "__main__":
    run_evaluation()
