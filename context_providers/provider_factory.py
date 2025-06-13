from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from .base import BaseContextProvider
from .database import DatabaseContextProvider
from .mock_database import MockDatabaseContextProvider
from .graphql import GraphQLContextProvider
from .mock_graphql import MockGraphQLContextProvider
from .rest import RESTContextProvider
from .mock_rest import MockRESTContextProvider
import os

class ProviderFactory:
    """Factory class for creating context providers based on environment"""
    
    _providers: Dict[str, Type[BaseContextProvider]] = {
        "database": {
            "production": DatabaseContextProvider,
            "development": MockDatabaseContextProvider
        },
        "graphql": {
            "production": GraphQLContextProvider,
            "development": MockGraphQLContextProvider
        },
        "rest": {
            "production": RESTContextProvider,
            "development": MockRESTContextProvider
        }
    }

    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> BaseContextProvider:
        """
        Create a provider instance based on the environment and provider type
        
        Args:
            provider_type: Type of provider to create (database, graphql, rest)
            **kwargs: Additional arguments for provider initialization
            
        Returns:
            BaseContextProvider: Instance of the requested provider
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
            
        environment = os.getenv("ENVIRONMENT", "development").lower()
        provider_class = cls._providers[provider_type][environment]
        
        # Initialize provider with appropriate arguments
        if environment == "production":
            if provider_type == "database":
                return provider_class(os.getenv("DATABASE_URL"))
            elif provider_type == "graphql":
                return provider_class(
                    os.getenv("GRAPHQL_ENDPOINT"),
                    {"Authorization": f"Bearer {os.getenv('GRAPHQL_TOKEN')}"}
                )
            elif provider_type == "rest":
                return provider_class(
                    os.getenv("REST_API_BASE_URL"),
                    {"Authorization": f"Bearer {os.getenv('REST_API_TOKEN')}"}
                )
        else:
            return provider_class()

    @classmethod
    def get_all_providers(cls) -> Dict[str, BaseContextProvider]:
        """
        Get all providers based on the current environment
        
        Returns:
            Dict[str, BaseContextProvider]: Dictionary of provider instances
        """
        return {
            provider_type: cls.create_provider(provider_type)
            for provider_type in cls._providers.keys()
        } 