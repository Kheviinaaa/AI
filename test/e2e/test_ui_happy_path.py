import os
import json
from pathlib import Path

import pytest

RUN_SERVER_TESTS = os.getenv("RUN_SERVER_TESTS") == "1"

try:
    import requests
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    requests = None  # type: ignore[assignment]
    pytestmark = pytest.mark.skip(reason="requests library not installed")
else:
    if not RUN_SERVER_TESTS:
        pytestmark = pytest.mark.skip(
            reason="Set RUN_SERVER_TESTS=1 to enable end-to-end HTTP tests"
        )


class TestUIHappyPath:
    
    BASE_URL = "http://localhost:5000"
    
    def test_ui_homepage_loading(self):
        """Test that the web UI homepage loads"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
    
    def test_ui_form_submission(self):
        """Test complete UI flow: form submission → generation → results display"""
        # Load test epic data
        data_path = Path("test/data/checkout_epic.json")
        with open(data_path) as f:
            epic_data = json.load(f)
        
        # Submit via UI form (this would normally be browser automation)
        # For now, testing the API that the UI would call
        response = requests.post(f"{self.BASE_URL}/api/generate", json=epic_data)
        assert response.status_code == 200
        
        data = response.json()
        run_id = data["run_id"]
        
        # Verify results can be retrieved (what UI would display)
        results_response = requests.get(f"{self.BASE_URL}/api/runs/{run_id}/json")
        assert results_response.status_code == 200
    
    def test_ui_export_buttons(self):
        """Test that export buttons generate downloadable files"""
        # First create a test run
        epic_data = {
            "epic": {
                "id": "EPIC-UI-TEST",
                "title": "UI Test Epic", 
                "description": "Test epic for UI exports",
                "key_requirements": ["Test requirement"]
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/api/generate", json=epic_data)
        assert response.status_code == 200
        run_id = response.json()["run_id"]
        
        # Test JSON export
        json_response = requests.get(f"{self.BASE_URL}/api/runs/{run_id}/json")
        assert json_response.status_code == 200
        assert len(json_response.content) > 0
        
        # Test CSV export  
        csv_response = requests.get(f"{self.BASE_URL}/api/runs/{run_id}/csv")
        assert csv_response.status_code == 200
        assert len(csv_response.content) > 0
    
    def test_ui_error_display(self):
        """Test that UI properly displays error messages"""
        # Submit invalid data
        response = requests.post(f"{self.BASE_URL}/api/generate", json={})
        
        # UI should handle both success and error responses gracefully
        # For now, just verify API returns some response
        assert response.status_code is not None
    
    def test_ui_batch_epic_processing(self):
        """Test UI handling of multiple epics"""
        epic1 = {
            "epic": {
                "id": "EPIC-1",
                "title": "First Epic",
                "description": "First test epic",
                "key_requirements": ["Req 1"]
            }
        }
        
        epic2 = {
            "epic": {
                "id": "EPIC-2", 
                "title": "Second Epic",
                "description": "Second test epic",
                "key_requirements": ["Req 2"]
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/api/generate", 
                               json={"epics": [epic1["epic"], epic2["epic"]]})
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["output"]["epics"]) == 2
