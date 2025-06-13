from typing import Dict, Any
from .base import BaseContextProvider
import aiohttp

class RESTContextProvider(BaseContextProvider):
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url
        self.headers = headers or {}
        self.session = None

    async def initialize(self):
        """Initialize the HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from REST API"""
        if not self.session:
            await self.initialize()

        # Example implementation - modify based on your needs
        endpoint = f"{self.base_url}/search"
        params = {
            "q": query,
            **kwargs
        }

        async with self.session.get(endpoint, params=params) as response:
            result = await response.json()
            return {
                "data": result,
                "source": "rest",
                "query": query
            }

    async def validate_connection(self) -> bool:
        """Validate the REST API connection"""
        try:
            if not self.session:
                await self.initialize()
            
            # Try to access a health check or status endpoint
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            print(f"REST API connection error: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None 