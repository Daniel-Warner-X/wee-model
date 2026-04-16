<img width="200" height="157" alt="sleepy" src="https://github.com/user-attachments/assets/fe6673bb-9822-45ed-a472-15ac3ff51475" />
<img width="423" height="333" alt="sleepy" src="https://github.com/user-attachments/assets/0432314d-f910-4d76-ac2f-d6dfa7e54e93" />

# Wee Model

A simple, standalone API service for getting model responses when pretty much any model response will do.

Uses qwen2.5:7b by default.

## Quickstart

### Clone this repo

```
git@github.com:Daniel-Warner-X/wee-model.git
```

### Change directories

```
cd wee-model
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
  API Key:  wee-abc123...
  Model:    qwen2.5:7b

Add this header to your requests:
  X-API-Key: wee-abc123...
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

### 5. Try tool/function calling

```bash
python tool_example.py
```


## Features

- **Chat completions**: Standard chat interface
- **Tool/function calling**: Let the model call functions you define
- **Structured extraction**: Extract JSON data from text
- **JSON formatting**: Request JSON-formatted responses

## API documentation

http://localhost:8080/docs

## Tool/Function Calling

The API supports tool/function calling, allowing the model to call functions you define. See `tool_example.py` for a complete example.

Example request with tools:

```bash
curl -X POST http://localhost:8080/chat \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the weather in Boston?"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          },
          "required": ["location"]
        }
      }
    }]
  }'
```

The response will include `tool_calls` when the model wants to call a function.


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
