# Model Context Protocol Server

A FastAPI-based server that implements the Model Context Protocol to provide relevant information to AI models when processing user queries.

## Environment Configuration

The server can be configured using environment variables. Create a `.env` file in the root directory with the following variables:

```env
# Server Configuration
HOST=0.0.0.0              # Server host (0.0.0.0 for all interfaces)
PORT=8000                 # Server port
ENVIRONMENT=development   # Environment (development/production)
DEBUG=true               # Enable debug mode
API_PREFIX=/api/v1       # API prefix for all endpoints

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL
OLLAMA_MODEL=llama2                     # Default model to use

# Database Configuration
DATABASE_URL=sqlite:///./catalog.db     # Database connection URL
```

## Deployment

### Local Development

1. Create and activate a virtual environment:
```bash
python -m venv .venv-py311
source .venv-py311/bin/activate  # On Unix/macOS
# or
.venv-py311\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

### Production Deployment

1. Set up environment variables for production:
```env
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
DEBUG=false
API_PREFIX=/api/v1
OLLAMA_BASE_URL=http://your-ollama-server:11434
OLLAMA_MODEL=llama2
```

2. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t mcp-server .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  -e OLLAMA_BASE_URL=http://your-ollama-server:11434 \
  -e OLLAMA_MODEL=llama2 \
  mcp-server
```

## API Documentation

When running in development mode (DEBUG=true), API documentation is available at:
- Swagger UI: `http://your-server:8000/api/v1/docs`
- ReDoc: `http://your-server:8000/api/v1/redoc`
- OpenAPI JSON: `http://your-server:8000/api/v1/openapi.json`

## Security Considerations

1. In production:
   - Set DEBUG=false to disable API documentation
   - Use HTTPS
   - Configure proper authentication
   - Use secure database credentials
   - Set appropriate CORS policies

2. For Ollama server:
   - Ensure Ollama server is properly secured
   - Use internal network for communication if possible
   - Consider using API keys or other authentication methods

## Monitoring and Logging

The server includes built-in logging with different levels based on the environment:
- Development: Debug level logging
- Production: Info level logging

Logs can be configured to output to files or external logging services.

## Features

- Intelligent query routing based on query analysis
- Support for multiple data sources (Database, GraphQL, REST)
- Integration with Ollama models (Mistral, Qwen, Llama2)
- Environment-aware configuration (Development/Production)
- Comprehensive logging and error handling
- Health check endpoints
- Mock data support for development

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- Required Ollama models:
  - mistral
  - qwen
  - llama2

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
```env
ENVIRONMENT=development
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

## Running the Server

1. Start Ollama (if not already running):
```bash
ollama serve
```

2. Start the MCP server:
```bash
python main.py
```

The server will be available at `http://localhost:8000`

## API Endpoints

### Get Context
```bash
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about iPhone 15",
    "model": "mistral"
  }'
```

### List Available Models
```bash
curl http://localhost:8000/models
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Project Structure

```
mcp-server/
├── context_providers/     # Data source providers
│   ├── database.py       # Database provider
│   ├── graphql.py        # GraphQL provider
│   ├── rest.py          # REST API provider
│   └── provider_factory.py
├── model_providers/      # AI model providers
│   ├── base.py          # Base model provider
│   ├── ollama.py        # Ollama integration
│   └── provider_factory.py
├── main.py              # FastAPI application
├── query_analyzer.py    # Query analysis logic
├── logger_config.py     # Logging configuration
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Development

### Adding New Providers

1. Create a new provider class in the appropriate directory
2. Implement the required interface methods
3. Register the provider in the factory

### Adding New Models

1. Add the model to the `AVAILABLE_MODELS` dictionary in `model_providers/ollama.py`
2. Update the model validation logic if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 