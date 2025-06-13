from typing import Dict, Any, List
from .base import BaseContextProvider
from mock_data import MOCK_REST_RESPONSES

class MockRESTContextProvider(BaseContextProvider):
    """Mock provider for REST API during development"""
    
    def __init__(self):
        self.responses = MOCK_REST_RESPONSES
    
    async def initialize(self):
        """Initialize the mock REST provider"""
        pass
    
    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from the mock REST provider"""
        required_fields = kwargs.get('required_fields', [])
        query = query.lower()
        
        # Find matching responses
        matching_responses = []
        for response in self.responses:
            if any(query in str(value).lower() for value in response.values()):
                matching_responses.append(response)
        
        return {
            "data": matching_responses,
            "source": "mock_rest",
            "query": query,
            "fields": required_fields
        }
    
    async def validate_connection(self) -> bool:
        """Validate the mock REST connection"""
        return True
    
    async def close(self):
        """Close the mock REST connection"""
        pass 