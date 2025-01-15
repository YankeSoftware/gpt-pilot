"""Logging configuration for gpt-pilot."""

import logging
from core.config import LogConfig

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