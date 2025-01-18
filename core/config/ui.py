from typing import Literal
from pydantic import BaseModel, Field

class PlainConfig(BaseModel):
    """Plain console UI configuration."""
    type: Literal["plain"] = Field("plain", description="Plain console UI")

class IPCClientConfig(BaseModel):
    """IPC client UI configuration."""
    type: Literal["ipc-client"] = Field("ipc-client", description="IPC client UI")
    host: str = Field("localhost", description="IPC server host")
    port: int = Field(1234, description="IPC server port")

UIConfig = PlainConfig | IPCClientConfig

