from enum import Enum
from os.path import abspath, dirname, isdir, join
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import Annotated

class LogConfig(BaseModel):
    """
    Configuration for logging.
    """
    level: str = Field(
        "DEBUG",
        description="Logging level",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    format: str = Field(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        description="Logging format",
    )
    output: Optional[str] = Field(
        None,
        description="Output file for logs (if None, logs are printed to stderr)",
    )

class FileSystemType(str, Enum):
    """Type of filesystem to use."""
    LOCAL = "local"

class LLMProvider(str, Enum):
    """
    Supported LLM providers.
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LM_STUDIO = "lm-studio"
    AZURE = "azure"
    DEEPSEEK = "deepseek"

class LLMConfig(BaseModel):
    """
    Complete configuration for an LLM.
    """
    provider: LLMProvider = LLMProvider.DEEPSEEK
    model: str = Field(description="Model to use")
    base_url: Optional[str] = Field(
        None,
        description="Base URL for the provider's API (if different from the provider default)",
    )
    api_key: Optional[str] = Field(
        None,
        description="API key to use for authentication",
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature to use for sampling",
        ge=0.0,
        le=1.0,
    )
    connect_timeout: float = Field(
        default=60.0,
        description="Timeout (in seconds) for connecting to the provider's API",
        ge=0.0,
    )
    read_timeout: float = Field(
        default=20.0,
        description="Timeout (in seconds) for receiving data",
        ge=0.0,
    )
    extra: Optional[dict[str, Any]] = Field(
        None,
        description="Extra provider-specific configuration",
    )

class ProviderConfig(BaseModel):
    """LLM provider configuration."""
    base_url: Optional[str] = Field(None, description="Base URL for provider API")
    api_key: Optional[str] = Field(None, description="API key")
    connect_timeout: float = Field(60.0, description="Connection timeout")
    read_timeout: float = Field(20.0, description="Read timeout")
    extra: Optional[dict[str, Any]] = Field(None, description="Extra provider config")

class DBConfig(BaseModel):
    """Database configuration"""
    url: str = Field("sqlite+aiosqlite:///pythagora.db", description="Database connection URL")
    debug_sql: bool = Field(False, description="Log all SQL queries")

class UIConfig(BaseModel):
    """UI configuration"""
    type: str = Field("plain", description="UI type")

class AgentConfig(BaseModel):
    """Agent configuration."""
    provider: LLMProvider = Field(default=LLMProvider.DEEPSEEK, description="Default LLM provider")
    model: str = Field(default="deepseek-chat", description="Default model name")
    temperature: float = Field(default=0.0, description="Default temperature")

class Config(BaseModel):
    """Main configuration."""
    agent: dict[str, AgentConfig] = Field(
        default={
            "default": AgentConfig()
        },
        description="Agent configurations"
    )
    llm: dict[LLMProvider, ProviderConfig] = Field(
        default={
            LLMProvider.OPENAI: ProviderConfig(),
            LLMProvider.ANTHROPIC: ProviderConfig(),
            LLMProvider.DEEPSEEK: ProviderConfig(
                base_url="https://api.deepseek.com/v1",
                extra={
                    "max_tokens": 8192,
                    "top_p": 0.95,
                }
            ),
        }
    )
    log: LogConfig = Field(default_factory=LogConfig)
    db: DBConfig = Field(default_factory=DBConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    def llm_for_provider(self, provider: LLMProvider) -> LLMConfig:
        """Get LLM configuration for a provider."""
        provider_config = self.llm.get(provider)
        if not provider_config:
            raise ValueError(f"No configuration found for provider {provider}")
            
        return LLMConfig(
            provider=provider,
            model="deepseek-chat" if provider == LLMProvider.DEEPSEEK else "default",
            base_url=provider_config.base_url,
            api_key=provider_config.api_key,
            temperature=0.7,
            connect_timeout=provider_config.connect_timeout,
            read_timeout=provider_config.read_timeout,
            extra=provider_config.extra
        )

class ConfigLoader:
    """Configuration loader."""
    config: Config
    config_path: Optional[str]

    def __init__(self):
        self.config_path = None
        self.config = Config()

    def from_json(self, config: str) -> Config:
        """Parse JSON into Config object."""
        return Config.model_validate_json(config)

    def load(self, path: str) -> Config:
        """Load config from file."""
        with open(path, "rb") as f:
            raw_config = f.read()
            
        if b"\x00" in raw_config:
            encoding = "utf-16"
        else:
            encoding = "utf-8"
            
        text_config = raw_config.decode(encoding)
        self.config = self.from_json(text_config)
        self.config_path = path
        return self.config

# Global instances
loader = ConfigLoader()

def get_config() -> Config:
    """Get current configuration."""
    return loader.config