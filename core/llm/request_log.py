"""Request logging for LLM interactions"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from core.config import LLMProvider

class LLMError(str, Enum):
    """Types of LLM errors."""
    GENERIC_API_ERROR = "generic_api_error"
    RATE_LIMITED = "rate_limited"

class LLMRequestStatus(str, Enum):
    """Status of an LLM request."""
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class RequestLog:
    """Simple log of an LLM request."""
    provider: LLMProvider
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class LLMRequestLog:
    """Detailed log of an LLM request and its outcome."""
    provider: LLMProvider
    model: str
    temperature: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration: float = 0.0
    status: LLMRequestStatus = LLMRequestStatus.SUCCESS
    response: Optional[str] = None
    error: Optional[str] = None
    prompts: List[str] = field(default_factory=list)

    def log_it(self) -> dict:
        """Convert to a format suitable for logging."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "temperature": self.temperature,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "duration": self.duration,
            "status": self.status,
            "error": self.error if self.error else None
        }