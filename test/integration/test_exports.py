import pytest
import requests
import json
import csv
from pathlib import Path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

class TestExportEndpoints:
    
    BASE_URL = "http://localhost:5000/api"
    
    def setup_method(self):
        """Create a test run first that we can export"""
        epic_data = {
            "epic": {
                "id": "EPIC-EXPORT-TEST",
                "title": "Export Test Epic",
                "description": "Test epic for export functionality",
                "key_requirements": ["Test requirement"]
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/generate", json=epic_data)
        if response.status_code == 200:
            self.run_id = response.json()["run_id"]
        else:
            self.run_id = "test-run-123"  # Fallback for testing
    
    def test_export_json(self):
        """TC-EXPORT-JSON-001: JSON export endpoint"""
        response = requests.get(f"{self.BASE_URL}/runs/{self.run_id}/json")
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'
        
        # Try to parse as JSON to validate structure
        data = response.json()
        assert "run_id" in data
        assert "output" in data
    
    def test_export_csv(self):
        """TC-EXPORT-CSV-002: CSV Flattening"""
        response = requests.get(f"{self.BASE_URL}/runs/{self.run_id}/csv")
        
        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']
        
        # Parse CSV to validate structure
        content = response.text
        lines = content.strip().split('\n')
        assert len(lines) > 1  # Header + at least one data row
        
        # Check for expected columns
        header = lines[0]
        expected_columns = ['test_case_id', 'story_id', 'story_title']
        for col in expected_columns:
            assert col in header
    
    def test_export_nonexistent_run(self):
        """Test export for non-existent run ID"""
        response = requests.get(f"{self.BASE_URL}/runs/nonexistent-run-999/json")
        
        # Should return 404 or appropriate error
        assert response.status_code in [404, 400]
    
    def test_export_content_validation(self):
        """Validate that exported content matches generated content"""
        # First get the run data
        json_response = requests.get(f"{self.BASE_URL}/runs/{self.run_id}/json")
        if json_response.status_code == 200:
            json_data = json_response.json()
            
            # Get CSV and verify it contains the same stories
            csv_response = requests.get(f"{self.BASE_URL}/runs/{self.run_id}/csv")
            if csv_response.status_code == 200:
                csv_content = csv_response.text
                # Basic check - CSV should contain story IDs from JSON
                story_ids = [story["id"] for story in json_data["output"]["epics"][0]["stories"]]
                for story_id in story_ids:
                    assert story_id in csv_content
