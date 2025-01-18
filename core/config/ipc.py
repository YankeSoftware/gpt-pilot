from typing import Literal
from pydantic import BaseModel, Field

class LocalIPCConfig(BaseModel):
    """Configuration for local IPC."""
    type: Literal["ipc_client"] = Field("ipc_client")
    host: str = Field("localhost", description="Host to connect to")
    port: int = Field(7681, description="Port to connect to")