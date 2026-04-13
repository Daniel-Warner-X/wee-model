# Garbage Model

A simple, standalone API service for getting model responses when pretty much any model response will do.

## Quickstart

### Clone this repo

```
git@github.com:Daniel-Warner-X/garbage-model.git
```

### Run the start script

```bash
./start.sh
```

After startup, you'll see:

```
=================================
✓ Setup complete!
=================================

Service Information:
  Endpoint: http://localhost:8080
  API Docs: http://localhost:8080/docs
  API Key:  grbg-abc123...
  Model:    qwen2.5:7b

Add this header to your requests:
  X-API-Key: grbg-abc123...
=================================
```

### 3. Test the health endpoint

```
curl http://localhost:8080/health | jq
```  

### 4. Send a sample chat completion request

```
curl -X POST http://localhost:8080/chat -H "X-API-Key: your-api-key-here" -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "What is the capital of France?"}], "temperature": 0.7}'
```


## API documentation

http://localhost:8080/docs


## What the setup script does:

1. Check for Ollama installation
2. Start Ollama service if needed
3. Pull the `qwen2.5:7b` model
4. Set up Python virtual environment
5. Install dependencies
6. Generate an API key
7. Start the API server

## Configuration

Environment variables (optional):

- `OLLAMA_MODEL`: Model to use (default: `qwen2.5:7b`)
- `API_KEY`: Custom API key (auto-generated if not set)
- `PORT`: API port (default: `8080`)

Example:
```bash
OLLAMA_MODEL=llama3.2:3b PORT=9000 ./start.sh
```

## Requirements

- Python 3.8+
- Ollama installed (`brew install ollama`)


## Stopping the Service

Press `Ctrl+C` to stop the API server.

Ollama will keep running in the background. To stop it:

```bash
pkill ollama
```

## License

MIT
