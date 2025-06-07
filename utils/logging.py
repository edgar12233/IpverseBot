"""
Logging Utility for IpverseBot

This module provides logging functionality for the IpverseBot. It handles
writing log messages to a file with timestamps for debugging and monitoring
purposes.

Functions:
    write_log(message: str) -> None: Write a timestamped log message to file

Developed by Matrix Team
"""

from datetime import datetime
from config.settings import LOG_FILE, LOG_ENABLED

def write_log(message: str) -> None:
    """
    Write a timestamped log message to file if logging is enabled.
    
    Args:
        message (str): The log message to write
    """
    if LOG_ENABLED:
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now()} - {message}\n")