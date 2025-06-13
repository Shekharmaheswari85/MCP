from typing import Dict, Any
from .base import BaseContextProvider
import aiohttp
import json

class GraphQLContextProvider(BaseContextProvider):
    def __init__(self, endpoint: str, headers: Dict[str, str] = None):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.session = None

    async def initialize(self):
        """Initialize the HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from GraphQL API"""
        if not self.session:
            await self.initialize()

        # Example GraphQL query - modify based on your needs
        graphql_query = """
        query SearchData($searchTerm: String!) {
            search(query: $searchTerm) {
                items {
                    id
                    name
                    description
                }
            }
        }
        """
        
        variables = {
            "searchTerm": query
        }

        async with self.session.post(
            self.endpoint,
            json={
                "query": graphql_query,
                "variables": variables
            }
        ) as response:
            result = await response.json()
            return {
                "data": result.get("data", {}),
                "source": "graphql",
                "query": query
            }

    async def validate_connection(self) -> bool:
        """Validate the GraphQL connection"""
        try:
            if not self.session:
                await self.initialize()
            
            # Simple introspection query to validate connection
            introspection_query = """
            query {
                __schema {
                    types {
                        name
                    }
                }
            }
            """
            
            async with self.session.post(
                self.endpoint,
                json={"query": introspection_query}
            ) as response:
                return response.status == 200
        except Exception as e:
            print(f"GraphQL connection error: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None 