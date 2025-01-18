"""Base LLM client for gpt-pilot."""

import asyncio
import datetime
import json
from enum import Enum
from time import time
from typing import Any, Callable, Optional, Tuple

import httpx
from openai import APIConnectionError, APIError

from core.config import LLMConfig, LLMProvider
from core.llm.convo import Convo
from core.llm.request_log import RequestLog, LLMRequestLog, LLMRequestStatus, LLMError
from core.log import get_logger

logger = get_logger(__name__)

__all__ = ['BaseLLMClient', 'APIError', 'LLMError']

class LLMError(str, Enum):
    """LLM error types."""
    KEY_EXPIRED = "key_expired"
    RATE_LIMITED = "rate_limited"
    GENERIC_API_ERROR = "generic_api_error"

class APIError(Exception):
    """API error."""
    def __init__(self, message: str):
        self.message = message


class BaseLLMClient:
    """Base class for LLM clients."""

    def __init__(self, config: LLMConfig, error_handler=None):
        self.config = config
        self.error_handler = error_handler

    async def __call__(
        self,
        convo: Convo,
        temperature: Optional[float] = None,
        json_mode: bool = False,
        parser: Optional[Callable] = None,
        max_retries: int = 3
    ) -> tuple[str, RequestLog]:
        """
        Send a conversation to the LLM and get a response.

        Args:
            convo: The conversation to send
            temperature: Override the default temperature
            json_mode: Whether to request JSON output
            parser: Optional function to parse the response
            max_retries: Maximum number of retries on error

        Returns:
            Tuple of (response text, request log)
        """
        retries = 0
        while True:
            try:
                response, prompt_tokens, completion_tokens = await self._make_request(
                    convo,
                    temperature=temperature,
                    json_mode=json_mode
                )

                if parser:
                    try:
                        response = parser(response)
                    except Exception as e:
                        if retries < max_retries:
                            retries += 1
                            continue
                        raise APIError(f"Error parsing response: {e}")

                return response, RequestLog(
                    provider=self.config.provider,
                    model=self.config.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens
                )

            except Exception as e:
                if retries < max_retries and isinstance(e, (APIConnectionError, APIError)):
                    retries += 1
                    continue

                if self.error_handler:
                    if isinstance(e, APIConnectionError):
                        message = f"Error connecting to the LLM: API connection error: {e}"
                    elif isinstance(e, APIError):
                        message = f"Error connecting to the LLM: LLM had an error processing our request: {e}"
                    else:
                        message = f"Error connecting to the LLM: {e}"

                    if await self.error_handler(e, message):
                        continue

                raise

    async def _make_request(
        self,
        convo: Convo,
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> tuple[str, int, int]:
        """
        Make a request to the LLM.

        Args:
            convo: The conversation to send
            temperature: Override the default temperature
            json_mode: Whether to request JSON output

        Returns:
            Tuple of (response text, prompt tokens, completion tokens)
        """
        raise NotImplementedError

    async def api_check(self) -> bool:
        """
        Perform an LLM API check.
        
        Returns:
            True if the check was successful, False otherwise.
        """
        convo = Convo()
        msg = "This is a connection test. If you can see this, please respond only with 'START' and nothing else."
        convo.user(msg)
        resp, _log = await self(convo)
        return bool(resp)

    def rate_limit_sleep(self, err: Exception) -> Optional[datetime.timedelta]:
        """Calculate retry delay from rate limit headers."""
        raise NotImplementedError()
        
    @staticmethod
    def for_provider(provider: LLMProvider) -> type["BaseLLMClient"]:
        """Return LLM client for the specified provider."""
        from .anthropic_client import AnthropicClient
        from .azure_client import AzureClient
        from .deepseek_client import DeepSeekClient
        from .groq_client import GroqClient
        from .openai_client import OpenAIClient

        if provider == LLMProvider.OPENAI:
            return OpenAIClient
        elif provider == LLMProvider.ANTHROPIC:
            return AnthropicClient
        elif provider == LLMProvider.GROQ:
            return GroqClient
        elif provider == LLMProvider.AZURE:
            return AzureClient
        elif provider == LLMProvider.DEEPSEEK:
            return DeepSeekClient
        else:
            raise ValueError(f"Unsupported LLM provider: {provider.value}")