from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from context_providers.provider_factory import ProviderFactory
from model_providers.provider_factory import ModelProviderFactory
from model_providers.ollama import OllamaModelProvider
from query_analyzer import QueryAnalyzer, QueryAnalysis
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from logger_config import setup_logger
from fastapi.security import APIKeyHeader
from fastapi.openapi.models import SecurityScheme

# Set up logger
logger = setup_logger("mcp_server")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")  # Default to 0.0.0.0 to accept external connections
PORT = int(os.getenv("PORT", "8000"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

# Initialize providers using the factory
providers = ProviderFactory.get_all_providers()
logger.info(f"Initialized providers: {list(providers.keys())}")

# Initialize model provider with default model
default_model = os.getenv("OLLAMA_MODEL", "llama2")
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model_provider = ModelProviderFactory.create_provider(
    "ollama",
    model_name=default_model,
    base_url=ollama_base_url
)
logger.info(f"Initialized model provider with model: {default_model} at {ollama_base_url}")

# Initialize query analyzer
query_analyzer = QueryAnalyzer()
logger.info("Initialized query analyzer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Initialize all providers
    logger.info(f"Starting up application in {ENVIRONMENT} environment...")
    for provider in providers.values():
        await provider.initialize()
        logger.debug(f"Initialized provider: {provider.__class__.__name__}")
    
    await model_provider.validate_connection()
    logger.info("Model provider connection validated")
    
    yield
    
    # Shutdown: Clean up provider resources
    logger.info("Shutting down application...")
    for provider in providers.values():
        if hasattr(provider, 'close'):
            await provider.close()
            logger.debug(f"Closed provider: {provider.__class__.__name__}")
    await model_provider.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Model Context Protocol Server",
    description="""
    API server for providing context and additional information to AI models.
    
    ## Features
    - Context-aware query processing
    - Multiple data provider support
    - Model-agnostic interface
    - Real-time context generation
    
    ## Authentication
    All endpoints require authentication using API keys.
    
    ## Rate Limiting
    API calls are rate-limited based on your subscription tier.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{API_PREFIX}/docs" if DEBUG else None,
    redoc_url=f"{API_PREFIX}/redoc" if DEBUG else None,
    openapi_url=f"{API_PREFIX}/openapi.json" if DEBUG else None,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    }
)

# Add security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

# Update OpenAPI schema
app.openapi_tags = [
    {
        "name": "models",
        "description": "Operations related to available AI models",
    },
    {
        "name": "context",
        "description": "Operations for retrieving context for AI model queries",
    },
    {
        "name": "health",
        "description": "Health check and monitoring endpoints",
    }
]

class ContextRequest(BaseModel):
    query: str
    model: str  # e.g., "mistral", "qwen", "llama3.2"

class ContextResponse(BaseModel):
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    analysis: Dict[str, Any]
    response: str

class ModelInfo(BaseModel):
    name: str
    description: str

@app.get("/models", response_model=List[ModelInfo], tags=["models"])
async def list_models():
    """
    List available models and their descriptions.
    
    Returns a list of all available AI models that can be used with the context protocol.
    Each model entry includes its name and a brief description of its capabilities.
    """
    logger.info("Listing available models")
    models = OllamaModelProvider.get_available_models()
    return [
        ModelInfo(name=name, description=description)
        for name, description in models.items()
    ]

@app.post("/context", response_model=ContextResponse, tags=["context"])
async def get_context(request: ContextRequest) -> ContextResponse:
    """
    Get context for an AI model query.
    
    This endpoint implements the Model Context Protocol to provide relevant information
    to AI models when processing user queries.
    
    - **query**: The user's query that needs context
    - **model**: The AI model that will process the query (e.g., "llama2", "mistral")
    
    Returns:
    - Context data relevant to the query
    - Metadata about the context generation
    - Analysis of the query
    - Model's response incorporating the context
    """
    logger.info(f"Received context request for query: {request.query} with model: {request.model}")
    
    try:
        # Validate model
        if request.model not in OllamaModelProvider.AVAILABLE_MODELS:
            logger.error(f"Invalid model requested: {request.model}. Available models: {list(OllamaModelProvider.AVAILABLE_MODELS.keys())}")
            raise HTTPException(
                status_code=400,
                detail=f"Model {request.model} not available. Available models: {list(OllamaModelProvider.AVAILABLE_MODELS.keys())}"
            )
        
        # Analyze the query to determine the best provider
        logger.debug("Analyzing query...")
        analysis = query_analyzer.analyze_query(request.query)
        logger.info(f"Query analysis: type={analysis.query_type}, confidence={analysis.confidence}, suggested_providers={analysis.suggested_providers}")
        
        # Try providers in order of preference until we get a successful response
        context_data = None
        used_provider = None
        
        for provider_type in analysis.suggested_providers:
            logger.debug(f"Trying provider: {provider_type}")
            provider = providers[provider_type]
            
            # Validate provider connection
            if not await provider.validate_connection():
                logger.warning(f"Provider {provider_type} connection validation failed")
                continue
                
            try:
                # Get context from the provider
                context_data = await provider.get_context(
                    request.query,
                    required_fields=analysis.required_fields
                )
                used_provider = provider_type
                logger.info(f"Successfully got context from provider: {provider_type}")
                logger.debug(f"Context data: {context_data}")
                break
            except Exception as e:
                logger.error(f"Error with provider {provider_type}: {str(e)}", exc_info=True)
                continue
        
        if not context_data:
            logger.error("No available providers could handle the query")
            raise HTTPException(
                status_code=503,
                detail="No available providers could handle the query"
            )
        
        # Generate response using the model
        logger.debug("Generating model response...")
        try:
            model_response = await model_provider.generate_response(
                request.query,
                context_data
            )
            logger.info("Model response generated successfully")
            logger.debug(f"Model response: {model_response}")
        except Exception as e:
            logger.error(f"Error generating model response: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error generating model response: {str(e)}"
            )
        
        return ContextResponse(
            context=context_data,
            metadata={
                "model": request.model,
                "provider": used_provider,
                "timestamp": "2024-03-19T12:00:00Z"  # We'll make this dynamic later
            },
            analysis={
                "query_type": analysis.query_type.value,
                "confidence": analysis.confidence,
                "entities": analysis.entities,
                "suggested_providers": analysis.suggested_providers,
                "used_provider": used_provider
            },
            response=model_response
        )
    except Exception as e:
        logger.error(f"Error processing context request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["health"])
async def health_check():
    """
    Check the health status of the MCP server.
    
    Returns the current health status of the server and its components,
    including the status of all configured providers.
    """
    logger.info("Health check requested")
    health_status = {
        "status": "healthy",
        "service": "mcp-server",
        "providers": {},
        "environment": ENVIRONMENT.lower()
    }
    
    # Check each provider's health
    for provider_type, provider in providers.items():
        try:
            is_healthy = await provider.validate_connection()
            health_status["providers"][provider_type] = "healthy" if is_healthy else "unhealthy"
            logger.debug(f"Provider {provider_type} health: {health_status['providers'][provider_type]}")
        except Exception as e:
            logger.error(f"Error checking provider {provider_type} health: {str(e)}")
            health_status["providers"][provider_type] = "unhealthy"
    
    # Check model provider health
    try:
        is_healthy = await model_provider.validate_connection()
        health_status["providers"]["model"] = "healthy" if is_healthy else "unhealthy"
        logger.debug(f"Model provider health: {health_status['providers']['model']}")
    except Exception as e:
        logger.error(f"Error checking model provider health: {str(e)}")
        health_status["providers"]["model"] = "unhealthy"
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    ) 