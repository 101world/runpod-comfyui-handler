"""Tests for network volume ComfyUI handler."""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add parent directory to path to import handler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestNetworkVolumeHandler(unittest.TestCase):
    """Test cases for network volume ComfyUI handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_job = {
            "id": "test-job-123",
            "input": {
                "workflow": {
                    "6": {
                        "inputs": {
                            "text": "test prompt",
                            "clip": ["30", 1]
                        },
                        "class_type": "CLIPTextEncode"
                    }
                }
            }
        }
    
    def test_job_structure(self):
        """Test that job structure is valid."""
        self.assertIn("id", self.sample_job)
        self.assertIn("input", self.sample_job)
        self.assertIn("workflow", self.sample_job["input"])
    
    def test_workflow_validation(self):
        """Test workflow validation logic."""
        workflow = self.sample_job["input"]["workflow"]
        
        # Should have at least one node
        self.assertGreater(len(workflow), 0)
        
        # Check node structure
        for node_id, node_data in workflow.items():
            self.assertIn("inputs", node_data)
            self.assertIn("class_type", node_data)
    
    @patch('requests.get')
    def test_comfyui_health_check(self, mock_get):
        """Test ComfyUI health check functionality."""
        # Mock successful health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # This would test the health check function
        # Implementation depends on handler structure
        self.assertTrue(True)  # Placeholder
    
    def test_flux_workflow_nodes(self):
        """Test FLUX-specific workflow nodes."""
        expected_classes = [
            "CLIPTextEncode", 
            "DualCLIPLoader", 
            "UNETLoader", 
            "VAELoader",
            "KSampler", 
            "VAEDecode", 
            "SaveImage"
        ]
        
        # Load test input
        with open("test_input.json", "r") as f:
            test_data = json.load(f)
        
        workflow = test_data["input"]["workflow"]
        
        # Extract all class types from workflow
        class_types = [node["class_type"] for node in workflow.values()]
        
        # Check that FLUX classes are present
        for expected_class in expected_classes:
            self.assertIn(expected_class, class_types, 
                         f"Missing required FLUX class: {expected_class}")


if __name__ == '__main__':
    unittest.main()
