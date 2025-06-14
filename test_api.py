import requests
import json
from typing import Dict, Any

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def list_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        response = requests.get(f"{self.base_url}/models", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_context(self, query: str, model: str) -> Dict[str, Any]:
        """Get context for a query"""
        data = {
            "query": query,
            "model": model
        }
        response = requests.post(
            f"{self.base_url}/context",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def check_health(self) -> Dict[str, Any]:
        """Check server health"""
        response = requests.get(f"{self.base_url}/health", headers=self.headers)
        response.raise_for_status()
        return response.json()

def main():
    # Initialize client
    client = MCPClient()
    
    try:
        # Check server health
        print("\n=== Health Check ===")
        health = client.check_health()
        print(json.dumps(health, indent=2))
        
        # List available models
        print("\n=== Available Models ===")
        models = client.list_models()
        print(json.dumps(models, indent=2))
        
        # Get context for a query
        print("\n=== Getting Context ===")
        query = "Tell me about iPhone 15"
        model = "llama2"
        context = client.get_context(query, model)
        print(json.dumps(context, indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 