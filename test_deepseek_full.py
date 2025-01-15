import asyncio
import httpx
from core.config import Config, LLMProvider, ProviderConfig

async def test_deepseek():
    """Test the DeepSeek integration."""
    print("Setting up configuration...")
    
    config = Config(llm={
        LLMProvider.DEEPSEEK: ProviderConfig(
            api_key="sk-aaa0a2708abf436dbe5d420bd36d68f5",
            base_url="https://api.deepseek.com/v1/chat/completions",
            extra={
                "max_tokens": 8192,
                "top_p": 0.95
            }
        )
    })

    print(f"Using provider: {LLMProvider.DEEPSEEK}")
    provider_config = config.llm[LLMProvider.DEEPSEEK]

    async with httpx.AsyncClient(
        base_url=provider_config.base_url,
        headers={
            "Authorization": f"Bearer {provider_config.api_key}",
            "Content-Type": "application/json",
        },
        timeout=60.0
    ) as client:
        try:
            print("\nSending request to DeepSeek API...")
            response = await client.post(
                "",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Tell me a Python programming joke."}],
                    "temperature": 0.7,
                    "max_tokens": provider_config.extra.get("max_tokens", 8192),
                    "top_p": provider_config.extra.get("top_p", 0.95),
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