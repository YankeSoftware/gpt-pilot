from enum import Enum
from os.path import abspath, dirname, isdir, join
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field

from core.config.adapter import UIAdapter
from core.config.ipc import LocalIPCConfig
from core.config.ui import UIConfig
from core.config.virtual import VirtualConfig
from core.config.magic_words import *

__all__ = [
    'UIAdapter', 'LocalIPCConfig', 'UIConfig', 'VirtualConfig',
    'FileSystemType', 'LogConfig', 'LLMProvider', 'LLMConfig',
    'ProviderConfig', 'DBConfig', 'FSConfig', 'AgentConfig', 'Config',
    'ConfigLoader', 'get_config',
    
    # Agent Names
    'ARCHITECT_AGENT_NAME', 'SPEC_WRITER_AGENT_NAME', 'CODE_MONKEY_AGENT_NAME',
    'CODE_REVIEW_AGENT_NAME', 'DESCRIBE_FILES_AGENT_NAME', 'GET_RELEVANT_FILES_AGENT_NAME', 'REVIEWER_AGENT_NAME',
    'DEVELOPER_AGENT_NAME', 'TECH_LEAD_AGENT_NAME', 'TECH_LEAD_PLANNING', 'TECH_WRITER_AGENT_NAME',
    'PARSE_TASK_AGENT_NAME', 'TASK_BREAKDOWN_AGENT_NAME', 'PROBLEM_SOLVER_AGENT_NAME', 'BUG_HUNTER_AGENT_NAME', 'EXTERNAL_DOCS_AGENT_NAME',
    'ERROR_HANDLER_AGENT_NAME', 'TROUBLESHOOTER_AGENT_NAME', 'TROUBLESHOOTER_BUG_REPORT', 'TASK_COMPLETER_AGENT_NAME',
    'CHECK_LOGS_AGENT_NAME', 'LOG_ANALYZER_AGENT_NAME', 'DATABASE_AGENT_NAME',
    'SYNTAX_CHECK_AGENT_NAME', 'TESTING_AGENT_NAME', 'DEPLOYMENT_AGENT_NAME',
    'MONITORING_AGENT_NAME', 'SECURITY_AGENT_NAME', 'PERFORMANCE_AGENT_NAME',

    # Status and Actions
    'ADD_LOGS', 'PROBLEM_IDENTIFIED', 'TASK_COMPLETED', 'BUG_FIXED',
    'IN_PROGRESS', 'FAILED', 'SUCCESS',

    # Commands
    'RUN_TESTS', 'DEBUG', 'CHECK_LOGS', 'ANALYZE_CODE', 'EXTERNAL_DOCUMENTATION_API', 'TROUBLESHOOTER_GET_RUN_COMMAND',

    # Message Types
    'ERROR', 'WARNING', 'INFO', 'DEBUG',

    # File Types
    'PYTHON', 'JAVASCRIPT', 'TYPESCRIPT', 'HTML', 'CSS', 'JSON', 'YAML', 'MARKDOWN'
]


class FileSystemType(str, Enum):
    """
    Type of filesystem to use.
    """
    LOCAL = "local"
    VIRTUAL = "virtual"


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


class FSConfig(BaseModel):
    """Filesystem configuration"""
    type: FileSystemType = Field(FileSystemType.LOCAL, description="Filesystem type")
    workspace_root: str = Field("workspace", description="Root directory for workspace")
    ignore_paths: list[str] = Field(
        default=[
            ".git",
            ".gpt-pilot",
            ".idea",
            ".vscode",
            ".next",
            ".DS_Store",
            "__pycache__",
            "site-packages",
            "node_modules",
            "package-lock.json",
            "venv",
            "dist",
            "build",
            "target",
            "*.min.js",
            "*.min.css",
            "*.svg",
            "*.csv",
            "*.log",
            "go.sum"
        ],
        description="Paths to ignore when examining files",
    )
    ignore_size_threshold: int = Field(
        50000,
        description="Maximum size of files to examine (in bytes)",
        ge=0,
    )


class AgentConfig(BaseModel):
    """Agent configuration"""
    provider: LLMProvider = Field(LLMProvider.OPENAI, description="LLM provider to use")
    model: str = Field("gpt-4", description="Model to use")
    temperature: float = Field(0.7, description="Temperature to use for sampling")


class Config(BaseModel):
    """Main configuration."""
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
    agent: dict[str, AgentConfig] = Field(
        default={
            "default": AgentConfig(),
            "files": AgentConfig(model="gpt-3.5-turbo")
        }
    )
    log: LogConfig = Field(default_factory=LogConfig)
    db: DBConfig = Field(default_factory=DBConfig)
    ui: UIConfig = Field(description="UI configuration")
    fs: FSConfig = Field(default_factory=FSConfig)

    def all_llms(self) -> list[LLMConfig]:
        """Get all configured LLMs."""
        return [self.llm_for_provider(provider) for provider in self.llm.keys()]
    
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

    def llm_for_agent(self, agent_name: str) -> LLMConfig:
        """Get LLM configuration for an agent."""
        agent_config = self.agent.get(agent_name.lower())
        if not agent_config:
            agent_config = self.agent["default"]
            
        provider_config = self.llm.get(agent_config.provider)
        if not provider_config:
            raise ValueError(f"No configuration found for provider {agent_config.provider}")
            
        return LLMConfig(
            provider=agent_config.provider,
            model=agent_config.model,
            base_url=provider_config.base_url,
            api_key=provider_config.api_key,
            temperature=agent_config.temperature,
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
        self.config = Config(ui={"type": "plain"})

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