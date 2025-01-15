"""Request logging for LLM interactions"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from core.config import LLMProvider

class LLMRequestStatus(str, Enum):
    """Status of an LLM request."""
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class LLMMessage:
    """A message in a conversation with an LLM."""
    role: str
    content: str

@dataclass
class LLMRequestLog:
    """Log of an LLM request and its outcome."""
    provider: LLMProvider
    model: str
    temperature: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration: float = 0.0
    messages: List[LLMMessage] = None
    response: Optional[str] = None
    error: Optional[str] = None
    status: LLMRequestStatus = LLMRequestStatus.SUCCESS

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