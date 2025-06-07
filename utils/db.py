"""
Database Utility Functions for IpverseBot

This module handles all database operations for the IpverseBot using JSON files
for persistent storage. It manages three main databases:
- users.json: User data, coins, referrals, and settings
- ip_files.json: IP file cache information and metadata
- settings.json: Bot configuration and channel settings

Functions:
    load_users(): Load user data from JSON file
    save_users(users): Save user data to JSON file
    load_ip_files(): Load IP files metadata from JSON file
    save_ip_files(ip_files): Save IP files metadata to JSON file
    load_settings(): Load bot settings from JSON file
    save_settings(settings): Save bot settings to JSON file
    initialize_data_dir(): Initialize data directories and create default files

Developed by Matrix Team
"""

import json
import os
from typing import Dict, Any
from config.settings import USERS_DB, IP_FILES_DB, SETTINGS_DB

def load_users() -> Dict[str, Any]:
    """
    Load users data from JSON file.
    
    Reads the users database file and returns the user data dictionary.
    Each user entry contains profile information, coin balance, referral data,
    and usage statistics.
    
    Returns:
        Dict[str, Any]: Dictionary containing all user data
        
    Raises:
        FileNotFoundError: If the users database file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(USERS_DB, "r") as f:
        return json.load(f)

def save_users(users: Dict[str, Any]) -> None:
    """
    Save users data to JSON file.
    
    Writes the user data dictionary to the users database file with proper
    JSON formatting and indentation for readability.
    
    Args:
        users (Dict[str, Any]): Dictionary containing all user data to save
        
    Raises:
        IOError: If unable to write to the database file
        TypeError: If the data contains non-serializable objects
    """
    with open(USERS_DB, "w") as f:
        json.dump(users, f, indent=2)

def load_ip_files() -> Dict[str, Any]:
    """Load IP files data from JSON file."""
    with open(IP_FILES_DB, "r") as f:
        return json.load(f)

def save_ip_files(ip_files: Dict[str, Any]) -> None:
    """Save IP files data to JSON file."""
    with open(IP_FILES_DB, "w") as f:
        json.dump(ip_files, f, indent=2)

def load_settings() -> Dict[str, Any]:
    """Load settings data from JSON file."""
    with open(SETTINGS_DB, "r") as f:
        return json.load(f)

def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings data to JSON file."""
    with open(SETTINGS_DB, "w") as f:
        json.dump(settings, f, indent=2)

def initialize_data_dir() -> None:
    """
    Initialize data directories and databases if they don't exist.
    
    This function sets up the bot's data structure by:
    1. Creating necessary directories for data storage
    2. Creating empty database files if they don't exist
    3. Setting up default configuration values
    
    The default settings include:
    - Empty users database
    - Empty IP files cache database  
    - Default settings with Matrix channel and force_join enabled
    
    This function should be called at bot startup to ensure proper initialization.
    """
    os.makedirs(os.path.dirname(USERS_DB), exist_ok=True)
    os.makedirs(os.path.dirname(IP_FILES_DB), exist_ok=True)
    os.makedirs(os.path.dirname(SETTINGS_DB), exist_ok=True)
    
    if not os.path.exists(USERS_DB):
        with open(USERS_DB, "w") as f:
            json.dump({}, f)
    if not os.path.exists(IP_FILES_DB):
        with open(IP_FILES_DB, "w") as f:
            json.dump({}, f)
    if not os.path.exists(SETTINGS_DB):
        with open(SETTINGS_DB, "w") as f:
            json.dump({"channels": ["@MatrixORG"], "force_join": True}, f)