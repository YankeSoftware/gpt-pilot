"""Logging configuration for gpt-pilot."""

import logging
from core.config import LogConfig

def setup(config: LogConfig, force: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        config: Logging configuration
        force: Whether to force reconfiguration by removing existing handlers
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers if forced
    if force:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Set log level
    level = getattr(logging, config.level)
    root_logger.setLevel(level)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(config.format))
    root_logger.addHandler(console_handler)
    
    # Add file handler if output file specified
    if config.output:
        file_handler = logging.FileHandler(config.output)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(config.format))

        root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, inherit from root logger
    if not logger.handlers:
        root_logger = logging.getLogger()
        # Inherit level from root logger if not set
        if not logger.level:
            logger.setLevel(root_logger.level)
        # Add handlers from root logger
        for handler in root_logger.handlers:
            logger.addHandler(handler)
    
    return logger