"""DeepSeek API Client"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1
MAX_RETRY_DELAY = 10

@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API client."""
    api_key: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 8192
    min_tokens: int = 1
    top_p: float = 0.95
    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = MAX_RETRIES

    def __post_init__(self):
        """Validate configuration parameters."""
        if not self.api_key:
            raise ValueError("API key is required")
        if not isinstance(self.temperature, (int, float)):
            raise ValueError("Temperature must be a number")
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        if not isinstance(self.max_tokens, int):
            raise ValueError("max_tokens must be an integer")
        if not isinstance(self.min_tokens, int):
            raise ValueError("min_tokens must be an integer")
        if self.min_tokens > self.max_tokens:
            raise ValueError("min_tokens cannot be greater than max_tokens")

class DeepSeekAPIError(Exception):
    """Base exception for DeepSeek API errors."""
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.request_id = request_id

    def __str__(self):
        parts = [self.args[0]]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " - ".join(parts)

class DeepSeekClient:
    """Client for the DeepSeek API with robust error handling and retries."""

    def __init__(self, config: DeepSeekConfig):
        """Initialize the DeepSeek client with configuration."""
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        logger.info(f"Initialized DeepSeek client with model: {config.model}")

    def _validate_response(self, data: Dict[str, Any]) -> None:
        """Validate the response format from DeepSeek API."""
        if not isinstance(data, dict):
            raise DeepSeekAPIError("Invalid response format: not a dictionary")
        
        if "choices" not in data:
            raise DeepSeekAPIError("Invalid response format: missing 'choices' field")
            
        if not isinstance(data["choices"], list) or not data["choices"]:
            raise DeepSeekAPIError("Invalid response format: empty or invalid 'choices'")
            
        choice = data["choices"][0]
        if not isinstance(choice, dict):
            raise DeepSeekAPIError("Invalid response format: choice is not a dictionary")
            
        if "message" not in choice:
            raise DeepSeekAPIError("Invalid response format: missing 'message' in choice")
            
        if "content" not in choice["message"]:
            raise DeepSeekAPIError("Invalid response format: missing 'content' in message")

    def _convert_message(
        self,
        message: Dict[str, Any],
        system_text: Optional[str] = None
    ) -> Dict[str, str]:
        """Convert message to DeepSeek format with validation."""
        if not isinstance(message, dict):
            raise DeepSeekAPIError(f"Invalid message format: {message}")
        
        if "role" not in message or "content" not in message:
            raise DeepSeekAPIError("Message missing required fields: role, content")

        role = message["role"]
        content = message["content"]
        
        # Convert list content to string if needed
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part["text"])
            content = " ".join(text_parts)
        elif not isinstance(content, str):
            raise DeepSeekAPIError(f"Unsupported content type: {type(content)}")
        
        # For first user message, prepend system text
        if role == "user" and system_text:
            content = f"{system_text}\n\nHuman: {content}"
        
        return {
            "role": role,
            "content": content
        }

    def _extract_system_text(self, system: Optional[Any]) -> Optional[str]:
        """Extract system text from various input formats with validation."""
        if system is None:
            return None
            
        if isinstance(system, str):
            return system.strip()
            
        if isinstance(system, dict):
            if system.get("type") == "text":
                return system["text"].strip()
            logger.warning("System prompt dict missing 'text' field or wrong type")
            return None
            
        if isinstance(system, list):
            text_parts = []
            for block in system:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block["text"].strip())
            return "\n".join(text_parts) if text_parts else None
            
        logger.warning(f"Unsupported system prompt type: {type(system)}")
        return None

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=INITIAL_RETRY_DELAY, max=MAX_RETRY_DELAY),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def create(
        self,
        *,
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system: Optional[Union[str, Dict[str, str], List[Dict[str, str]]]] = None,
    ) -> Dict[str, Any]:
        """Create a chat completion using the DeepSeek API with retries."""
        if not messages:
            raise DeepSeekAPIError("No messages provided")

        # Validate and adjust parameters
        max_tokens = min(
            max(max_tokens or self.config.max_tokens, self.config.min_tokens),
            self.config.max_tokens
        )
        temperature = min(
            max(temperature or self.config.temperature, 0.0),
            2.0
        )

        # Extract system text with improved handling
        system_text = self._extract_system_text(system)
        logger.debug(f"Extracted system text: {bool(system_text)}")
        
        # Convert messages
        try:
            deepseek_messages = []
            remaining_system = system_text
            for msg in messages:
                deepseek_msg = self._convert_message(msg, remaining_system)
                deepseek_messages.append(deepseek_msg)
                remaining_system = None  # Only use system text once
        except Exception as e:
            logger.error(f"Error converting messages: {e}", exc_info=True)
            raise DeepSeekAPIError(f"Message conversion error: {str(e)}")

        request_data = {
            "model": self.config.model,
            "messages": deepseek_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": self.config.top_p,
        }

        try:
            logger.debug(f"Sending request to DeepSeek API: {json.dumps(request_data)}")
            response = await self.client.post(
                DEEPSEEK_API_URL,
                json=request_data,
            )
            response.raise_for_status()
            data = response.json()

            # Get request ID from headers if available
            request_id = response.headers.get("x-request-id")
            if request_id:
                logger.debug(f"Request ID: {request_id}")

            # Validate response format
            self._validate_response(data)
            
            # Convert to common format
            completion = data["choices"][0]["message"]
            logger.debug("Successfully received and validated response")
            
            return {
                "role": "assistant",
                "content": [{
                    "type": "text",
                    "text": completion["content"]
                }]
            }

        except httpx.HTTPStatusError as e:
            error_body = {}
            try:
                error_body = e.response.json() if e.response.content else {}
            except json.JSONDecodeError:
                error_body = {"raw_content": e.response.content.decode()}
                
            error_message = error_body.get("error", {}).get("message", "Unknown error")
            request_id = e.response.headers.get("x-request-id")
            
            logger.error(
                f"API request failed: {error_message}",
                extra={"request_id": request_id},
                exc_info=True
            )
            
            raise DeepSeekAPIError(
                f"API request failed: {error_message}",
                status_code=e.response.status_code,
                response=error_body,
                request_id=request_id,
            )
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise DeepSeekAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise DeepSeekAPIError(f"Unexpected error: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup."""
        try:
            await self.client.aclose()
        except Exception as e:
            logger.error(f"Error closing client: {e}", exc_info=True)