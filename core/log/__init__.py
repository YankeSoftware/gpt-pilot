"""Logging configuration for gpt-pilot."""

import logging
from core.config import LogConfig

def setup(config: LogConfig) -> None:
    """Configure logging with the given settings."""
    root_logger = logging.getLogger()
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handler with configured format
    handler = logging.StreamHandler()
    formatter = logging.Formatter(config.format)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Set log level
    root_logger.setLevel(config.level)
    
    # If output file is specified, add file handler
    if config.output:
        file_handler = logging.FileHandler(config.output)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger configured with the current settings."""
    logger = logging.getLogger(name)
    
    # Only add handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    
    return logger