from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseModelProvider(ABC):
    """Base class for model providers"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a response using the model"""
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate the connection to the model"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close the model connection"""
        pass 