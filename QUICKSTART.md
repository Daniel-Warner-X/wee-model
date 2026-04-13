# Quick Start Guide

## 1. Start the API (one command)

```bash
./start.sh
```

**That's it!** The script handles everything:
- Checks dependencies
- Starts Ollama
- Pulls the model
- Sets up Python environment
- Generates API key
- Starts the server

## 2. Copy your credentials

After startup, you'll see:
```
=================================
✓ Setup complete!
=================================

Service Information:
  Endpoint: http://localhost:8080
  API Docs: http://localhost:8080/docs
  API Key:  grbg-a1b2c3d4e5f6...
  Model:    qwen2.5:7b
=================================
```

**Save the API key!** You'll need it for all requests.

## 3. Test it

### Option A: Use the test script
```bash
# In a new terminal
export API_KEY="grbg-your-key-here"
pip install requests
python test_api.py
```

### Option B: Quick curl test
```bash
curl http://localhost:8080/health
```

### Option C: Browse interactive docs
Open in browser: http://localhost:8080/docs

## 4. Use it in your app

```python
import requests

API_KEY = "grbg-your-key-here"
headers = {"X-API-Key": API_KEY}

# Extract structured data
response = requests.post(
    "http://localhost:8080/extract",
    headers=headers,
    json={
        "prompt": "Parse: Meeting tomorrow at 3pm in room 401",
        "schema_description": '{"time": "string", "location": "string"}'
    }
)

print(response.json()["data"])
# {"time": "tomorrow at 3pm", "location": "room 401"}
```

## Common Use Cases

### Intent Classification
```python
data = client.extract(
    prompt="User says: I want to cancel my subscription",
    schema_description='{"intent": "cancel|upgrade|support|info", "urgency": "low|medium|high"}'
)
```

### Entity Extraction
```python
data = client.extract(
    prompt="Send invoice to john@example.com for $299.99",
    schema_description='{"email": "string", "amount": float, "currency": "string"}'
)
```

### Sentiment Analysis
```python
data = client.extract(
    prompt="This product is amazing! Best purchase ever!",
    schema_description='{"sentiment": "positive|negative|neutral", "confidence": "low|medium|high"}'
)
```

## Configuration

Want to customize? Set environment variables before `./start.sh`:

```bash
# Use a different model
OLLAMA_MODEL=llama3.2:3b ./start.sh

# Use a different port
PORT=9000 ./start.sh

# Use a custom API key
API_KEY=my-secret-key ./start.sh
```

## Stopping

Press `Ctrl+C` in the terminal running the API.

## Troubleshooting

**"Ollama not found"**
```bash
brew install ollama
```

**"Service not ready"**
- Make sure Ollama is running: `pgrep ollama`
- Check logs in the terminal

**"403 Forbidden"**
- Double-check your API key
- Make sure you're sending the `X-API-Key` header

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [client_example.py](client_example.py) for Python client code
- Run [test_api.py](test_api.py) to test all endpoints
- Visit http://localhost:8080/docs for interactive API docs

---

**Questions?** The API follows standard REST conventions and uses FastAPI, so any FastAPI documentation applies here too.
