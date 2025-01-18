import asyncio
import json
from dataclasses import dataclass
import httpx
from typing import Optional
from core.config import LLMProvider, Config

async def test_deepseek():
    config = Config(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="sk-aaa0a2708abf436dbe5d420bd36d68f5",
        temperature=0.7
    )
    
    print(f"Using model: {config.model}")
    
    async with httpx.AsyncClient(
        base_url="https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        timeout=60.0
    ) as client:
        try:
            print("\nSending request to DeepSeek API...")
            response = await client.post(
                "",
                json={
                    "model": config.model,
                    "messages": [{"role": "user", "content": "Tell me a programming joke."}],
                    "temperature": config.temperature,
                    "max_tokens": 8192,
                }
            )
            response.raise_for_status()
            data = response.json()
            print("\nDeepSeek Response:")
            print("-" * 40)
            print(data["choices"][0]["message"]["content"])
            print("\nResponse tokens:", data.get("usage", {}).get("completion_tokens", 0))
            return True
        except Exception as e:
            print(f"\nError: {str(e)}")
            if hasattr(e, "response"):
                try:
                    print(f"Response: {e.response.text}")
                except:
                    pass
            return False

if __name__ == "__main__":
    success = asyncio.run(test_deepseek())
    exit(0 if success else 1)