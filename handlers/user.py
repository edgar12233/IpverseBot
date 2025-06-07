"""
User Message Handlers for IpverseBot

This module contains all user-facing message handlers for the IpverseBot.
It handles user commands, text messages, and interactions including:
- Welcome messages and language selection
- Channel membership verification
- IP range requests and processing
- User account management
- Referral system

Key Handlers:
    send_welcome(): Handle /start command and new user registration
    handle_message(): Process all text messages and country code requests
    register_handlers(): Register all user handlers with the dispatcher

Developed by Matrix Team
"""

from aiogram import Dispatcher, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import aiohttp
from config.settings import LANGUAGES, ADMIN_ID
from utils.db import load_users, save_users, load_settings
from utils.telegram import check_channel_membership, check_spam, check_rate_limit, sanitize_country_code, edit_or_send_message
from utils.ip_processing import process_country
from utils.logging import write_log

async def send_welcome(message: Message, bot: Bot) -> None:
    """
    Handle /start command and new user registration.
    
    Processes new user registration with referral tracking, language selection,
    channel membership verification, and welcome message generation.
    
    Args:
        message (Message): The incoming /start message
        bot (Bot): The Telegram bot instance
    """
    user_id = str(message.from_user.id)
    is_admin = user_id == ADMIN_ID
    users = load_users()
    settings = load_settings()

    write_log(f"Processing /start for user {user_id}, force_join={settings.get('force_join', True)}, referrer={message.text.split()[1] if message.text.startswith('/start ') and len(message.text.split()) > 1 else None}")

    if user_id not in users:
        ref = message.text.split()[1] if message.text.startswith("/start ") and len(message.text.split()) > 1 else None
        users[user_id] = {
            "lang": None,
            "coins": 0,
            "daily_requests": {"date": "", "count": 0},
            "referrer": ref,
            "referrals": 0,
            "last_message_id": None,
            "last_message_time": 0,
            "recent_requests": [],
            "processing": False,
            "referral_awarded": False
        }
        save_users(users)
        write_log(f"New user {user_id} registered with referrer {ref}")
        if not settings.get("force_join", True) and ref and ref in users and ref != user_id:
            try:
                users[ref]["coins"] = users[ref].get("coins", 0) + 1
                users[ref]["referrals"] = users[ref].get("referrals", 0) + 1
                users[user_id]["referral_awarded"] = True
                save_users(users)
                write_log(f"Awarded 1 coin to referrer {ref} for user {user_id} (force_join=False)")
                referrer_lang = users[ref].get("lang", "en")
                await bot.send_message(
                    ref,
                    LANGUAGES[referrer_lang]["referral_notification"].format(user_id, users[ref]["coins"])
                )
            except Exception as e:
                write_log(f"Failed to process referral for referrer {ref} (user {user_id}): {e}")

    if not await check_spam(bot, user_id, is_admin):
        write_log(f"User {user_id} blocked by spam check")
        return

    lang = users[user_id].get("lang", "en")

    if not users[user_id]["lang"]:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa")]
        ])
        msg = await message.answer(LANGUAGES["en"]["select_lang_prompt"], reply_markup=keyboard)
        users[user_id]["last_message_id"] = msg.message_id
        save_users(users)
        write_log(f"Prompted language selection for user {user_id}")
        return

    membership_passed = await check_channel_membership(bot, user_id)
    write_log(f"Membership check for user {user_id}: {'passed' if membership_passed else 'failed'}")

    if not membership_passed:
        channels = settings.get("channels", [])
        non_member_channels = []
        for channel in channels:
            chat_member = await bot.get_chat_member(channel, int(user_id))
            if chat_member.status in ["left", "kicked"]:
                non_member_channels.append(channel)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=channel, url=f"https://t.me/{channel[1:]}")] for channel in non_member_channels
        ] + [[InlineKeyboardButton(text=LANGUAGES[lang]["check_join"], callback_data="check_join")]])
        msg = await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                        LANGUAGES[lang]["no_access"], keyboard)
        users[user_id]["last_message_id"] = msg.message_id
        save_users(users)
        write_log(f"Sent membership prompt to user {user_id}")
        return

    ref = users[user_id].get("referrer")
    write_log(f"Checking referral in send_welcome for user {user_id}: referrer={ref}, referral_awarded={users[user_id].get('referral_awarded', False)}, force_join={settings.get('force_join', True)}")
    if settings.get("force_join", True) and ref and ref in users and ref != user_id and not users[user_id].get("referral_awarded", False):
        try:
            users[ref]["coins"] = users[ref].get("coins", 0) + 1
            users[ref]["referrals"] = users[ref].get("referrals", 0) + 1
            users[user_id]["referral_awarded"] = True
            save_users(users)
            write_log(f"Awarded 1 coin to referrer {ref} for user {user_id} in send_welcome (force_join=True)")
            referrer_lang = users[ref].get("lang", "en")
            await bot.send_message(
                ref,
                LANGUAGES[referrer_lang]["referral_notification"].format(user_id, users[ref]["coins"])
            )
        except Exception as e:
            write_log(f"Failed to process referral in send_welcome for referrer {ref} (user {user_id}): {e}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LANGUAGES[lang]["update_ip"], callback_data="update_ip"),
            InlineKeyboardButton(text=LANGUAGES[lang]["account"], callback_data="account")
        ],
        [
            InlineKeyboardButton(text=LANGUAGES[lang]["referral"], callback_data="referral"),
            InlineKeyboardButton(text=LANGUAGES[lang]["select_lang"], callback_data="select_lang")
        ]
    ])
    if is_admin:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=LANGUAGES[lang]["admin_panel"], callback_data="admin_panel")])
    msg = await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                    LANGUAGES[lang]["welcome"], keyboard)
    users[user_id]["last_message_id"] = msg.message_id
    save_users(users)
    write_log(f"Sent welcome message to user {user_id}")

