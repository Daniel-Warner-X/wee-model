"""
Test script for Garbage Model API
Run after starting the API with ./start.sh
"""

import os
import sys

import requests

# Get API key from environment or command line
API_KEY = os.getenv("API_KEY") or (sys.argv[1] if len(sys.argv) > 1 else None)

if not API_KEY:
    print("Error: No API key provided")
    print("Usage: python test_api.py YOUR_API_KEY")
    print("Or: export API_KEY=YOUR_API_KEY && python test_api.py")
    sys.exit(1)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def test_health():
    """Test health endpoint (no auth required)."""
    print("\n📊 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_extract():
    """Test structured data extraction."""
    print("\n🎯 Testing /extract endpoint...")

    data = {
        "prompt": "Extract information from: Meeting scheduled for Tuesday at 2pm in Conference Room A with John Smith to discuss Q4 budget",
        "schema_description": """Expected JSON schema:
        {
            "day": "string",
            "time": "string",
            "location": "string",
            "attendees": ["list of names"],
            "topic": "string"
        }""",
        "temperature": 0.3,
    }

    response = requests.post(f"{BASE_URL}/extract", headers=headers, json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Extracted data: {result['data']}")
        print(f"Model used: {result['model_used']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_chat():
    """Test chat completion."""
    print("\n💬 Testing /chat endpoint...")

    data = {
        "messages": [
            {"role": "user", "content": "Explain what an API is in one sentence."}
        ],
        "temperature": 0.7,
    }

    response = requests.post(f"{BASE_URL}/chat", headers=headers, json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content']}")
        print(f"Model used: {result['model_used']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_complete():
    """Test simple completion."""
    print("\n✍️  Testing /complete endpoint...")

    data = {"prompt": "Write a three-word tagline for a coffee shop", "temperature": 0.8}

    response = requests.post(f"{BASE_URL}/complete", headers=headers, json=data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content']}")
        print(f"Model used: {result['model_used']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🗑️  Garbage Model API Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")

    results = []
    results.append(("Health Check", test_health()))
    results.append(("Extract Data", test_extract()))
    results.append(("Chat Completion", test_chat()))
    results.append(("Simple Completion", test_complete()))

    print("\n" + "=" * 60)
    print("📋 Test Results")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
