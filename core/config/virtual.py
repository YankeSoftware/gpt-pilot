from typing import Literal
from pydantic import BaseModel, Field

class VirtualConfig(BaseModel):
    """Virtual UI configuration."""
    type: Literal["virtual"] = Field("virtual", description="Virtual UI type")
    inputs: list[dict[str, str]] = Field(default=[], description="Predefined inputs for testing")