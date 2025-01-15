"""Base LLM client for gpt-pilot."""

import asyncio
import datetime
import json
from time import time
from typing import Any, Callable, Optional, Tuple

import httpx

from core.config import LLMConfig, LLMProvider
from core.llm.convo import Convo
from core.llm.request_log import LLMRequestLog, LLMRequestStatus
from core.log import get_logger

logger = get_logger(__name__)

class BaseLLMClient:
    """Base asynchronous streaming client for language models."""

    provider: LLMProvider

    def __init__(
        self,
        config: LLMConfig,
        *,
        stream_handler: Optional[Callable] = None,
        error_handler: Optional[Callable] = None,
    ):
        """Initialize the client with the given configuration."""
        self.config = config
        self.stream_handler = stream_handler
        self.error_handler = error_handler
        self._init_client()

    def _init_client(self):
        """Initialize the HTTP client."""
        raise NotImplementedError()

    async def _make_request(
        self,
        convo: Convo,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> Tuple[str, int, int]:
        """
        Call the LLM with the given conversation.

        Args:
            convo: Conversation to send
            temperature: Optional temperature override
            json_mode: Whether to request JSON output

        Returns:
            Tuple of (response_text, prompt_tokens, completion_tokens)
        """
        raise NotImplementedError()

    async def __call__(
        self,
        convo: Convo,
        *,
        temperature: Optional[float] = None,
        max_retries: int = 3,
        json_mode: bool = False,
    ) -> Tuple[str, LLMRequestLog]:
        """
        Invoke the LLM with given conversation.

        Args:
            convo: Conversation to send
            temperature: Optional temperature override
            max_retries: Maximum retries on failure
            json_mode: Whether to request JSON output

        Returns:
            Tuple of response text and request log
        """
        request_log = LLMRequestLog(
            provider=self.provider,
            model=self.config.model,
            temperature=temperature or self.config.temperature,
            prompts=[msg.content for msg in convo.messages]
        )

        t0 = time()
        remaining_retries = max_retries

        while True:
            if remaining_retries == 0:
                error_msg = request_log.error or "Maximum retries exceeded"
                if self.error_handler:
                    should_retry = await self.error_handler("error", message=error_msg)
                    if should_retry:
                        remaining_retries = max_retries
                        continue
                raise Exception(error_msg)

            remaining_retries -= 1
            request_log.status = LLMRequestStatus.SUCCESS
            request_log.error = None
            request_log.response = None

            try:
                response, prompt_tokens, completion_tokens = await self._make_request(
                    convo,
                    temperature=temperature,
                    json_mode=json_mode,
                )
                request_log.prompt_tokens = prompt_tokens
                request_log.completion_tokens = completion_tokens
                request_log.response = response
                break

            except httpx.HTTPStatusError as e:
                request_log.status = LLMRequestStatus.ERROR
                request_log.error = str(e)
                if e.response.status_code == 429:  # Rate limit
                    wait_time = self.rate_limit_sleep(e)
                    if wait_time:
                        message = f"Rate limited. Sleeping for {wait_time.seconds}s..."
                        if self.error_handler:
                            await self.error_handler("rate_limit", message=message)
                        await asyncio.sleep(wait_time.seconds)
                        continue
                raise

            except Exception as e:
                request_log.status = LLMRequestStatus.ERROR
                request_log.error = str(e)
                raise

        t1 = time()
        request_log.duration = t1 - t0

        return response, request_log

    def rate_limit_sleep(self, err: Exception) -> Optional[datetime.timedelta]:
        """Calculate retry delay from rate limit headers."""
        raise NotImplementedError()