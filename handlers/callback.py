"""
Callback Query Handlers for IpverseBot

This module handles all callback queries (inline button presses) for the IpverseBot.
It manages user interactions with inline keyboards including:
- Channel membership verification
- Language selection
- Account information display
- Referral link generation
- Admin panel navigation

Key Functions:
    check_join(): Verify user membership in required channels
    select_language(): Handle language selection callbacks
    show_account(): Display user account information
    show_referral(): Show referral link and information
    register_handlers(): Register all callback handlers

Developed by Matrix Team
"""

from aiogram import Dispatcher, Bot, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import LANGUAGES, ADMIN_ID
from utils.db import load_users, save_users, load_ip_files, save_settings, load_settings
from utils.telegram import check_channel_membership, check_bot_admin, edit_or_send_message
from utils.logging import write_log
from handlers.admin import admin_panel, manage_channels, add_channel_prompt_callback, remove_channel_prompt
from datetime import datetime

async def check_join(callback: CallbackQuery, bot: Bot) -> None:
    """
    Handle check_join callback to verify channel membership.
    
    This function verifies if a user has joined all required channels
    and processes referral rewards if applicable. It's called when users
    click the "Check Membership" button.
    
    Process:
    1. Check membership status in all required channels
    2. Award referral coins if user came from referral and joins successfully
    3. Display appropriate welcome message or membership error
    4. Update user database with membership status
    
    Args:
        callback (CallbackQuery): The callback query from check membership button
        bot (Bot): The Telegram bot instance
    """
    user_id = str(callback.from_user.id)
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    settings = load_settings()

    write_log(f"Processing check_join for user {user_id}, force_join={settings.get('force_join', True)}, channels={settings.get('channels', [])}")

    # Check which channels the user is not a member of
    channels = settings.get("channels", [])
    non_member_channels = []
    membership_passed = True
    for channel in channels:
        chat_member = await bot.get_chat_member(channel, int(user_id))
        if chat_member.status in ["left", "kicked"]:
            non_member_channels.append(channel)
            membership_passed = False
        write_log(f"User {user_id} membership in {channel}: {chat_member.status}")

    if membership_passed:
        ref = users[user_id].get("referrer")
        write_log(f"Checking referral for user {user_id}: referrer={ref}, referral_awarded={users[user_id].get('referral_awarded', False)}")
        if ref and ref in users and ref != user_id and not users[user_id].get("referral_awarded", False):
            if settings.get("force_join", True):
                try:
                    users[ref]["coins"] = users[ref].get("coins", 0) + 1
                    users[ref]["referrals"] = users[ref].get("referrals", 0) + 1
                    users[user_id]["referral_awarded"] = True
                    save_users(users)
                    write_log(f"Awarded 1 coin to referrer {ref} for user {user_id} (force_join=True)")
                    referrer_lang = users[ref].get("lang", "en")
                    await bot.send_message(
                        ref,
                        LANGUAGES[referrer_lang]["referral_notification"].format(user_id, users[ref]["coins"])
                    )
                except Exception as e:
                    write_log(f"Failed to process referral for referrer {ref} (user {user_id}): {e}")

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
        if user_id == ADMIN_ID:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text=LANGUAGES[lang]["admin_panel"], callback_data="admin_panel")])
        await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["welcome"], keyboard)
        users[user_id]["last_message_id"] = callback.message.message_id
        save_users(users)
        await callback.answer()
    else:
        await callback.answer(LANGUAGES[lang]["not_joined_alert"], show_alert=True)

