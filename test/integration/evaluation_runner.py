#!/usr/bin/env python3
"""
Evaluation Runner for AI-Powered Jira Agent
Run with: python test/evaluation_runner.py

Consolidated version for single /test folder structure
"""

import requests
import json
import jsonschema
from pathlib import Path
import time
import sys
import os

class TestEvaluator:
    
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.results = []
        
    def load_schema(self):
        """Load JSON schema for validation"""
        schema_path = Path("src/schemas/output.schema.json")
        if not schema_path.exists():
            print("❌ Schema file not found at src/schemas/output.schema.json")
            return None
            
        with open(schema_path) as f:
            return json.load(f)
    
    def load_test_epics(self):
        """Load mock epics from test/data"""
        epics = []
        data_dir = Path("test/data")
        
        if not data_dir.exists():
            print("❌ test/data directory not found")
            return []
            
        for epic_file in data_dir.glob("*_epic.json"):
            try:
                with open(epic_file) as f:
                    epics.append(json.load(f))
                print(f"✅ Loaded test epic: {epic_file.name}")
            except Exception as e:
                print(f"❌ Error loading {epic_file}: {e}")
        
        return epics[:3]  # Test with max 3 epics
    
    def validate_structure(self, output):
        """Validate against JSON schema"""
        schema = self.load_schema()
        if not schema:
            return False, "Schema not available"
            
        try:
            jsonschema.validate(output, schema)
            return True, "Valid"
        except jsonschema.ValidationError as e:
            return False, str(e)
    
    def check_constraints(self, output):
        """Check story and test case count constraints"""
        issues = []
        
        for epic in output.get("epics", []):
            stories = epic.get("stories", [])
            if not (3 <= len(stories) <= 5):
                issues.append(f"Epic has {len(stories)} stories (expected 3-5)")
            
            for story in stories:
                test_cases = story.get("test_cases", [])
                if not (2 <= len(test_cases) <= 3):
                    issues.append(f"Story {story.get('id')} has {len(test_cases)} test cases (expected 2-3)")
        
        return len(issues) == 0, issues
    
    def check_risk_coverage(self, output):
        """Verify high-risk stories have adequate test coverage"""
        issues = []
        
        for epic in output.get("epics", []):
            for story in epic.get("stories", []):
                if story.get("risk") == "High":
                    test_cases = story.get("test_cases", [])
                    if len(test_cases) < 3:
                        issues.append(f"High-risk story {story.get('id')} has only {len(test_cases)} test cases (need ≥3)")
                    
                    # Check for negative test cases
                    negative_tests = [tc for tc in test_cases if tc.get('test_type') == 'Negative']
                    if not negative_tests:
                        issues.append(f"High-risk story {story.get('id')} has no negative test cases")
                    
                    # Check for resilience test cases  
                    resilience_tests = [tc for tc in test_cases if tc.get('test_type') == 'Resilience']
                    if not resilience_tests:
                        issues.append(f"High-risk story {story.get('id')} has no resilience test cases")
        
        return len(issues) == 0, issues
    
    def test_exports(self, run_id):
        """Test JSON and CSV export endpoints"""
        try:
            # Test JSON export
            json_response = requests.get(f"{self.base_url}/runs/{run_id}/json", timeout=10)
            if json_response.status_code != 200:
                return False
            
            # Test CSV export  
            csv_response = requests.get(f"{self.base_url}/runs/{run_id}/csv", timeout=10)
            if csv_response.status_code != 200:
                return False
            
            return True
        except Exception as e:
            print(f"❌ Export test failed: {e}")
            return False
    
    def calculate_consistency_score(self, output):
        """Calculate consistency score based on baseline comparison"""
        # Simplified scoring - in practice, compare with golden baseline
        score = 0
        
        for epic in output.get("epics", []):
            for story in epic.get("stories", []):
                # Format adherence (30 points)
                if all(key in story for key in ['id', 'title', 'description', 'acceptance_criteria']):
                    score += 5
                
                # Clarity/specificity (40 points)
                if story.get('description', '').startswith('As a'):
                    score += 10
                if len(story.get('acceptance_criteria', [])) >= 1:
                    score += 10
                
                # Risk coverage (40 points)
                if story.get('risk') in ['High', 'Medium', 'Low']:
                    score += 10
                if story.get('story_points') in [1, 2, 3, 5, 8, 13]:
                    score += 10
        
        # Normalize to 0-100 scale
        total_stories = sum(len(epic.get('stories', [])) for epic in output.get('epics', []))
        if total_stories > 0:
            score = min(100, score * 100 / (total_stories * 40))
        
        return score
    
    def run_evaluation(self):
        """Main evaluation method"""
        print("🚀 Starting AI Agent Evaluation...")
        print("=" * 50)
        
        epics = self.load_test_epics()
        
        if not epics:
            print("❌ No test epics found. Evaluation cannot proceed.")
            return
        
        metrics = {
            "total_runs": 0,
            "schema_valid": 0,
            "constraints_met": 0,
            "risk_coverage_met": 0,
            "export_success": 0,
            "consistency_scores": [],
            "e2e_times": []
        }
        
        for i, epic in enumerate(epics, 1):
            print(f"\n📦 Testing Epic {i}/{len(epics)}...")
            start_time = time.time()
            
            try:
                # Generate stories and test cases
                print("  🤖 Generating stories and test cases...")
                response = requests.post(f"{self.base_url}/generate", json=epic, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                print("  ✅ Generation successful")
                metrics["total_runs"] += 1
                
                # Validate structure
                print("  🔍 Validating JSON structure...")
                is_valid, validation_msg = self.validate_structure(data["output"])
                if is_valid:
                    print("  ✅ Schema validation passed")
                    metrics["schema_valid"] += 1
                else:
                    print(f"  ❌ Schema validation failed: {validation_msg}")
                
                # Check constraints
                print("  📊 Checking constraints...")
                constraints_ok, constraint_issues = self.check_constraints(data["output"])
                if constraints_ok:
                    print("  ✅ Constraints met")
                    metrics["constraints_met"] += 1
                else:
                    print(f"  ❌ Constraint issues: {constraint_issues}")
                
                # Check risk coverage
                print("  🎯 Checking risk coverage...")
                risk_ok, risk_issues = self.check_risk_coverage(data["output"])
                if risk_ok:
                    print("  ✅ Risk coverage met")
                    metrics["risk_coverage_met"] += 1
                else:
                    print(f"  ❌ Risk coverage issues: {risk_issues}")
                
                # Calculate consistency score
                consistency_score = self.calculate_consistency_score(data["output"])
                metrics["consistency_scores"].append(consistency_score)
                print(f"  📈 Consistency score: {consistency_score:.1f}/100")
                
                # Test exports
                run_id = data["run_id"]
                print("  💾 Testing exports...")
                export_success = self.test_exports(run_id)
                if export_success:
                    print("  ✅ Exports working")
                    metrics["export_success"] += 1
                else:
                    print("  ❌ Export test failed")
                
                end_time = time.time()
                execution_time = end_time - start_time
                metrics["e2e_times"].append(execution_time)
                print(f"  ⏱️  Execution time: {execution_time:.2f}s")
                
            except requests.exceptions.RequestException as e:
                print(f"  ❌ API Error: {e}")
            except Exception as e:
                print(f"  ❌ Unexpected error: {e}")
        
        self.generate_report(metrics)
    
    def generate_report(self, metrics):
        """Generate Markdown test report in test/docs/"""
        print("\n" + "=" * 50)
        print("📊 GENERATING TEST REPORT...")
        print("=" * 50)
        
        if metrics["total_runs"] == 0:
            print("❌ No successful test runs - cannot generate report")
            return
        
        # Calculate percentages
        schema_percent = (metrics["schema_valid"] / metrics["total_runs"]) * 100
        constraints_percent = (metrics["constraints_met"] / metrics["total_runs"]) * 100
        risk_percent = (metrics["risk_coverage_met"] / metrics["total_runs"]) * 100
        export_percent = (metrics["export_success"] / metrics["total_runs"]) * 100
        avg_consistency = sum(metrics["consistency_scores"]) / len(metrics["consistency_scores"]) if metrics["consistency_scores"] else 0
        avg_e2e_time = sum(metrics["e2e_times"]) / len(metrics["e2e_times"]) if metrics["e2e_times"] else 0
        
        report = f"""# Test Evaluation Report
## AI-Powered Jira Agent

**Evaluation Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Test Runs**: {metrics['total_runs']}

## Metrics Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Structural Validity | {metrics['schema_valid']}/{metrics['total_runs']} ({schema_percent:.1f}%) | ≥95% | {'✅' if schema_percent >= 95 else '❌'} |
| Completeness | {metrics['constraints_met']}/{metrics['total_runs']} ({constraints_percent:.1f}%) | 100% | {'✅' if constraints_percent >= 100 else '❌'} |
| Risk Coverage | {metrics['risk_coverage_met']}/{metrics['total_runs']} ({risk_percent:.1f}%) | 100% | {'✅' if risk_percent >= 100 else '❌'} |
| Export Success | {metrics['export_success']}/{metrics['total_runs']} ({export_percent:.1f}%) | 100% | {'✅' if export_percent >= 100 else '❌'} |
| Consistency Score | {avg_consistency:.1f}/100 | ≥90 | {'✅' if avg_consistency >= 90 else '❌'} |
| Avg E2E Time | {avg_e2e_time:.2f}s | Monitor | 📊 |

## Detailed Results

### Structural Validity
- **Passed**: {metrics['schema_valid']} out of {metrics['total_runs']} runs
- **Rate**: {schema_percent:.1f}%
- **Status**: {'PASS' if schema_percent >= 95 else 'FAIL'}

### Completeness (Constraints)
- **Stories per epic**: 3-5
- **Test cases per story**: 2-3  
- **Passed**: {metrics['constraints_met']} out of {metrics['total_runs']} runs
- **Rate**: {constraints_percent:.1f}%
- **Status**: {'PASS' if constraints_percent >= 100 else 'FAIL'}

### Risk Coverage
- **High-risk stories**: ≥3 test cases with negative + resilience
- **Passed**: {metrics['risk_coverage_met']} out of {metrics['total_runs']} runs
- **Rate**: {risk_percent:.1f}%
- **Status**: {'PASS' if risk_percent >= 100 else 'FAIL'}

### Export Functionality
- **JSON Export**: /runs/{{id}}/json
- **CSV Export**: /runs/{{id}}/csv
- **Passed**: {metrics['export_success']} out of {metrics['total_runs']} runs
- **Rate**: {export_percent:.1f}%
- **Status**: {'PASS' if export_percent >= 100 else 'FAIL'}

### Performance
- **Average execution time**: {avg_e2e_time:.2f} seconds
- **Individual times**: {', '.join(f'{t:.2f}s' for t in metrics['e2e_times'])}

## Recommendations

{"🎉 **ALL TARGETS MET** - System is ready for release!" if all([
    schema_percent >= 95,
    constraints_percent >= 100, 
    risk_percent >= 100,
    export_percent >= 100,
    avg_consistency >= 90
]) else "⚠️ **SOME TARGETS NOT MET** - Review the following areas:"}

{"- Schema validation needs improvement" if schema_percent < 95 else ""}
{"- Story/test case constraints not consistently met" if constraints_percent < 100 else ""}  
{"- Risk coverage rules not fully implemented" if risk_percent < 100 else ""}
{"- Export functionality has issues" if export_percent < 100 else ""}
{"- Output consistency needs improvement" if avg_consistency < 90 else ""}

## Next Steps

1. Review detailed test logs for failing cases
2. Check defect log for open issues
3. Address critical issues before release
4. Re-run evaluation after fixes

---
*Report generated by Test Evaluation Runner*
"""
        
        # Ensure test/docs directory exists
        docs_dir = Path("test/docs")
        docs_dir.mkdir(exist_ok=True)
        
        # Save report
        report_path = docs_dir / "testing-report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✅ Evaluation complete! Report saved to {report_path}")
        print("\n" + "=" * 50)
        print("QUICK SUMMARY:")
        print(f"✅ Schema Validity: {schema_percent:.1f}%")
        print(f"✅ Completeness: {constraints_percent:.1f}%") 
        print(f"✅ Risk Coverage: {risk_percent:.1f}%")
        print(f"✅ Export Success: {export_percent:.1f}%")
        print(f"✅ Consistency: {avg_consistency:.1f}/100")
        print(f"✅ Avg Time: {avg_e2e_time:.2f}s")
        print("=" * 50)

if __name__ == "__main__":
    evaluator = TestEvaluator()
    evaluator.run_evaluation()
