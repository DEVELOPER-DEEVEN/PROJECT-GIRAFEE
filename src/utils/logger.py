"""
Logging configuration for the Windows AI Assistant
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logging():
    """Setup logging configuration"""
    # Remove default handler
    logger.remove()
    
    # Get log directory
    log_dir = Path.home() / ".windows_ai_assistant" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File handler for all logs
    logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # File handler for errors only
    logger.add(
        log_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="90 days",
        compression="zip"
    )
    
    logger.info("Logging system initialized")


def get_logger(name: str = None):
    """Get a logger instance"""
    return logger.bind(name=name) if name else logger 