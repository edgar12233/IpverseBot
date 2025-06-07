"""
IpverseBot - Telegram Bot for IP Range Information

This is the main entry point for the IpverseBot, a Telegram bot that provides
IP range information for different countries. The bot fetches ASN data from 
ipinfo.io and provides users with comprehensive IP range reports.

Features:
- Multi-language support (English and Persian/Farsi)
- User management with coin system
- Referral system for earning coins
- Admin panel for bot management
- Rate limiting and spam protection
- Automatic cache cleanup
- Channel membership verification

Developed by Matrix Team
"""

import asyncio
from aiogram import Bot, Dispatcher
from config.settings import API_TOKEN
from utils.db import initialize_data_dir
from utils.logging import write_log
from handlers.user import register_handlers as register_user_handlers
from handlers.admin import register_handlers as register_admin_handlers
from handlers.callback import register_handlers as register_callback_handlers
from datetime import datetime, timedelta
from utils.db import load_ip_files, save_ip_files
import os

async def cleanup_cache() -> None:
    """
    Daily cleanup task to remove old IP cache files.
    
    This function runs continuously in the background and performs daily cleanup
    of cached IP files that are older than one day. It helps maintain disk space
    and keeps the cache directory clean.
    
    The cleanup process:
    1. Calculate yesterday's date
    2. Load IP files database
    3. Remove files older than 1 day
    4. Update the database
    5. Sleep for 24 hours before next cleanup
    """
    while True:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        ip_files = load_ip_files()
        for country in ip_files:
            if yesterday in ip_files[country]:
                file_path = ip_files[country][yesterday]["file_path"]
                if os.path.exists(file_path):
                    os.remove(file_path)
                    write_log(f"Deleted old cache file {file_path}")
                del ip_files[country][yesterday]
        save_ip_files(ip_files)
        await asyncio.sleep(24 * 3600)

async def main() -> None:
    """
    Initialize and start the bot.
    
    This is the main entry point for the IpverseBot. It performs the following
    initialization steps:
    1. Create bot and dispatcher instances
    2. Initialize data directories and databases
    3. Register all message and callback handlers
    4. Start the background cache cleanup task
    5. Begin polling for updates from Telegram
    
    The function runs indefinitely until manually stopped or an error occurs.
    All bot operations are logged for monitoring and debugging purposes.
    
    Raises:
        ValueError: If required environment variables are missing
        aiogram.exceptions.TelegramUnauthorizedError: If bot token is invalid
        Exception: For any other startup errors
    """
    write_log("Bot started.")
    print(".\n.\n.\n.\n.\n.\n.\nBot Started!")
    
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    initialize_data_dir()
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_callback_handlers(dp)
    
    asyncio.create_task(cleanup_cache())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())