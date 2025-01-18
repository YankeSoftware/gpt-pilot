import datetime
import re
from typing import Optional, Callable, AsyncGenerator

import tiktoken
from httpx import Timeout
from openai import AsyncOpenAI, APIError, APIConnectionError
from openai.types.chat import ChatCompletionChunk

from core.config import LLMConfig
from core.llm.base import BaseLLMClient
from core.llm.convo import Convo
from core.llm.request_log import RequestLog
from core.log import get_logger

log = get_logger(__name__)
tokenizer = tiktoken.get_encoding("cl100k_base")


class OpenAIClient(BaseLLMClient):
    """OpenAI chat completion client."""

    def __init__(self, config: LLMConfig, error_handler: Optional[Callable] = None, stream_handler: Optional[Callable] = None):
        """Initialize the OpenAI client.
        
        Args:
            config: LLM configuration
            error_handler: Optional function to handle errors
            stream_handler: Optional function to handle streaming responses
        """
        super().__init__(config, error_handler)
        self.stream_handler = stream_handler
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.endpoint,
        )

    async def _make_request(
        self,
        convo: Convo,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> tuple[str, int, int]:
        """Make a request to the OpenAI API.
        
        Args:
            convo: The conversation to send
            temperature: Override the default temperature
            json_mode: Whether to request JSON output
            
        Returns:
            Tuple of (response text, prompt tokens, completion tokens)
        """
        completion_kwargs = {
            "model": self.config.model,
            "messages": [msg.__dict__ for msg in convo.messages],
            "temperature": self.config.temperature if temperature is None else temperature,
            "stream": True,
        }

        if json_mode:
            completion_kwargs["response_format"] = {"type": "json_object"}

        stream = await self.client.chat.completions.create(**completion_kwargs)
        
        content_parts = []
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_parts.append(content)
                if self.stream_handler:
                    await self.stream_handler(content)

        response = "".join(content_parts)
        
        # Get token counts from the last chunk
        usage = chunk.usage
        return response, usage.prompt_tokens, usage.completion_tokens

    def rate_limit_sleep(self, err: APIError) -> Optional[datetime.timedelta]:
        """
        OpenAI rate limits docs:
        https://platform.openai.com/docs/guides/rate-limits/error-mitigation
        Limit reset times are in "2h32m54s" format.
        """

        headers = err.response.headers
        if "x-ratelimit-remaining-tokens" not in headers:
            return None

        remaining_tokens = headers["x-ratelimit-remaining-tokens"]
        time_regex = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
        if remaining_tokens == 0:
            match = re.search(time_regex, headers["x-ratelimit-reset-tokens"])
        else:
            match = re.search(time_regex, headers["x-ratelimit-reset-requests"])

        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            seconds = int(match.group(3)) if match.group(3) else 0
            total_seconds = hours * 3600 + minutes * 60 + seconds
        else:
            # Not sure how this would happen, we would have to get a RateLimitError,
            # but nothing (or invalid entry) in the `reset` field. Using a sane default.
            total_seconds = 5

        return datetime.timedelta(seconds=total_seconds)


__all__ = ["OpenAIClient"]