async def handle_country(message: Message, bot: Bot) -> None:
    """Handle 2-letter country code input."""
    user_id = str(message.from_user.id)
    is_admin = user_id == ADMIN_ID
    write_log(f"Handling country code {message.text} for user {user_id}, message_id {message.message_id}")

    if not await check_spam(bot, user_id, is_admin) or not await check_rate_limit(bot, user_id, is_admin):
        return

    users = load_users()
    if users[user_id].get("processing", False):
        return

    if not await check_channel_membership(bot, user_id):
        settings = load_settings()
        lang = users.get(user_id, {}).get("lang", "en")
        channels = settings.get("channels", [])
        non_member_channels = []
        for channel in channels:
            chat_member = await bot.get_chat_member(channel, int(user_id))
            if chat_member.status in ["left", "kicked"]:
                non_member_channels.append(channel)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=channel, url=f"https://t.me/{channel[1:]}")] for channel in non_member_channels
        ] + [[InlineKeyboardButton(text=LANGUAGES[lang]["check_join"], callback_data="check_join")]])
        await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["no_access"], keyboard)
        users[user_id]["last_message_id"] = message.message_id
        save_users(users)
        return

    lang = users.get(user_id, {}).get("lang", "en")
    country = sanitize_country_code(message.text)
    if not country:
        await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["invalid_country"])
        users[user_id]["last_message_id"] = message.message_id
        save_users(users)
        return

    today = datetime.now().strftime("%Y-%m-%d")
    if users[user_id]["daily_requests"]["date"] != today:
        users[user_id]["daily_requests"] = {"date": today, "count": 0}
    if users[user_id]["daily_requests"]["count"] >= 5:
        if users[user_id]["coins"] < 1:
            await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                      LANGUAGES[lang]["no_coins"])
            users[user_id]["last_message_id"] = message.message_id
            save_users(users)
            return
        users[user_id]["coins"] -= 1
        users[user_id]["coins_spent"] = users[user_id].get("coins_spent", 0) + 1
    users[user_id]["daily_requests"]["count"] += 1
    users[user_id]["processing"] = True
    save_users(users)

    async with aiohttp.ClientSession() as session:
        try:
            result = await process_country(bot, message, session, country, user_id, lang)
            if not result:
                # Error message already sent by process_country
                pass
        except Exception as e:
            write_log(f"Error processing country for user {user_id}: {e}")
            await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                      LANGUAGES[lang]["invalid_country"])
            users[user_id]["last_message_id"] = message.message_id
        finally:
            users[user_id]["processing"] = False
            save_users(users)

def register_handlers(dp: Dispatcher) -> None:
    """Register user-related handlers."""
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(handle_country, F.text.len() == 2)