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

# Set up logger
logger = setup_logger("mcp_server")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize providers using the factory
providers = ProviderFactory.get_all_providers()
logger.info(f"Initialized providers: {list(providers.keys())}")

# Initialize model provider with default model
default_model = os.getenv("OLLAMA_MODEL", "mistral")
model_provider = ModelProviderFactory.create_provider(
    "ollama",
    model_name=default_model,
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)
logger.info(f"Initialized model provider with model: {default_model}")

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
    logger.info("Starting up application...")
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
    description="API server for providing context and additional information to AI models",
    version="1.0.0",
    lifespan=lifespan
)

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

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List available models and their descriptions"""
    logger.info("Listing available models")
    models = OllamaModelProvider.get_available_models()
    return [
        ModelInfo(name=name, description=description)
        for name, description in models.items()
    ]

@app.post("/context")
async def get_context(request: ContextRequest) -> ContextResponse:
    """
    Endpoint for AI models to request context for their queries.
    This implements the Model Context Protocol to provide relevant information
    to AI models when processing user queries.
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

@app.get("/health")
async def health_check():
    """Health check endpoint for the MCP server"""
    logger.info("Health check requested")
    health_status = {
        "status": "healthy",
        "service": "mcp-server",
        "providers": {},
        "environment": os.getenv("ENVIRONMENT", "development").lower()
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
    logger.info("Starting MCP server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 