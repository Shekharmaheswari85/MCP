from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseContextProvider(ABC):
    """Base class for all context providers"""
    
    @abstractmethod
    async def get_context(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get context from the provider"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate the connection to the data source"""
        pass 