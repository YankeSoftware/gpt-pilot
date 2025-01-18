"""Conversation handling for LLM interactions."""

import textwrap
from dataclasses import dataclass
from typing import Optional, Any
import json

@dataclass
class Message:
    """A message in a conversation."""
    role: str
    content: str
    name: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to message fields."""
        return getattr(self, key)

    def __eq__(self, other: Any) -> bool:
        """Compare message with another message or dict."""
        if isinstance(other, dict):
            return (
                self.role == other.get("role") and
                self.content == other.get("content") and
                (self.name == other.get("name") if "name" in other else True)
            )
        return super().__eq__(other)

class Convo:
    """A conversation with an LLM."""

    def __init__(self, system_prompt: Optional[str] = None):
        """Initialize a new conversation."""
        self.messages: list[Message] = []
        if system_prompt:
            self.system(system_prompt)

    def add(self, role: str, content: Any, name: Optional[str] = None) -> 'Convo':
        """Add a message to the conversation.
        
        Args:
            role: The role of the message sender (system, user, assistant, function)
            content: The message content
            name: Optional name for the message sender
            
        Returns:
            self for chaining
        """
        if role not in {"system", "user", "assistant", "function"}:
            raise ValueError(f"Unknown role: {role}")

        if content is None:
            raise ValueError("Message content cannot be None")

        if isinstance(content, dict):
            content = content
        elif not isinstance(content, str):
            content = str(content)

        if isinstance(content, str):
            content = textwrap.dedent(content).strip()
            if content.startswith("\n"):
                content = "\n" + content

        if not content:
            raise ValueError("Message content cannot be empty")

        self.messages.append(Message(role=role, content=content, name=name))
        return self

    def user(self, content: str | dict, name: Optional[str] = None) -> 'Convo':
        """Add a user message."""
        return self.add("user", content, name)

    def assistant(self, content: str | dict, name: Optional[str] = None) -> 'Convo':
        """Add an assistant message."""
        return self.add("assistant", content, name)

    def system(self, content: str | dict, name: Optional[str] = None) -> 'Convo':
        """Add a system message."""
        return self.add("system", content, name)

    def function(self, content: str | dict, name: Optional[str] = None) -> 'Convo':
        """Add a function message."""
        if not isinstance(content, (str, dict)):
            raise TypeError("Function message content must be str or dict")
        return self.add("function", content, name)

    def fork(self) -> 'Convo':
        """Create a copy of this conversation."""
        new_convo = Convo()
        new_convo.messages = self.messages.copy()
        return new_convo

    def after(self, other: 'Convo') -> 'Convo':
        """Create a new conversation with messages that come after other."""
        if not other.messages:
            return self.fork()

        last_common_idx = -1
        for i, (msg1, msg2) in enumerate(zip(self.messages, other.messages)):
            if msg1 != msg2:
                break
            last_common_idx = i

        new_convo = Convo()
        new_convo.messages = self.messages[last_common_idx + 1:]
        return new_convo

    def __iter__(self):
        """Iterate over messages in the conversation."""
        return iter(self.messages)

    def __len__(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)

    @property
    def last(self) -> Optional[Message]:
        """Get the last message in the conversation."""
        return self.messages[-1] if self.messages else None