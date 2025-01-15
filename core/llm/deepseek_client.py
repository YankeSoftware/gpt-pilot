"""DeepSeek client for gpt-pilot"""

import json
import logging
import datetime
from typing import Optional, Dict, Any, List, Tuple

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from core.config import LLMProvider
from core.llm.base import BaseLLMClient
from core.llm.convo import Convo
from core.log import get_logger

logger = get_logger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1
MAX_RETRY_DELAY = 10

class DeepSeekClient(BaseLLMClient):
    """Client implementation for DeepSeek's LLM API"""
    
    provider = LLMProvider.DEEPSEEK

    def _init_client(self):
        """Initialize the DeepSeek client with proper configuration."""
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url or DEEPSEEK_API_URL,
            timeout=httpx.Timeout(
                connect=self.config.connect_timeout,
                read=self.config.read_timeout
            ),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        logger.info(f"Initialized DeepSeek client with model: {self.config.model}")

    async def _convert_messages(self, convo: Convo) -> List[Dict[str, str]]:
        """Convert conversation messages to DeepSeek format."""
        messages = []
        system_content = None

        # Extract system message if present
        for msg in convo.messages:
            if msg.role == "system":
                if system_content:
                    system_content += f"\n\n{msg.content}"
                else:
                    system_content = msg.content
                continue

            # Handle function messages as user messages
            role = "user" if msg.role == "function" else msg.role
            
            # For first user message, prepend system content if any
            if role == "user" and system_content and not messages:
                content = f"{system_content}\n\nHuman: {msg.content}"
                system_content = None  # Only use system once
            else:
                content = msg.content

            # Merge consecutive messages of same role
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += f"\n\n{content}"
            else:
                messages.append({"role": role, "content": content})

        return messages

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=INITIAL_RETRY_DELAY, max=MAX_RETRY_DELAY),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _make_request(
        self,
        convo: Convo,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> Tuple[str, int, int]:
        """
        Make a request to the DeepSeek API with automatic retries.

        Args:
            convo: The conversation to send
            temperature: Optional temperature override
            json_mode: Whether to request JSON output

        Returns:
            Tuple of (response_text, prompt_tokens, completion_tokens)
        """
        messages = await self._convert_messages(convo)
        
        request_data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": self.config.extra.get("max_tokens", 8192),
            "top_p": self.config.extra.get("top_p", 0.95),
            "response_format": {"type": "json_object"} if json_mode else None,
        }
        
        # Remove None values
        request_data = {k: v for k, v in request_data.items() if v is not None}

        try:
            response = await self.client.post(
                "",  # Base URL already set in client
                json=request_data
            )
            response.raise_for_status()
            data = response.json()

            # Validate response format
            if not isinstance(data, dict) or "choices" not in data:
                raise ValueError("Invalid response format: missing 'choices'")
            
            if not data["choices"] or not isinstance(data["choices"][0], dict):
                raise ValueError("Invalid response format: empty or invalid choices")
            
            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise ValueError("Invalid response format: missing message content")

            # Get tokens used
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            response_text = choice["message"]["content"]

            # Stream response chunks if handler provided
            if self.stream_handler:
                await self.stream_handler(response_text)

            return response_text, prompt_tokens, completion_tokens

        except httpx.HTTPStatusError as e:
            error_body = {}
            try:
                error_body = e.response.json()
            except json.JSONDecodeError:
                error_body = {"raw": e.response.text}
                
            error_msg = error_body.get("error", {}).get("message", str(e))
            logger.error(f"DeepSeek API error: {error_msg}")
            raise  # Let tenacity handle retry

        except Exception as e:
            logger.error(f"Unexpected error calling DeepSeek API: {e}")
            raise

    def rate_limit_sleep(self, err: Exception) -> Optional[datetime.timedelta]:
        """
        Calculate retry delay from rate limit headers.
        
        Args:
            err: The rate limit exception
            
        Returns:
            Optional time to wait before retry
        """
        try:
            if not hasattr(err, "response"):
                return None
                
            headers = err.response.headers
            reset_time = headers.get("x-ratelimit-reset")
            
            if reset_time:
                # Convert reset timestamp to delay
                reset_timestamp = int(reset_time)
                now = datetime.datetime.now().timestamp()
                delay_seconds = max(1, reset_timestamp - now)
                return datetime.timedelta(seconds=delay_seconds)
            
            # Default retry delay if no header
            return datetime.timedelta(seconds=INITIAL_RETRY_DELAY)
            
        except Exception as e:
            logger.warning(f"Error parsing rate limit headers: {e}")
            return None