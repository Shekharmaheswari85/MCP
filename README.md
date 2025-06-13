# Model Context Protocol (MCP) Server

A FastAPI-based server implementing the Model Context Protocol for providing contextual information to AI models. This server acts as a middleware between AI models and various data sources, intelligently routing queries to the most appropriate data provider.

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