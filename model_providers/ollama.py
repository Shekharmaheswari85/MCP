from typing import Dict, Any, List
import httpx
from .base import BaseModelProvider
from logger_config import setup_logger

logger = setup_logger("ollama_provider")

class OllamaModelProvider(BaseModelProvider):
    """Provider for Ollama models"""
    
    AVAILABLE_MODELS = {
        "llama2": "General purpose model optimized for various tasks"
    }
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} not available. Available models: {list(self.AVAILABLE_MODELS.keys())}")
        
        self.model_name = model_name
        self.base_url = base_url
        # Increase timeout to 300 seconds (5 minutes)
        self.client = httpx.AsyncClient(base_url=base_url, timeout=300.0)
        logger.info(f"Initialized Ollama provider with model: {model_name} at {base_url}")
    
    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """Get list of available models"""
        return cls.AVAILABLE_MODELS
    
    async def validate_connection(self) -> bool:
        """Validate connection to Ollama server"""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            logger.info("Successfully connected to Ollama server")
            return True
        except httpx.ConnectError:
            logger.error("Failed to connect to Ollama server. Make sure Ollama is running at %s", self.base_url)
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server: {str(e)}", exc_info=True)
            return False
    
    async def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate response using the model"""
        try:
            # Format the prompt with context
            prompt = self._format_prompt(query, context)
            logger.debug(f"Formatted prompt: {prompt}")
            
            # Make request to Ollama with increased timeout
            async with httpx.AsyncClient(base_url=self.base_url, timeout=300) as client:
                response = await client.post(
                    "/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                            "num_predict": 1024  # Limit response length
                        }
                    }
                )
                response.raise_for_status()
            
            # Extract response
            result = response.json()
            logger.debug(f"Raw model response: {result}")
            
            if "response" not in result:
                logger.error(f"Unexpected response format: {result}")
                raise ValueError("Unexpected response format from Ollama")
            
            return result["response"]
        except httpx.ConnectError:
            logger.error("Failed to connect to Ollama server. Make sure Ollama is running at %s", self.base_url)
            raise ValueError("Could not connect to Ollama server. Please ensure it's running.")
        except httpx.TimeoutException as e:
            logger.error(f"Timeout while generating response: {str(e)}", exc_info=True)
            raise ValueError("Model response generation timed out. Please try again with a shorter query or context.")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise
    
    def _format_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Format the prompt with context"""
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's query.

Context:
{self._format_context(context)}

User Query: {query}

Please provide a detailed and helpful response based on the context provided."""
        
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format the context data for the prompt"""
        formatted_context = []
        
        if "data" in context:
            data = context["data"]
            if "products" in data:
                formatted_context.append("Products:")
                for product in data["products"]:
                    formatted_context.append(f"- {product['name']}: {product['description']}")
                    if "specifications" in product:
                        formatted_context.append("  Specifications:")
                        for key, value in product["specifications"].items():
                            formatted_context.append(f"  - {key}: {value}")
            
            if "categories" in data:
                formatted_context.append("\nCategories:")
                for category in data["categories"]:
                    formatted_context.append(f"- {category['name']}: {category['description']}")
            
            if "brands" in data:
                formatted_context.append("\nBrands:")
                for brand in data["brands"]:
                    formatted_context.append(f"- {brand['name']}: {brand['description']}")
        
        return "\n".join(formatted_context)
    
    async def close(self):
        """Close the Ollama client"""
        await self.client.aclose()
        logger.info("Closed Ollama client") 