async def select_language(callback: CallbackQuery, bot: Bot) -> None:
    """Show language selection menu."""
    user_id = str(callback.from_user.id)
    users = load_users()
    if users[user_id].get("processing", False):
        await callback.answer()
        return
    lang = users.get(user_id, {}).get("lang", "en")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa")],
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["select_lang"], keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def change_language(callback: CallbackQuery, bot: Bot) -> None:
    """Handle language change."""
    user_id = str(callback.from_user.id)
    users = load_users()
    if users[user_id].get("processing", False):
        await callback.answer()
        return
    lang = callback.data.split("_")[1]
    users[user_id]["lang"] = lang
    save_users(users)
    write_log(f"User {user_id} changed language to {lang}")

    settings = load_settings()
    membership_passed = await check_channel_membership(bot, user_id)
    write_log(f"Membership check in change_language for user {user_id}: {'passed' if membership_passed else 'failed'}")

    if membership_passed:
        ref = users[user_id].get("referrer")
        write_log(f"Checking referral in change_language for user {user_id}: referrer={ref}, referral_awarded={users[user_id].get('referral_awarded', False)}, force_join={settings.get('force_join', True)}")
        if settings.get("force_join", True) and ref and ref in users and ref != user_id and not users[user_id].get("referral_awarded", False):
            try:
                users[ref]["coins"] = users[ref].get("coins", 0) + 1
                users[ref]["referrals"] = users[ref].get("referrals", 0) + 1
                users[user_id]["referral_awarded"] = True
                save_users(users)
                write_log(f"Awarded 1 coin to referrer {ref} for user {user_id} in change_language (force_join=True)")
                referrer_lang = users[ref].get("lang", "en")
                await bot.send_message(
                    ref,
                    LANGUAGES[referrer_lang]["referral_notification"].format(user_id, users[ref]["coins"])
                )
            except Exception as e:
                write_log(f"Failed to process referral in change_language for referrer {ref} (user {user_id}): {e}")

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
        if user_id == ADMIN_ID:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text=LANGUAGES[lang]["admin_panel"], callback_data="admin_panel")])
        await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["welcome"], keyboard)
        users[user_id]["last_message_id"] = callback.message.message_id
    else:
        channels = settings.get("channels", [])
        non_member_channels = []
        for channel in channels:
            chat_member = await bot.get_chat_member(channel, int(user_id))
            if chat_member.status in ["left", "kicked"]:
                non_member_channels.append(channel)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=channel, url=f"https://t.me/{channel[1:]}")] for channel in non_member_channels
        ] + [[InlineKeyboardButton(text=LANGUAGES[lang]["check_join"], callback_data="check_join")]])
        await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["no_access"], keyboard)
        users[user_id]["last_message_id"] = callback.message.message_id

    save_users(users)
    await callback.answer(LANGUAGES[lang]["lang_changed"])

async def show_account(callback: CallbackQuery, bot: Bot) -> None:
    """Show user account details."""
    user_id = str(callback.from_user.id)
    users = load_users()
    if users[user_id].get("processing", False):
        await callback.answer()
        return
    lang = users.get(user_id, {}).get("lang", "en")
    coins = users[user_id].get("coins", 0)
    today = datetime.now().strftime("%Y-%m-%d")
    daily_requests = users[user_id].get("daily_requests", {"date": today, "count": 0})
    if daily_requests["date"] != today:
        daily_requests = {"date": today, "count": 0}
        users[user_id]["daily_requests"] = daily_requests
        save_users(users)
    remaining_requests = max(0, 5 - daily_requests["count"])
    used_requests = daily_requests["count"]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["account_info"].format(coins, remaining_requests, used_requests), keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def show_referral(callback: CallbackQuery, bot: Bot) -> None:
    """Show referral information."""
    user_id = str(callback.from_user.id)
    users = load_users()
    if users[user_id].get("processing", False):
        await callback.answer()
        return
    lang = users.get(user_id, {}).get("lang", "en")
    bot_username = (await bot.get_me()).username
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["referral_info"].format(f"https://t.me/{bot_username}?start={user_id}"), keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def remove_channel(callback: CallbackQuery, bot: Bot) -> None:
    """Remove a channel from the required list."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.answer("❌ Access denied!")
        return
    channel = callback.data.replace("remove_channel_", "")
    settings = load_settings()
    if channel in settings.get("channels", []):
        settings["channels"].remove(channel)
        save_settings(settings)
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["channel_removed"].format(channel), keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def toggle_force_join(callback: CallbackQuery, bot: Bot) -> None:
    """Toggle the force join requirement."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.answer("❌ Access denied!")
        return
    settings = load_settings()
    settings["force_join"] = not settings.get("force_join", True)
    save_settings(settings)
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    status = "On" if settings["force_join"] else "Off"
    status_fa = "فعال" if settings["force_join"] else "غیرفعال"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_admin")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["force_join_toggled"].format(status if lang == "en" else status_fa), keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def broadcast_prompt(callback: CallbackQuery, bot: Bot) -> None:
    """Prompt for broadcast message."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.answer("❌ Access denied!")
        return
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    users[user_id]["awaiting_broadcast"] = True
    save_users(users)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_admin")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["broadcast_prompt"], keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def back_to_main(callback: CallbackQuery, bot: Bot) -> None:
    """Return to the main menu."""
    user_id = str(callback.from_user.id)
    users = load_users()
    if users[user_id].get("processing", False):
        await callback.answer()
        return
    lang = users.get(user_id, {}).get("lang", "en")
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
    if user_id == ADMIN_ID:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=LANGUAGES[lang]["admin_panel"], callback_data="admin_panel")])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["welcome"], keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def back_to_admin(callback: CallbackQuery, bot: Bot) -> None:
    """Return to the admin panel."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.answer("❌ Access denied!")
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

