from typing import Dict, Any, List
from .base import BaseContextProvider
from mock_data import MOCK_GRAPHQL_RESPONSES

class MockGraphQLContextProvider(BaseContextProvider):
    """Mock provider for GraphQL during development"""
    
    def __init__(self):
        self.responses = MOCK_GRAPHQL_RESPONSES
    
    async def initialize(self):
        """Initialize the mock GraphQL provider"""
        pass
    
    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from the mock GraphQL provider"""
        required_fields = kwargs.get('required_fields', [])
        query = query.lower()
        
        # Find matching responses
        matching_responses = []
        for response in self.responses:
            if any(query in str(value).lower() for value in response.values()):
                matching_responses.append(response)
        
        return {
            "data": matching_responses,
            "source": "mock_graphql",
            "query": query,
            "fields": required_fields
        }
    
    async def validate_connection(self) -> bool:
        """Validate the mock GraphQL connection"""
        return True
    
    async def close(self):
        """Close the mock GraphQL connection"""
        pass 