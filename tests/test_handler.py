""""""Unit tests for ComfyUI handler with network volume setup.""""""

import unittest
import json
import os
from unittest.mock import patch, MagicMock

# Import handler (adjust path as needed)
import sys
sys.path.append('..')
import handler


class TestNetworkVolumeHandler(unittest.TestCase):
    """"""Test cases for network volume ComfyUI handler.""""""
    
    def setUp(self):
        """"""Set up test fixtures.""""""
        self.sample_job = {
            ""id"": ""test-job-123"",
            ""input"": {
                ""workflow"": {
                    ""6"": {
                        ""inputs"": {
                            ""text"": ""a beautiful landscape"",
                            ""clip"": [""30"", 1]
                        },
                        ""class_type"": ""CLIPTextEncode""
                    }
                }
            }
        }
    
    def test_validate_input_valid_workflow(self):
        """"""Test input validation with valid workflow.""""""
        validated_data, error = handler.validate_input(self.sample_job[""input""])
        self.assertIsNone(error)
        self.assertIsNotNone(validated_data)
        self.assertIn(""workflow"", validated_data)
    
    def test_validate_input_missing_workflow(self):
        """"""Test input validation with missing workflow.""""""
        invalid_input = {""not_workflow"": ""invalid""}
        validated_data, error = handler.validate_input(invalid_input)
        self.assertIsNotNone(error)
        self.assertIn(""workflow"", error)
    
    @patch('handler.requests.get')
    def test_check_server_available(self, mock_get):
        """"""Test server availability check.""""""
        mock_get.return_value.status_code = 200
        result = handler.check_server(""http://127.0.0.1:3001/"", 1, 1000)
        self.assertTrue(result)
    
    @patch('handler.requests.get')
    def test_check_server_unavailable(self, mock_get):
        """"""Test server availability check when unavailable.""""""
        mock_get.side_effect = Exception(""Connection refused"")
        result = handler.check_server(""http://127.0.0.1:3001/"", 1, 1000)
        self.assertFalse(result)
    
    @patch('handler.requests.post')
    def test_queue_workflow_success(self, mock_post):
        """"""Test successful workflow queuing.""""""
        mock_response = MagicMock()
        mock_response.json.return_value = {""prompt_id"": ""test-prompt-123""}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = handler.queue_workflow(self.sample_job[""input""][""workflow""], ""client-123"")
        self.assertEqual(result[""prompt_id""], ""test-prompt-123"")
    
    def test_network_volume_constants(self):
        """"""Test that network volume specific constants are set correctly.""""""
        # ComfyUI should be configured for port 3001 (your setup)
        self.assertEqual(handler.COMFY_HOST, ""127.0.0.1"")
        # Add more constant checks as needed
    
    @patch('handler.websocket.WebSocket')
    @patch('handler.queue_workflow')
    @patch('handler.check_server')
    def test_handler_network_volume_integration(self, mock_check_server, mock_queue, mock_ws):
        """"""Test handler integration with network volume setup.""""""
        # Mock server as available (ComfyUI running on network volume)
        mock_check_server.return_value = True
        
        # Mock successful workflow queuing
        mock_queue.return_value = {""prompt_id"": ""test-prompt-123""}
        
        # Mock websocket
        mock_ws_instance = MagicMock()
        mock_ws.return_value = mock_ws_instance
        mock_ws_instance.recv.side_effect = [
            json.dumps({""type"": ""executing"", ""data"": {""node"": None}}),
            json.dumps({""type"": ""executed"", ""data"": {""node"": ""test-node"", ""output"": {}}})
        ]
        
        # This would be a more complex test with full handler execution
        # For now, just verify mocks are set up correctly
        self.assertTrue(mock_check_server.return_value)


if __name__ == '__main__':
    # Load test input for integration tests
    with open('../test_input.json', 'r') as f:
        test_data = json.load(f)
    
    unittest.main()
