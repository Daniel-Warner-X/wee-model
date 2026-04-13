#!/bin/bash

# Garbage Model - Startup Script
# One-command setup for Ollama-based API service

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODEL="${OLLAMA_MODEL:-qwen2.5:7b}"
PORT="${PORT:-8080}"
API_KEY="${API_KEY:-}"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}🗑️  Garbage Model API Startup${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}✗ Ollama not found${NC}"
    echo -e "${YELLOW}Install with: brew install ollama${NC}"
    echo -e "${YELLOW}Or visit: https://ollama.ai${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ollama found${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo -e "${GREEN}✓ Ollama started${NC}"
else
    echo -e "${GREEN}✓ Ollama already running${NC}"
fi

# Pull model if not present
echo -e "${YELLOW}Checking for model ${MODEL}...${NC}"
if ! ollama list | grep -q "${MODEL}"; then
    echo -e "${YELLOW}Pulling model ${MODEL} (this may take a few minutes)...${NC}"
    ollama pull "${MODEL}"
    echo -e "${GREEN}✓ Model ${MODEL} ready${NC}"
else
    echo -e "${GREEN}✓ Model ${MODEL} already available${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Generate API key if not provided
if [ -z "$API_KEY" ]; then
    # Generate a random API key
    API_KEY="grbg-$(openssl rand -hex 16 2>/dev/null || cat /dev/urandom | LC_ALL=C tr -dc 'a-f0-9' | head -c 32)"
fi

export API_KEY
export OLLAMA_MODEL="${MODEL}"

echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${BLUE}Service Information:${NC}"
echo -e "  Endpoint: ${GREEN}http://localhost:${PORT}${NC}"
echo -e "  API Docs: ${GREEN}http://localhost:${PORT}/docs${NC}"
echo -e "  API Key:  ${GREEN}${API_KEY}${NC}"
echo -e "  Model:    ${GREEN}${MODEL}${NC}"
echo ""
echo -e "${YELLOW}Add this header to your requests:${NC}"
echo -e "  ${BLUE}X-API-Key: ${API_KEY}${NC}"
echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${YELLOW}Starting API server...${NC}"
echo ""

# Start the API
python3 app.py
