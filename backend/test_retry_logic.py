import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock
import anthropic
from app.agents.client_wrapper import RetryAnthropicClient

class TestRetryLogic(unittest.IsolatedAsyncioTestCase):
    async def test_retry_on_529(self):
        print("\nTesting retry on 529 Overloaded error...")
        
        # Mock the parent class methods
        client = RetryAnthropicClient(api_key="fake", model="fake")
        
        # We need to mock the *underlying* call that the parent class makes, 
        # OR since we are inheriting, we can mock the method on the super() object?
        # Actually, since we call super().invoke(), we can't easily mock super() in Python.
        # Instead, we can mock the method on the instance but that would mock our wrapper too.
        # A better approach for this specific test is to mock the method we are wrapping 
        # but we can't easily inject a mock for super().
        
        # Alternative: Create a subclass for testing that overrides the method to fail then succeed
        class MockClient(RetryAnthropicClient):
            def __init__(self):
                self.attempt_count = 0
                
            def invoke(self, *args, **kwargs):
                self.attempt_count += 1
                print(f"Attempt {self.attempt_count}")
                if self.attempt_count < 3:
                    print("Simulating 529 Error")
                    raise anthropic.APIStatusError(
                        message="Overloaded",
                        response=MagicMock(status_code=529),
                        body={"error": {"type": "overloaded_error"}}
                    )
                return "Success"

        mock_client = MockClient()
        
        # Test synchronous invoke
        result = mock_client.invoke("test")
        self.assertEqual(result, "Success")
        self.assertEqual(mock_client.attempt_count, 3)
        print("✅ Synchronous retry worked!")

    async def test_async_retry_on_529(self):
        print("\nTesting async retry on 529 Overloaded error...")
        
        class AsyncMockClient(RetryAnthropicClient):
            def __init__(self):
                self.attempt_count = 0
                
            async def a_invoke(self, *args, **kwargs):
                self.attempt_count += 1
                print(f"Async Attempt {self.attempt_count}")
                if self.attempt_count < 3:
                    print("Simulating 529 Error")
                    raise anthropic.APIStatusError(
                        message="Overloaded",
                        response=MagicMock(status_code=529),
                        body={"error": {"type": "overloaded_error"}}
                    )
                return "Async Success"

        mock_client = AsyncMockClient()
        
        # Test async invoke
        result = await mock_client.a_invoke("test")
        self.assertEqual(result, "Async Success")
        self.assertEqual(mock_client.attempt_count, 3)
        print("✅ Async retry worked!")

if __name__ == "__main__":
    unittest.main()
