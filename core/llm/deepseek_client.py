"""DeepSeek client for gpt-pilot"""

import json
import datetime
from typing import Optional, Dict, Any, List, Tuple

import httpx
from core.config import LLMProvider
from core.llm.base import BaseLLMClient
from core.llm.convo import Convo
from core.llm.request_log import LLMRequestLog, LLMRequestStatus
from core.log import get_logger

logger = get_logger(__name__)

class DeepSeekClient(BaseLLMClient):
    """Client implementation for DeepSeek's LLM API"""
    
    provider = LLMProvider.DEEPSEEK

    def _init_client(self):
        """Initialize the DeepSeek client with proper configuration."""
        base_url = self.config.base_url or "https://api.deepseek.com/v1/chat/completions"
        
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
        )
        logger.info(f"Initialized DeepSeek client with model: {self.config.model}")

    async def _make_request(
        self,
        convo: Convo,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> Tuple[str, int, int]:
        """
        Make a request to the DeepSeek API with retries.

        Args:
            convo: Conversation history
            temperature: Optional temperature override
            json_mode: Whether to request JSON output

        Returns:
            Tuple of (response_text, prompt_tokens, completion_tokens)
        """
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

            # Handle function calls to user messages
            role = "user" if msg.role == "function" else msg.role
            
            # For first user message, prepend system content if any
            if role == "user" and system_content and not messages:
                content = f"{system_content}\n\nHuman: {msg.content}"
                system_content = None
            else:
                content = msg.content

            # Merge consecutive messages of same role
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += f"\n\n{content}"
            else:
                messages.append({"role": role, "content": content})

        request_data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": self.config.extra.get("max_tokens", 8192) if self.config.extra else 8192,
            "top_p": self.config.extra.get("top_p", 0.95) if self.config.extra else 0.95,
        }
        
        if json_mode:
            request_data["response_format"] = {"type": "json_object"}

        try:
            response = await self.client.post("", json=request_data)
            response.raise_for_status()
            data = response.json()

            # Get tokens used
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            response_text = data["choices"][0]["message"]["content"]

            # Stream response if handler provided
            if self.stream_handler:
                await self.stream_handler(response_text)

            logger.debug(f"Got response ({completion_tokens} tokens): {response_text[:100]}...")
            return response_text, prompt_tokens, completion_tokens

        except httpx.HTTPStatusError as e:
            error_body = {}
            try:
                error_body = e.response.json()
            except json.JSONDecodeError:
                error_body = {"raw": e.response.text}
                
            error_msg = error_body.get("error", {}).get("message", str(e))
            logger.error(f"DeepSeek API error: {error_msg}", exc_info=True)
            raise

        except Exception as e:
            logger.error(f"Unexpected error calling DeepSeek API: {e}", exc_info=True)
            raise

    def rate_limit_sleep(self, err: Exception) -> Optional[datetime.timedelta]:
        """
        Calculate retry delay from rate limit headers.
        
        Args:
            err: The exception that triggered the retry

        Returns:
            Optional time to wait before retry
        """
        try:
            if not hasattr(err, "response"):
                return None

            # Check for rate limit error
            if err.response.status_code == 429:
                # Try to get retry delay from headers
                reset_time = err.response.headers.get("x-ratelimit-reset")
                if reset_time:
                    reset_timestamp = int(reset_time)
                    now = datetime.datetime.now().timestamp()
                    delay_seconds = max(1, reset_timestamp - now)
                    return datetime.timedelta(seconds=delay_seconds)

                # Default 5 second retry if no header
                return datetime.timedelta(seconds=5)

            return None

        except Exception as e:
            logger.warning(f"Error parsing rate limit headers: {e}")
            return None