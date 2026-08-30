# Logging configuration for AdventureWorks Analytics Platform

"""
Centralized logging configuration.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = 'logs'

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging(name: str) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        f'{LOG_DIR}/adventureworks.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger
