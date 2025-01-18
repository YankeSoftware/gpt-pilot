from typing import Literal, Union
from pydantic import BaseModel, Field

from core.config.ipc import LocalIPCConfig
from core.config.virtual import VirtualConfig

class PlainConfig(BaseModel):
    """Plain UI configuration."""
    type: Literal["plain"] = Field("plain", description="Plain UI type")

# Union type for all UI configurations
UIConfig = Union[PlainConfig, LocalIPCConfig, VirtualConfig]