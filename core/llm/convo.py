"""Conversation handling for LLM interactions."""

from dataclasses import dataclass
from typing import List

@dataclass
class Message:
    """A message in a conversation."""
    role: str
    content: str

class Convo:
    """A conversation with an LLM."""
    def __init__(self):
        self.messages: List[Message] = []
        self.prompt_log: List[str] = []

    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
        self.prompt_log.append(content)

    def user(self, content: str):
        """Add a user message."""
        self.add_message("user", content)

    def assistant(self, content: str):
        """Add an assistant message."""
        self.add_message("assistant", content)

    def system(self, content: str):
        """Add a system message."""
        self.add_message("system", content)

    def function(self, content: str):
        """Add a function result message."""
        self.add_message("function", content)

    def fork(self) -> 'Convo':
        """Create a copy of this conversation."""
        convo = Convo()
        convo.messages = self.messages.copy()
        convo.prompt_log = self.prompt_log.copy()
        return convo