# utils/logger.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Advanced Logging System - Compatible with Railway
=============================================================================
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Try to import loguru, fallback to standard logging if not available
try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging as std_logger
    logger = std_logger.getLogger("AMORIA")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def setup_logging(module_name: str = "AMORIA"):
    """
    Setup logging system untuk AMORIA
    
    Args:
        module_name: Nama module untuk log
    
    Returns:
        Logger instance
    """
    from config import settings
    
    if LOGURU_AVAILABLE:
        # Use loguru for advanced logging
        loguru_logger.remove()  # Remove default handler
        
        # Console handler (INFO+)
        loguru_logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True,
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
        
        # File handler jika diperlukan
        try:
            log_dir = Path("data/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"{module_name}.log"
            loguru_logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level="DEBUG",
                rotation="50 MB",
                retention="30 days",
                compression="zip",
                enqueue=True
            )
            loguru_logger.info(f"📁 Log file: {log_file}")
        except Exception as e:
            loguru_logger.warning(f"Could not create log file: {e}")
        
        return loguru_logger
    
    else:
        # Fallback to standard logging
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            log_dir = Path("data/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"{module_name}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s')
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
            logger.info(f"📁 Log file: {log_file}")
        except Exception as e:
            logger.warning(f"Could not create log file: {e}")
        
        return logger


def get_logger(name: str = None):
    """
    Get logger instance
    
    Args:
        name: Nama logger (optional)
    
    Returns:
        Logger instance
    """
    if LOGURU_AVAILABLE:
        if name:
            return loguru_logger.bind(name=name)
        return loguru_logger
    else:
        return logging.getLogger(name or "AMORIA")


# Export logger instance
if LOGURU_AVAILABLE:
    logger = loguru_logger
else:
    logger = logging.getLogger("AMORIA")


__all__ = ['setup_logging', 'get_logger', 'logger']
