from typing import Dict, Type
from .base import BaseModelProvider
from .ollama import OllamaModelProvider
import os

class ModelProviderFactory:
    """Factory for creating model providers"""
    
    _providers: Dict[str, Type[BaseModelProvider]] = {
        "ollama": OllamaModelProvider
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> BaseModelProvider:
        """
        Create a model provider instance
        
        Args:
            provider_type: Type of provider to create (e.g., "ollama")
            **kwargs: Additional arguments for provider initialization
            
        Returns:
            BaseModelProvider: Instance of the requested provider
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown model provider type: {provider_type}")
            
        provider_class = cls._providers[provider_type]
        
        # Initialize provider with appropriate arguments
        if provider_type == "ollama":
            return provider_class(
                model_name=kwargs.get("model_name", "llama2"),
                base_url=kwargs.get("base_url", "http://localhost:11434")
            )
        
        return provider_class(**kwargs) 