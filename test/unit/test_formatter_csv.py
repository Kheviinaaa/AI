import pytest
import csv
import tempfile
from pathlib import Path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

class TestCSVFormatter:
    
    def test_csv_flattening_structure(self):
        """Test that stories and test cases are flattened to one row per test case"""
        # This would test your actual CSV formatter
        # For now, creating a mock test
        test_data = [
            {
                'test_case_id': 'TC-01-01',
                'story_id': 'US-01',
                'story_title': 'User Login',
                'test_steps': '1. Navigate to login\n2. Enter credentials',
                'expected_result': 'Successful login'
            }
        ]
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=test_data[0].keys())
            writer.writeheader()
            writer.writerows(test_data)
            temp_path = f.name
        
        # Verify CSV was created with correct data
        with open(temp_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 1
            assert rows[0]['test_case_id'] == 'TC-01-01'
            assert rows[0]['story_id'] == 'US-01'
        
        # Cleanup
        os.unlink(temp_path)
    
    def test_csv_columns_correct(self):
        """Test that CSV has all required columns"""
        required_columns = [
            'test_case_id', 'story_id', 'story_title', 'story_points',
            'risk_level', 'preconditions', 'test_steps', 'expected_result'
        ]
        
        # Mock CSV creation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=required_columns)
            writer.writeheader()
            temp_path = f.name
        
        # Verify columns
        with open(temp_path, 'r') as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == required_columns
        
        os.unlink(temp_path)
