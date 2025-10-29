"""
Integration script to connect the existing multi_ai_qa_agent.py with the FastAPI backend.
This allows the frontend to trigger tests through the API.
"""
import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the existing multi_ai_qa_agent components
from multi_ai_qa_agent import MultiAIQAAgent, TestResult, PerformanceMetrics

class QAAgentIntegration:
    """Integration class to connect the existing QA Agent with the API."""
    
    def __init__(self):
        self.agent = MultiAIQAAgent()
        self.active_tests = {}
    
    async def run_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a test using the existing QA Agent."""
        test_id = test_config.get('id', f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Store test info
            self.active_tests[test_id] = {
                'id': test_id,
                'status': 'running',
                'start_time': datetime.now().isoformat(),
                'config': test_config
            }
            
            # Prepare test parameters
            url = test_config.get('url', 'https://www.w3schools.com')
            username = test_config.get('username', '')
            password = test_config.get('password', '')
            test_type = test_config.get('test_type', 'login')
            description = test_config.get('description', '')
            
            # Run the test using the existing agent
            result = await self.agent.run_test(
                url=url,
                username=username,
                password=password,
                test_type=test_type,
                description=description
            )
            
            # Update test status
            self.active_tests[test_id].update({
                'status': 'success' if result.success else 'failure',
                'end_time': datetime.now().isoformat(),
                'result': result,
                'screenshot': result.screenshot if hasattr(result, 'screenshot') else None
            })
            
            return {
                'id': test_id,
                'status': 'success' if result.success else 'failure',
                'result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                'screenshot': result.screenshot if hasattr(result, 'screenshot') else None
            }
            
        except Exception as e:
            # Update test status on error
            self.active_tests[test_id].update({
                'status': 'failure',
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            })
            
            return {
                'id': test_id,
                'status': 'failure',
                'error': str(e)
            }
    
    def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific test."""
        return self.active_tests.get(test_id)
    
    def get_all_tests(self) -> Dict[str, Any]:
        """Get all tests."""
        return self.active_tests
    
    def stop_test(self, test_id: str) -> bool:
        """Stop a running test."""
        if test_id in self.active_tests:
            self.active_tests[test_id]['status'] = 'stopped'
            return True
        return False

# Global integration instance
qa_integration = QAAgentIntegration()

async def run_qa_test(test_config: Dict[str, Any]) -> Dict[str, Any]:
    """Run a QA test through the integration."""
    return await qa_integration.run_test(test_config)

def get_test_status(test_id: str) -> Optional[Dict[str, Any]]:
    """Get test status."""
    return qa_integration.get_test_status(test_id)

def get_all_tests() -> Dict[str, Any]:
    """Get all tests."""
    return qa_integration.get_all_tests()

def stop_test(test_id: str) -> bool:
    """Stop a test."""
    return qa_integration.stop_test(test_id)

if __name__ == "__main__":
    # Test the integration
    async def test_integration():
        test_config = {
            'url': 'https://www.w3schools.com',
            'username': 'test@example.com',
            'password': 'testpassword',
            'test_type': 'login',
            'description': 'Test login functionality'
        }
        
        result = await run_qa_test(test_config)
        print(f"Test result: {result}")
    
    asyncio.run(test_integration())

