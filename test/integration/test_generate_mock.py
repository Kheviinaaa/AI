import pytest
import requests
import json
from pathlib import Path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

class TestGenerateFromMock:
    
    BASE_URL = "http://localhost:5000/api"
    
    def load_test_data(self, filename):
        """Load test data from test/data folder"""
        data_path = Path("test/data") / filename
        with open(data_path) as f:
            return json.load(f)
    
    def test_generate_from_mock_happy_path(self):
        """TC-API-GEN-001: Generate from Mock (Happy Path)"""
        epic_data = self.load_test_data("checkout_epic.json")
        
        response = requests.post(f"{self.BASE_URL}/generate", json=epic_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "run_id" in data
        assert "output" in data
        assert "epics" in data["output"]
        
        stories = data["output"]["epics"][0]["stories"]
        
        # Validate constraints
        assert 3 <= len(stories) <= 5, f"Expected 3-5 stories, got {len(stories)}"
        
        for story in stories:
            test_cases = story.get("test_cases", [])
            assert 2 <= len(test_cases) <= 3, f"Expected 2-3 test cases per story, got {len(test_cases)}"
            
            # Validate story has required fields
            assert "id" in story
            assert "title" in story
            assert "description" in story
            assert "acceptance_criteria" in story
            assert len(story["acceptance_criteria"]) >= 1
    
    def test_generate_empty_epic(self):
        """Test error handling for empty epic input"""
        response = requests.post(f"{self.BASE_URL}/generate", json={"epics": []})
        
        assert response.status_code == 400
        error_data = response.json()
        assert "error" in error_data
    
    def test_generate_with_missing_fields(self):
        """Test with epic missing required fields"""
        invalid_epic = {
            "epic": {
                "title": "Incomplete Epic"
                # Missing description, key_requirements, etc.
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/generate", json=invalid_epic)
        # Should either handle gracefully or return error
        assert response.status_code in [200, 400]
    
    def test_generate_multiple_epics(self):
        """Test batch processing of multiple epics"""
        epic1 = self.load_test_data("checkout_epic.json")
        epic2 = {
            "epic": {
                "id": "EPIC-002",
                "title": "User Registration",
                "description": "User registration system",
                "key_requirements": ["Email validation", "Password strength"]
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/generate", json={"epics": [epic1["epic"], epic2["epic"]]})
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["output"]["epics"]) == 2
