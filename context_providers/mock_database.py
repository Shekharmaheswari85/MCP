from typing import Dict, Any, List
from .base import BaseContextProvider
from mock_data import MOCK_PRODUCTS, MOCK_CATEGORIES, MOCK_BRANDS

class MockDatabaseContextProvider(BaseContextProvider):
    """Mock provider for database during development"""
    
    def __init__(self):
        self.products = MOCK_PRODUCTS
        self.categories = MOCK_CATEGORIES
        self.brands = MOCK_BRANDS
    
    async def initialize(self):
        """Initialize the mock database"""
        pass
    
    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from the mock database"""
        required_fields = kwargs.get('required_fields', [])
        query = query.lower()
        
        # Search in products
        matching_products = [
            product for product in self.products
            if any(query in str(value).lower() for value in product.values())
        ]
        
        return {
            "data": {
                "products": matching_products,
                "categories": self.categories,
                "brands": self.brands
            },
            "source": "mock_database",
            "query": query,
            "fields": required_fields
        }
    
    async def validate_connection(self) -> bool:
        """Validate the mock database connection"""
        return True
    
    async def close(self):
        """Close the mock database connection"""
        pass 