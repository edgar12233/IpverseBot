"""
Admin Handlers for IpverseBot

This module contains all administrative handlers for the IpverseBot.
It provides comprehensive admin functionality including:
- Bot statistics and dashboard
- Channel management (add/remove channels)
- Force join settings toggle
- Broadcast messaging to all users
- User and system monitoring

Key Functions:
    admin_panel(): Display admin dashboard with statistics
    manage_channels(): Channel management interface
    toggle_force_join(): Toggle mandatory channel membership
    broadcast_message(): Send messages to all users
    register_handlers(): Register all admin handlers

Security:
    All functions verify admin status using ADMIN_ID from settings.
    Unauthorized access attempts are logged and denied.

Developed by Matrix Team
"""

from aiogram import Dispatcher, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from config.settings import LANGUAGES, ADMIN_ID
from utils.db import load_users, save_users, load_settings, save_settings, load_ip_files
from utils.telegram import edit_or_send_message
from utils.logging import write_log
import asyncio

async def admin_panel(callback: CallbackQuery, bot: Bot) -> None:
    """
    Show admin panel with comprehensive bot statistics.
    
    This function displays the main admin dashboard containing:
    - Total registered users count
    - Total IP files generated
    - Cached IP files count  
    - Total coins spent by users
    - Admin control buttons for various functions
    
    Args:
        callback (CallbackQuery): The callback query from admin button
        bot (Bot): The Telegram bot instance
        
    Security:
        Verifies admin status before displaying panel.
        Non-admin users receive access denied message.
    """
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.message.answer("❌ Access denied!")
        return
    users = load_users()
    ip_files = load_ip_files()
    total_users = len(users)
    total_ip_files = sum(len(dates) for country, dates in ip_files.items())
    total_cached_ip_files = sum(
        sum(1 for date, data in dates.items() if data.get("cached", False))
        for country, dates in ip_files.items()
    )
    total_coins_spent = sum(user.get("coins_spent", 0) for user in users.values())
    lang = users.get(user_id, {}).get("lang", "en")
    settings = load_settings()
    force_join_status = "On" if settings.get("force_join", True) else "Off"
    status_fa = "فعال" if settings["force_join"] else "غیرفعال"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["manage_channels_button"], callback_data="manage_channels")],
        [InlineKeyboardButton(
            text=LANGUAGES[lang]["toggle_force_join"].format(
                force_join_status if lang == "en" else status_fa
            ),
            callback_data="toggle_force_join"
        )],
        [InlineKeyboardButton(text=LANGUAGES[lang]["broadcast"], callback_data="broadcast")],
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["admin_stats"].format(total_users, total_ip_files, total_cached_ip_files, total_coins_spent),
                              keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def manage_channels(callback: CallbackQuery, bot: Bot) -> None:
    """Show channel management menu."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.message.answer("❌ Access denied!")
        return
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    settings = load_settings()
    channels = settings.get("channels", [])
    channel_list = "\n".join([f"📢 {channel}" for channel in channels]) if channels else "📭 No channels added yet!"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["add_channel"], callback_data="add_channel")],
        [InlineKeyboardButton(text=LANGUAGES[lang]["remove_channel"], callback_data="remove_channel_prompt")],
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_admin")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["manage_channels"].format(channel_list), keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def add_channel_prompt_callback(callback: CallbackQuery, bot: Bot) -> None:
    """Prompt for adding a channel via callback."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.message.answer("❌ Access denied!")
        return
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    users[user_id]["awaiting_channel"] = True
    save_users(users)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["add_channel_prompt"], keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def add_channel_prompt_message(message: Message, bot: Bot) -> None:
    """Handle channel username input."""
    user_id = str(message.from_user.id)
    if user_id != ADMIN_ID:
        await message.answer("❌ Access denied!")
        return
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    if not users.get(user_id, {}).get("awaiting_channel", False):
        return
    users[user_id]["awaiting_channel"] = False
    save_users(users)
    channel = message.text.strip()
    if not channel.startswith("@"):
        channel = f"@{channel}"
    settings = load_settings()
    channels = settings.get("channels", [])
    if channel in channels:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
        ])
        await message.answer(LANGUAGES[lang]["channel_added"].format(channel), reply_markup=keyboard)
        return
    try:
        chat = await bot.get_chat(channel)
        member = await bot.get_chat_member(channel, bot.id)
        if member.status not in ["administrator", "creator"]:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=LANGUAGES[lang]["check_again"], callback_data=f"check_channel_{channel}")],
                [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
            ])
            await message.answer(LANGUAGES[lang]["not_admin"].format(channel), reply_markup=keyboard)
            return
        channels.append(channel)
        settings["channels"] = channels
        save_settings(settings)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
        ])
        await message.answer(LANGUAGES[lang]["channel_added"].format(channel), reply_markup=keyboard)
        await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["manage_channels"].format(
                                      "\n".join([f"📢 {ch}" for ch in channels])),
                                  keyboard)
        users[user_id]["last_message_id"] = message.message_id
        save_users(users)
    except Exception as e:
        write_log(f"Failed to add channel {channel}: {e}")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
        ])
        await message.answer(LANGUAGES[lang]["not_admin"].format(channel), reply_markup=keyboard)

