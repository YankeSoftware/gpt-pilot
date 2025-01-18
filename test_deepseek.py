#!/usr/bin/env python

import asyncio
from core.config import get_config, loader
from core.llm.convo import Convo
from core.llm.base import BaseLLMClient


async def test_deepseek():
    """Test the DeepSeek integration with a simple conversation."""
    print("Loading configuration...")
    config = loader.load("config.json")
    llm_config = config.llm_for_agent("default")

    print(f"Using provider: {llm_config.provider}")
    print(f"Using model: {llm_config.model}")

    # Create client for the default agent
    client_class = BaseLLMClient.for_provider(llm_config.provider)
    client = client_class(llm_config)

    print("Testing DeepSeek API connection...")
    convo = Convo()
    convo.user("Tell me a short joke about programming.")

    try:
        response, request_log = await client(convo)
        print("\nDeepSeek Response:")
        print("-----------------")
        print(response)
        print("\nRequest Stats:")
        print("--------------")
        print(f"Prompt tokens: {request_log.prompt_tokens}")
        print(f"Completion tokens: {request_log.completion_tokens}")
        print(f"Response time: {request_log.duration:.2f}s")
        return True
    except Exception as e:
        print(f"\nError testing DeepSeek:")
        print(f"{str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_deepseek())
    exit(0 if success else 1)