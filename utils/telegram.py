"""
Telegram Utility Functions for IpverseBot

This module contains various utility functions for Telegram operations including:
- Channel membership verification
- Spam protection
- Rate limiting
- Message editing and sending
- User input validation

Functions:
    check_channel_membership(bot, user_id): Verify user membership in required channels
    check_spam(bot, user_id, is_admin): Check if user is sending messages too frequently
    check_rate_limit(bot, user_id, is_admin): Check if user exceeds request rate limits
    sanitize_country_code(code): Validate and clean country code input
    edit_or_send_message(bot, chat_id, message_id, text, keyboard): Edit existing or send new message

Developed by Matrix Team
"""

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message
from config.settings import LANGUAGES, SPAM_THRESHOLD, RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD, ADMIN_ID
from utils.db import load_users, save_users, load_settings
from utils.logging import write_log
import time
import asyncio

async def check_channel_membership(bot: Bot, user_id: str) -> bool:
    """
    Check if user is a member of all required channels.
    
    Args:
        bot (Bot): The Telegram bot instance
        user_id (str): The user's Telegram ID as a string
        
    Returns:
        bool: True if user is member of all required channels, False otherwise
    """
    settings = load_settings()
    channels = settings.get("channels", [])
    write_log(f"Checking channel membership for user {user_id}: force_join={settings.get('force_join', True)}, channels={channels}")
    
    if not settings.get("force_join", True) or not channels:
        return True

    for channel in channels:
        try:
            chat_member = await bot.get_chat_member(channel, int(user_id))
            status = chat_member.status
            write_log(f"User {user_id} is a {status} of {channel}")
            if status in ["left", "kicked"]:
                return False
        except Exception as e:
            write_log(f"Error checking membership for user {user_id} in {channel}: {e}")
            return False
    write_log(f"Membership check passed for user {user_id}: joined all required channels")
    return True

async def check_spam(bot: Bot, user_id: str, is_admin: bool) -> bool:
    """
    Check if user is sending messages too frequently (spam protection).
    
    Args:
        bot (Bot): The Telegram bot instance
        user_id (str): The user's Telegram ID as a string
        is_admin (bool): Whether the user is an admin (admins bypass spam checks)
        
    Returns:
        bool: True if request is allowed, False if spam detected
    """
    if is_admin:
        return True
    users = load_users()
    user_data = users.get(user_id, {})
    current_time = time.time()
    recent_requests = user_data.get("recent_requests", [])
    recent_requests = [t for t in recent_requests if current_time - t < SPAM_THRESHOLD]
    recent_requests.append(current_time)
    users[user_id]["recent_requests"] = recent_requests[-10:]  # Keep last 10 requests
    save_users(users)
    if len(recent_requests) > 5:  # Max 5 requests in SPAM_THRESHOLD
        lang = user_data.get("lang", "en")
        await bot.send_message(user_id, LANGUAGES[lang]["spam_warning"])
        write_log(f"Spam detected for user {user_id}")
        return False
    return True

async def check_rate_limit(bot: Bot, user_id: str, is_admin: bool) -> bool:
    """Check if the user exceeds the rate limit."""
    if is_admin:
        return True
    users = load_users()
    user_data = users.get(user_id, {})
    current_time = time.time()
    last_message_time = user_data.get("last_message_time", 0)
    if current_time - last_message_time < RATE_LIMIT_PERIOD:
        request_count = user_data.get("request_count", 0) + 1
        if request_count > RATE_LIMIT_REQUESTS:
            lang = user_data.get("lang", "en")
            await bot.send_message(user_id, LANGUAGES[lang]["rate_limit_warning"])
            write_log(f"Rate limit exceeded for user {user_id}")
            return False
    else:
        request_count = 1
    users[user_id]["last_message_time"] = current_time
    users[user_id]["request_count"] = request_count
    save_users(users)
    return True

def sanitize_country_code(country: str) -> str:
    """Sanitize and validate a 2-letter country code."""
    country = country.strip().upper()
    if len(country) == 2 and country.isalpha():
        return country
    return ""

async def edit_or_send_message(bot: Bot, chat_id: int, message_id: int | None, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> Message:
    """Edit an existing message or send a new one if editing fails."""
    try:
        if message_id:
            try:
                return await bot.edit_message_text(
                    text=text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            except Exception as e:
                write_log(f"Failed to edit message {message_id} for chat {chat_id}: {e}")
        # If editing fails or message_id is None, send a new message
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        write_log(f"Failed to send/edit message for chat {chat_id}: {e}")
        # Fallback: send a new message without parse_mode to ensure delivery
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )

async def check_bot_admin(bot: Bot, channel: str) -> bool:
    """Check if the bot is an admin in the specified channel."""
    try:
        bot_id = (await bot.get_me()).id
        chat_member = await bot.get_chat_member(channel, bot_id)
        return chat_member.status in ["administrator", "creator"]
    except Exception as e:
        write_log(f"Error checking bot admin status in {channel}: {e}")
        return False