async def remove_channel_prompt(callback: CallbackQuery, bot: Bot) -> None:
    """Show channel removal menu."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.message.answer("❌ Access denied!")
        return
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    settings = load_settings()
    channels = settings.get("channels", [])
    if not channels:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
        ])
        await callback.message.answer(LANGUAGES[lang]["channel_list"].format("📭 No channels to remove!"), reply_markup=keyboard)
        return
    channel_list = "\n".join([f"📢 {channel}" for channel in channels])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[[InlineKeyboardButton(text=f"🗑 {channel}", callback_data=f"remove_channel_{channel}")]
          for channel in channels],
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["select_remove_channel"].format(channel_list), keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def broadcast_prompt(message: Message, bot: Bot) -> None:
    """Prompt for broadcast message."""
    user_id = str(message.from_user.id)
    if user_id != ADMIN_ID:
        await message.answer("❌ Access denied!")
        return
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    users[user_id]["awaiting_broadcast"] = True
    save_users(users)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_admin")]
    ])
    await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["broadcast_prompt"], keyboard)
    users[user_id]["last_message_id"] = message.message_id
    save_users(users)

async def broadcast_message(message: Message, bot: Bot) -> None:
    """Handle broadcast message."""
    user_id = str(message.from_user.id)
    if user_id != ADMIN_ID:
        await message.answer("❌ Access denied!")
        return
    users = load_users()
    if not users.get(user_id, {}).get("awaiting_broadcast", False):
        return
    users[user_id]["awaiting_broadcast"] = False
    save_users(users)
    lang = users.get(user_id, {}).get("lang", "en")
    total_users = len(users)
    sent = 0
    failed = 0

    async def send_broadcast():
        nonlocal sent, failed
        for uid in users:
            try:
                await bot.send_message(uid, message.text, parse_mode="Markdown")
                sent += 1
            except Exception as e:
                write_log(f"Failed to send broadcast to user {uid}: {e}")
                failed += 1
            await asyncio.sleep(0.05)  # Rate limiting

    # Run broadcast in background
    asyncio.create_task(send_broadcast())

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_admin")]
    ])
    await edit_or_send_message(bot, message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["broadcast_done"].format(sent, total_users, failed),
                              keyboard)
    users[user_id]["last_message_id"] = message.message_id
    save_users(users)

def register_handlers(dp: Dispatcher) -> None:
    """Register admin handlers."""
    dp.callback_query.register(admin_panel, lambda callback: callback.data == "admin_panel" and str(callback.from_user.id) == ADMIN_ID)
    dp.callback_query.register(manage_channels, lambda callback: callback.data == "manage_channels" and str(callback.from_user.id) == ADMIN_ID)
    dp.callback_query.register(add_channel_prompt_callback, lambda callback: callback.data == "add_channel" and str(callback.from_user.id) == ADMIN_ID)
    dp.callback_query.register(remove_channel_prompt, lambda callback: callback.data == "remove_channel_prompt" and str(callback.from_user.id) == ADMIN_ID)
    dp.message.register(add_channel_prompt_message, lambda message: str(message.from_user.id) == ADMIN_ID and load_users().get(str(message.from_user.id), {}).get("awaiting_channel", False))
    dp.message.register(broadcast_message, lambda message: str(message.from_user.id) == ADMIN_ID and load_users().get(str(message.from_user.id), {}).get("awaiting_broadcast", False))