async def update_request(callback: CallbackQuery, bot: Bot) -> None:
    """Prompt for IP range update."""
    user_id = str(callback.from_user.id)
    users = load_users()
    if users[user_id].get("processing", False):
        await callback.answer()
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
        await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["no_access"], keyboard)
        users[user_id]["last_message_id"] = callback.message.message_id
        save_users(users)
        await callback.answer()
        return
    lang = users.get(user_id, {}).get("lang", "en")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
    ])
    await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                              LANGUAGES[lang]["update_ip_prompt"], keyboard)
    users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

async def check_admin_again(callback: CallbackQuery, bot: Bot) -> None:
    """Check if bot is admin in a channel again."""
    user_id = str(callback.from_user.id)
    if user_id != ADMIN_ID:
        await callback.answer("❌ Access denied!")
        return
    channel = callback.data.replace("check_channel_", "")
    users = load_users()
    lang = users.get(user_id, {}).get("lang", "en")
    if await check_bot_admin(bot, channel):
        settings = load_settings()
        if channel not in settings.get("channels", []):
            settings["channels"].append(channel)
            save_settings(settings)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
        ])
        await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["channel_added"].format(channel), keyboard)
        users[user_id]["last_message_id"] = callback.message.message_id
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["check_again"], callback_data=f"check_channel_{channel}")],
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="manage_channels")]
        ])
        await edit_or_send_message(bot, callback.message.chat.id, users[user_id]["last_message_id"],
                                  LANGUAGES[lang]["not_admin"].format(channel), keyboard)
        users[user_id]["last_message_id"] = callback.message.message_id
    save_users(users)
    await callback.answer()

def register_handlers(dp: Dispatcher) -> None:
    """Register callback query handlers."""
    dp.callback_query.register(check_join, F.data == "check_join")
    dp.callback_query.register(select_language, F.data == "select_lang")
    dp.callback_query.register(change_language, F.data.startswith("lang_"))
    dp.callback_query.register(show_account, F.data == "account")
    dp.callback_query.register(show_referral, F.data == "referral")
    dp.callback_query.register(remove_channel, F.data.startswith("remove_channel_"))
    dp.callback_query.register(toggle_force_join, F.data == "toggle_force_join")
    dp.callback_query.register(broadcast_prompt, F.data == "broadcast")
    dp.callback_query.register(back_to_main, F.data == "back_main")
    dp.callback_query.register(back_to_admin, F.data == "back_admin")
    dp.callback_query.register(update_request, F.data == "update_ip")
    dp.callback_query.register(check_admin_again, F.data.startswith("check_channel_"))
    dp.callback_query.register(admin_panel, F.data == "admin_panel")
    dp.callback_query.register(manage_channels, F.data == "manage_channels")
    dp.callback_query.register(add_channel_prompt_callback, F.data == "add_channel")
    dp.callback_query.register(remove_channel_prompt, F.data == "remove_channel_prompt")