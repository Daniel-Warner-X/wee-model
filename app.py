"""
Garbage Model - Standalone Ollama API Service
A simple API service for structured data extraction using Ollama.
"""

import json
import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Any

import ollama
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API Key security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)
VALID_API_KEY = os.getenv("API_KEY", "garbage-key-" + secrets.token_urlsafe(32))


# Models
class ExtractionRequest(BaseModel):
    """Request for structured data extraction."""

    prompt: str = Field(
        ...,
        description="The prompt/text to extract structured data from",
        min_length=1,
    )
    schema_description: str = Field(
        ...,
        description="Description of the expected JSON schema",
        min_length=1,
    )
    temperature: float = Field(
        default=0.3,
        description="Sampling temperature (0.0-1.0, lower = more deterministic)",
        ge=0.0,
        le=1.0,
    )


class ChatRequest(BaseModel):
    """Request for chat completion."""

    messages: list[dict[str, Any]] = Field(
        ..., description="List of messages with 'role' and 'content' keys"
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    format_json: bool = Field(
        default=False, description="Request JSON formatted response"
    )
    tools: list[dict[str, Any]] | None = Field(
        default=None, description="List of tools/functions available for the model to call"
    )


class CompletionRequest(BaseModel):
    """Request for text completion."""

    prompt: str = Field(..., description="Input prompt", min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    format_json: bool = Field(default=False)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model: str
    ollama_available: bool


class ExtractionResponse(BaseModel):
    """Response from extraction endpoint."""

    data: dict[str, Any]
    model_used: str


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    content: str | None = None
    model_used: str
    tool_calls: list[dict[str, Any]] | None = None


# Ollama client
class OllamaService:
    """Service for interacting with Ollama."""

    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.client = ollama.Client()

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

    def ensure_model(self) -> bool:
        """Ensure model is pulled."""
        try:
            response = self.client.list()

            # Handle both dict response and object response
            if isinstance(response, dict):
                models_list = response.get("models", [])
            else:
                models_list = getattr(response, "models", [])

            # Extract model names - try 'model' key first, then 'name'
            model_names = []
            for m in models_list:
                if isinstance(m, dict):
                    model_names.append(m.get("model") or m.get("name"))
                else:
                    model_names.append(getattr(m, "model", None) or getattr(m, "name", None))

            logger.info(f"Available models: {model_names}")

            if self.model not in model_names:
                logger.info(f"Pulling model {self.model}...")
                self.client.pull(self.model)
                logger.info(f"Model {self.model} ready")
            else:
                logger.info(f"Model {self.model} already available")

            return True
        except Exception as e:
            logger.error(f"Failed to ensure model: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def extract_structured_data(
        self, prompt: str, schema_description: str, temperature: float = 0.3
    ) -> dict[str, Any]:
        """Extract structured data using JSON format."""
        full_prompt = f"""{prompt}

{schema_description}

Return ONLY valid JSON matching the schema above. Do not include any explanation or additional text."""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                format="json",
                options={"temperature": temperature},
            )

            response_text = response["message"]["content"]
            logger.info(f"LLM response: {response_text[:200]}...")

            return json.loads(response_text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON response: {e}") from e
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise

    def chat(
        self, messages: list[dict[str, Any]], temperature: float = 0.7, format_json: bool = False, tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Send chat messages."""
        try:
            chat_params = {
                "model": self.model,
                "messages": messages,
                "options": {"temperature": temperature},
            }

            if format_json:
                chat_params["format"] = "json"

            if tools:
                chat_params["tools"] = tools

            response = self.client.chat(**chat_params)

            message = response["message"]
            result = {
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls")
            }

            return result
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise


# Global service instance
ollama_service: OllamaService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    global ollama_service

    logger.info("Starting Garbage Model API...")

    # Initialize Ollama service
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    ollama_service = OllamaService(model=model)

    if not ollama_service.is_available():
        logger.error("Ollama service not available!")
        logger.error("Make sure Ollama is running: ollama serve")
        raise RuntimeError("Ollama service not available")

    if not ollama_service.ensure_model():
        logger.error(f"Failed to ensure model {model}")
        raise RuntimeError("Model not available")

    logger.info(f"✓ Garbage Model API ready with {model}")
    logger.info(f"✓ API Key: {VALID_API_KEY}")

    yield

    logger.info("Shutting down Garbage Model API...")


# FastAPI app
app = FastAPI(
    title="Garbage Model API",
    description="Simple API for structured data extraction using Ollama",
    version="1.0.0",
    lifespan=lifespan,
)


def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Verify API key."""
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key


@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "Garbage Model API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health():
    """Health check endpoint."""
    if not ollama_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return HealthResponse(
        status="healthy" if ollama_service.is_available() else "unhealthy",
        model=ollama_service.model,
        ollama_available=ollama_service.is_available(),
    )


@app.post("/extract", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_data(
    request: ExtractionRequest,
    _: str = Depends(verify_api_key),
):
    """
    Extract structured data from text.

    Requires API key in X-API-Key header.
    """
    if not ollama_service:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        result = ollama_service.extract_structured_data(
            prompt=request.prompt,
            schema_description=request.schema_description,
            temperature=request.temperature,
        )

        return ExtractionResponse(data=result, model_used=ollama_service.model)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=500, detail="Extraction failed")


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    _: str = Depends(verify_api_key),
):
    """
    Chat completion with optional tool/function calling support.

    Requires API key in X-API-Key header.
    """
    if not ollama_service:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        result = ollama_service.chat(
            messages=request.messages,
            temperature=request.temperature,
            format_json=request.format_json,
            tools=request.tools,
        )

        return ChatResponse(
            content=result["content"],
            tool_calls=result["tool_calls"],
            model_used=ollama_service.model
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")


@app.post("/complete", response_model=ChatResponse, tags=["Chat"])
async def complete(
    request: CompletionRequest,
    _: str = Depends(verify_api_key),
):
    """
    Simple text completion.

    Requires API key in X-API-Key header.
    """
    if not ollama_service:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        result = ollama_service.chat(
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            format_json=request.format_json,
        )

        return ChatResponse(
            content=result["content"],
            tool_calls=result["tool_calls"],
            model_used=ollama_service.model
        )

    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(status_code=500, detail="Completion failed")


if __name__ == "__main__":
    # Print startup info
    print("=" * 80)
    print("🗑️  GARBAGE MODEL API")
    print("=" * 80)
    print(f"API Key: {VALID_API_KEY}")
    print("Endpoint: http://localhost:8080")
    print("Docs: http://localhost:8080/docs")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
