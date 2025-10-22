import pytest
import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

class TestIDGenerators:
    
    def test_story_id_format(self):
        """Test that story IDs follow US-xx format"""
        # Mock ID generator - replace with your actual function
        def generate_story_id(index):
            return f"US-{index:02d}"
        
        test_cases = [
            (1, "US-01"),
            (15, "US-15"),
            (99, "US-99")
        ]
        
        for input_index, expected_id in test_cases:
            result = generate_story_id(input_index)
            assert result == expected_id
            assert re.match(r'^US-\d{2}$', result)
    
    def test_test_case_id_format(self):
        """Test that test case IDs follow TC-xx-yy format"""
        # Mock ID generator - replace with your actual function
        def generate_test_case_id(story_index, test_index):
            return f"TC-{story_index:02d}-{test_index:02d}"
        
        result = generate_test_case_id(1, 2)
        assert result == "TC-01-02"
        assert re.match(r'^TC-\d{2}-\d{2}$', result)
    
    def test_id_uniqueness(self):
        """Test that generated IDs are unique"""
        def generate_ids(count):
            return [f"US-{i:02d}" for i in range(1, count + 1)]
        
        ids = generate_ids(5)
        assert len(ids) == len(set(ids)), "IDs should be unique"
    
    def test_run_id_generation(self):
        """Test that run IDs are generated correctly"""
        import uuid
        from datetime import datetime
        
        # Mock run ID generator
        def generate_run_id():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_part = str(uuid.uuid4())[:8]
            return f"RUN-{timestamp}-{unique_part}"
        
        run_id = generate_run_id()
        assert run_id.startswith("RUN-")
        assert len(run_id) > 10
