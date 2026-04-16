"""
Example Python client for Wee Model API

Install requests first:
    pip install requests
"""

import os

import requests


class WeeModelClient:
    """Simple client for Wee Model API."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8080"):
        """
        Initialize client.

        Args:
            api_key: Your API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    def health(self) -> dict:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def extract(
        self, prompt: str, schema_description: str, temperature: float = 0.3
    ) -> dict:
        """
        Extract structured data from text.

        Args:
            prompt: Text to extract data from
            schema_description: Description of expected JSON schema
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Extracted data dict
        """
        data = {
            "prompt": prompt,
            "schema_description": schema_description,
            "temperature": temperature,
        }

        response = requests.post(f"{self.base_url}/extract", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["data"]

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        format_json: bool = False,
    ) -> str:
        """
        Chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            format_json: Request JSON formatted response

        Returns:
            Response content string
        """
        data = {
            "messages": messages,
            "temperature": temperature,
            "format_json": format_json,
        }

        response = requests.post(f"{self.base_url}/chat", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["content"]

    def complete(self, prompt: str, temperature: float = 0.7, format_json: bool = False) -> str:
        """
        Simple text completion.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            format_json: Request JSON formatted response

        Returns:
            Completion text
        """
        data = {"prompt": prompt, "temperature": temperature, "format_json": format_json}

        response = requests.post(f"{self.base_url}/complete", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["content"]


# Example usage
if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Set API_KEY environment variable")
        exit(1)

    # Initialize client
    client = WeeModelClient(api_key=api_key)

    # Check health
    print("Health:", client.health())

    # Extract structured data
    print("\n--- Structured Extraction ---")
    result = client.extract(
        prompt="Customer email: John ordered 5 laptops on March 15th, shipping to NYC",
        schema_description='{"customer": "string", "quantity": int, "product": "string", "date": "string", "location": "string"}',
    )
    print(f"Extracted: {result}")

    # Chat
    print("\n--- Chat Completion ---")
    response = client.chat(
        messages=[
            {"role": "user", "content": "What are the benefits of async programming?"}
        ]
    )
    print(f"Response: {response}")

    # Simple completion
    print("\n--- Simple Completion ---")
    response = client.complete("List 3 programming languages: ")
    print(f"Completion: {response}")
