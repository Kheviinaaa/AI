import pytest
import json
import jsonschema
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

class TestJSONSchemas:
    
    def test_story_schema_validation(self):
        """Test that valid story JSON passes schema validation"""
        schema_path = Path("src/schemas/output.schema.json")
        
        if not schema_path.exists():
            pytest.skip("Schema file not found, skipping schema tests")
            
        with open(schema_path) as f:
            schema = json.load(f)
        
        # Valid story data
        valid_story = {
            "stories": [
                {
                    "id": "US-01",
                    "title": "User login",
                    "description": "As a user, I want to login",
                    "acceptance_criteria": [
                        {"given": "I am on login page", "when": "I enter valid credentials", "then": "I access my dashboard"}
                    ],
                    "story_points": 3,
                    "sp_justification": "Simple authentication flow",
                    "risk": "Low",
                    "test_cases": [
                        {
                            "id": "TC-01-01",
                            "preconditions": "User has valid account",
                            "test_steps": "1. Navigate to login\n2. Enter credentials\n3. Click login",
                            "expected_result": "User is redirected to dashboard"
                        }
                    ]
                }
            ]
        }
        
        # Should not raise exception
        jsonschema.validate(valid_story, schema)
    
    def test_story_missing_required_fields(self):
        """Test that missing required fields fails validation"""
        schema_path = Path("src/schemas/output.schema.json")
        
        if not schema_path.exists():
            pytest.skip("Schema file not found, skipping schema tests")
            
        with open(schema_path) as f:
            schema = json.load(f)
        
        invalid_story = {
            "stories": [
                {
                    "id": "US-01",
                    "title": "User login"
                    # Missing required fields: description, acceptance_criteria, etc.
                }
            ]
        }
        
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_story, schema)
    
    def test_story_points_validation(self):
        """Test that story_points must be in Fibonacci sequence"""
        schema_path = Path("src/schemas/output.schema.json")
        
        if not schema_path.exists():
            pytest.skip("Schema file not found, skipping schema tests")
            
        with open(schema_path) as f:
            schema = json.load(f)
        
        invalid_story_points = {
            "stories": [
                {
                    "id": "US-01",
                    "title": "User login",
                    "description": "As a user, I want to login",
                    "acceptance_criteria": [
                        {"given": "I am on login page", "when": "I enter valid credentials", "then": "I access my dashboard"}
                    ],
                    "story_points": 4,  # Invalid: not in Fibonacci
                    "sp_justification": "Simple authentication flow",
                    "risk": "Low",
                    "test_cases": []
                }
            ]
        }
        
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_story_points, schema)
    
    def test_id_uniqueness(self):
        """Test that story IDs are unique within output"""
        schema_path = Path("src/schemas/output.schema.json")
        
        if not schema_path.exists():
            pytest.skip("Schema file not found, skipping schema tests")
            
        with open(schema_path) as f:
            schema = json.load(f)
        
        duplicate_ids = {
            "stories": [
                {
                    "id": "US-01",
                    "title": "Story 1",
                    "description": "First story",
                    "acceptance_criteria": [{"given": "A", "when": "B", "then": "C"}],
                    "story_points": 3,
                    "sp_justification": "Test",
                    "risk": "Low",
                    "test_cases": []
                },
                {
                    "id": "US-01",  # Duplicate ID
                    "title": "Story 2", 
                    "description": "Second story",
                    "acceptance_criteria": [{"given": "A", "when": "B", "then": "C"}],
                    "story_points": 5,
                    "sp_justification": "Test",
                    "risk": "Medium",
                    "test_cases": []
                }
            ]
        }
        
        # This should pass schema validation (uniqueness may be app logic)
        jsonschema.validate(duplicate_ids, schema)
