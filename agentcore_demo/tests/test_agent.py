"""
Test suite for AgentCore Demo Agent
Last Updated: 2025-12-29 - All 12 tests passing
"""

import pytest
import json
from datetime import datetime
from agent import agent_handler, AgentCoreDemo

class TestAgentCoreDemo:
    """Test cases for the AgentCore demo agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = AgentCoreDemo()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        assert self.agent.agent_name == "AgentCore Demo Agent"
        assert self.agent.version == "1.0.0"
    
    def test_hello_response(self):
        """Test hello greeting responses"""
        test_cases = ["hello", "hi", "Hey there", "HELLO"]
        
        for prompt in test_cases:
            request = {"prompt": prompt}
            response = agent_handler(request)
            
            assert response["status"] == "success"
            assert "Hello!" in response["response"]
            assert "AgentCore" in response["response"]
    
    def test_time_response(self):
        """Test time-related queries"""
        request = {"prompt": "What time is it?"}
        response = agent_handler(request)
        
        assert response["status"] == "success"
        assert "Current time:" in response["response"]
        assert datetime.now().strftime("%Y") in response["response"]
    
    def test_agentcore_info_response(self):
        """Test AgentCore information queries"""
        request = {"prompt": "Tell me about AgentCore"}
        response = agent_handler(request)
        
        assert response["status"] == "success"
        assert "AgentCore" in response["response"]
        assert "AWS" in response["response"]
        assert "serverless" in response["response"].lower()
    
    def test_capabilities_response(self):
        """Test capabilities query"""
        request = {"prompt": "What are your capabilities?"}
        response = agent_handler(request)
        
        assert response["status"] == "success"
        assert "capabilities" in response["response"]
        assert "demo agent" in response["response"].lower()
    
    def test_default_response(self):
        """Test default response for unknown queries"""
        request = {"prompt": "Random unknown query"}
        response = agent_handler(request)
        
        assert response["status"] == "success"
        assert "You said:" in response["response"]
        assert "demo agent" in response["response"].lower()
    
    def test_response_structure(self):
        """Test response has correct structure"""
        request = {"prompt": "test", "user_id": "test_user", "session_id": "test_session"}
        response = agent_handler(request)
        
        required_fields = ["response", "agent_name", "version", "user_id", "session_id", "timestamp", "status"]
        
        for field in required_fields:
            assert field in response
        
        assert response["agent_name"] == "AgentCore Demo Agent"
        assert response["version"] == "1.0.0"
        assert response["user_id"] == "test_user"
        assert response["session_id"] == "test_session"
        assert response["status"] == "success"
    
    def test_empty_prompt(self):
        """Test handling of empty prompt"""
        request = {"prompt": ""}
        response = agent_handler(request)
        
        assert response["status"] == "success"
        assert isinstance(response["response"], str)
    
    def test_missing_prompt(self):
        """Test handling of missing prompt"""
        request = {}
        response = agent_handler(request)
        
        assert response["status"] == "success"
        assert isinstance(response["response"], str)
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        # This test would need to be adapted based on actual error conditions
        # For now, we test that the agent handles various input types gracefully
        
        test_cases = [
            {"prompt": None},
            {"prompt": 123},
            {"prompt": []},
            {"prompt": {}}
        ]
        
        for request in test_cases:
            response = agent_handler(request)
            assert "status" in response
            assert isinstance(response["response"], str)

class TestAgentIntegration:
    """Integration tests for AgentCore functionality"""
    
    def test_json_serialization(self):
        """Test that responses can be JSON serialized"""
        request = {"prompt": "hello"}
        response = agent_handler(request)
        
        # Should not raise an exception
        json_str = json.dumps(response)
        parsed = json.loads(json_str)
        
        assert parsed == response
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request(prompt):
            request = {"prompt": f"Test {prompt}"}
            response = agent_handler(request)
            results.append(response)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests completed successfully
        assert len(results) == 5
        for result in results:
            assert result["status"] == "success"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])