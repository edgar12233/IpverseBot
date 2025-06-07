"""
Configuration Settings for IpverseBot

This module contains all configuration settings, constants, and localized
text strings for the IpverseBot. It handles:
- Environment variable loading and validation
- Bot operational parameters
- Multi-language text strings (English and Persian)
- File paths and directories
- Rate limiting and spam protection settings

Key Configurations:
- API_TOKEN: Telegram bot token from BotFather
- ADMIN_ID: Telegram user ID of the bot administrator
- Language dictionaries with all user-facing text
- Database file paths and cache directories
- Performance and security parameters

Developed by Matrix Team
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
API_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: str = os.getenv("ADMIN_ID", "")
LOG_FILE: str = "log.txt"
LOG_ENABLED: bool = False
DATA_DIR: str = "data"
IP_CACHE_DIR: str = os.path.join(DATA_DIR, "ip_cache")
USERS_DB: str = os.path.join(DATA_DIR, "users.json")
IP_FILES_DB: str = os.path.join(DATA_DIR, "ip_files.json")
SETTINGS_DB: str = os.path.join(DATA_DIR, "settings.json")
SPAM_THRESHOLD: int = 2  # Seconds between non-admin commands
RATE_LIMIT_REQUESTS: int = 10  # Max IP requests per minute per user
RATE_LIMIT_PERIOD: int = 60  # Seconds for request limit window

# Validate required environment variables
if not API_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID environment variable is required")

# Language dictionary
LANGUAGES = {
    "en": {
        "select_lang_prompt": "🌐 Welcome to Ipverse Bot! 🌐\nPlease select your language to continue:",
        "welcome_new": "🌟 Welcome to Ipverse Bot! 🌟\nTo get started, please join our official channels below.\nOnce joined, press Check Membership to unlock the bot's features!",
        "check_join": "✅ Check Membership",
        "no_access": "❌ You must join the required channels to access Ipverse Bot:\n\nJoin and press Check Membership to proceed.",
        "not_joined_alert": "❌ You haven't joined all required channels yet!",
        "welcome": "🎉 Welcome to Ipverse Bot! 🎉\nExplore the features below to get IP ranges, check your account, or invite friends to earn coins!\n\n🔹 Enter a 2-letter country code (e.g., US, IR) to fetch IP ranges.\n🔹 You have 5 free requests daily; additional requests cost 1 coin.\n🔹 Invite friends to earn coins!",
        "select_lang": "🌐 Change Language",
        "lang_changed": "✅ Language switched to English! You're ready to explore Ipverse Bot's features.",
        "invalid_country": "❌ Invalid country code! Please enter a valid 2-letter code (e.g., US, IR) to proceed.",
        "processing": "⏳ Fetching IP ranges for {}... Please wait.\n📄 Pages processed: {}\n🔢 Total ASNs: {}\n🌐 Total IP Ranges: {}\n⏱ Elapsed time: {:.1f} seconds",
        "processing_complete": "✅ Processing complete for {}!",
        "done": "✅ IP Range Report for {}\n📅 Generated on: {}\n\n📄 Pages processed: {}\n🔢 Total ASNs: {}\n🌐 Total IP Ranges: {}\n⏱ Time taken: {:.1f} seconds\n\n💾 File ready for download!",
        "update_ip": "🔄 Fetch IP Range",
        "update_ip_prompt": "🌍 Please enter a 2-letter country code (e.g., US, IR) to fetch the IP range:",
        "account": "👤 User Account",
        "referral": "📎 Invite Friends",
        "no_coins": "❌ You need 1 coin to fetch more IP ranges!\n📎 Invite friends to earn coins or check your account.",
        "daily_limit": "⛔ You've reached your daily limit of 5 free IP range requests.\n💰 Use 1 coin for additional requests or invite friends to earn more!",
        "referral_info": "📎 Your Referral Link: {}\n\n🎁 Invite friends to Ipverse Bot and earn 1 coin for each new user who joins using your link!\n💡 Share this link to grow your coin balance and unlock more IP range requests.",
        "referral_notification": "🎉 New user with ID {} joined via your referral link!\n💰 You earned 1 coin. Your balance: {} coins.",
        "account_info": "👤 Your Account Details:\n💰 Coin Balance: {} coins\n📊 Daily Free Requests Remaining: {}\n🔄 Daily Requests Used: {}\n\n🔹 You get 5 free IP range requests daily.\n🔹 Additional requests cost 1 coin each.\n🔹 Invite friends to earn more coins!",
        "admin_panel": "🛠 Admin Control Panel",
        "admin_stats": "📈 Ipverse Bot Dashboard\n👥 Total Users: {}\n📄 Total IP Files Generated: {}\n🔄 Total Cached IP Files: {}\n💰 Total Coins Spent: {}\n\n🔧 Select an option below to manage Ipverse Bot:",
        "manage_channels": "📢 Channel Management\n\nCurrent Channels:\n{}\n\n🔧 Choose an action to manage your channels:",
        "manage_channels_button": "Manage Channels",
        "toggle_force_join": "🔒 Toggle Force Join ({})",
        "broadcast": "📣 Broadcast Message",
        "add_channel": "➕ Add New Channel",
        "add_channel_prompt": "📢 Enter the channel username (e.g., @ChannelName) to add it to the bot:",
        "remove_channel": "🗑 Remove Channel",
        "back": "⬅ Back",
        "channel_list": "📋 Current Channels:\n{}\n\n🔧 Select an action:",
        "enter_channel": "📢 Please enter the channel username (e.g., @ChannelName) to add:",
        "not_admin": "⚠ Ipverse Bot is not an admin in {}. Please make the bot an admin and press Check Again.",
        "check_again": "🔄 Check Again",
        "select_remove_channel": "🗑 Select a Channel to Remove:\n\n{}\n\nChoose a channel to remove it from the bot:",
        "channel_added": "🎉 Channel {} added successfully! It's now part of Ipverse Bot.",
        "channel_removed": "✅ Channel {} removed successfully! It's no longer required.",
        "force_join_toggled": "🔄 Force join requirement set to {}!",
        "broadcast_prompt": "📣 Please send the message (text, photo, video, etc.) to broadcast to all users:",
        "broadcast_progress": "📣 Broadcast in progress:\n👥 Sent: {}/{} users\n⏱ Estimated time remaining: {:.1f} seconds",
        "broadcast_done": "✅ Broadcast completed: {}/{} sent, {} failed",
        "spam_warning": "⚠ Slow down! You're sending messages too fast. Please wait {} seconds before trying again.",
        "rate_limit_warning": "⛔ You've exceeded the request limit of {} requests per minute. Please try again in {} seconds.",
        "file_locked": "⏳ The IP list for {} is being generated. Please try again in a few minutes or request another country's file."
    },
    "fa": {
        "select_lang_prompt": "🌐 به ربات Ipverse خوش آمدید! 🌐\nلطفاً زبان خود را برای ادامه انتخاب کنید:",
        "welcome_new": "🌟 به ربات Ipverse خوش آمدید! 🌟\nبرای شروع، لطفاً در کانال‌های رسمی زیر عضو شوید.\nپس از عضویت، روی بررسی عضویت کلیک کنید تا قابلیت‌های ربات فعال شود!",
        "check_join": "✅ بررسی عضویت",
        "no_access": "❌ برای دسترسی به ربات Ipverse باید در کانال‌های مورد نیاز زیر عضو شوید:\n\nعضو شوید و روی بررسی عضویت کلیک کنید تا ادامه دهید.",
        "not_joined_alert": "❌ هنوز عضو تمام کانال‌ها نشده‌اید!",
        "welcome": "🎉 به ربات Ipverse خوش آمدید! 🎉\nویژگی‌های زیر را کاوش کنید تا محدوده‌های آی‌پی را دریافت کنید، حساب کاربری خود را بررسی کنید یا دوستانتان را دعوت کنید تا سکه به دست آورید!\n\n🔹 یک کد ۲ حرفی کشور (مثل US، IR) وارد کنید تا محدوده‌های آی‌پی دریافت شود.\n🔹 روزانه ۵ درخواست رایگان دارید؛ درخواست‌های اضافی ۱ سکه هزینه دارند.\n🔹 دوستان خود را دعوت کنید تا سکه به دست آورید!",
        "select_lang": "🌐 تغییر زبان",
        "lang_changed": "✅ زبان به فارسی تغییر یافت! آماده کاوش در ویژگی‌های ربات Ipverse هستید.",
        "invalid_country": "❌ کد کشور نامعتبر است! لطفاً یک کد ۲ حرفی معتبر (مثل US، IR) وارد کنید.",
        "processing": "⏳ در حال دریافت محدوده‌های آی‌پی برای {}... لطفاً صبر کنید.\n📄 صفحات پردازش شده: {}\n🔢 تعداد ASNها: {}\n🌐 تعداد محدوده‌های آی‌پی: {}\n⏱ زمان سپری شده: {:.1f} ثانیه",
        "processing_complete": "✅ پردازش برای {} تکمیل شد!",
        "done": "✅ گزارش محدوده آی‌پی برای {}\n📅 تولید شده در: {}\n\n📄 صفحات پردازش شده: {}\n🔢 تعداد ASNها: {}\n🌐 تعداد محدوده‌های آی‌پی: {}\n⏱ زمان صرف شده: {:.1f} ثانیه\n\n💾 فایل آماده دانلود است!",
        "update_ip": "🔄 دریافت محدوده آی‌پی",
        "update_ip_prompt": "🌍 لطفاً یک کد ۲ حرفی کشور (مثل US، IR) را برای دریافت محدوده آی‌پی وارد کنید:",
        "account": "👤 حساب کاربری",
        "referral": "📎 دعوت از دوستان",
        "no_coins": "❌ برای دریافت محدوده‌های بیشتر به ۱ سکه نیاز دارید!\n📎 دوستان خود را دعوت کنید تا سکه به دست آورید یا حساب کاربری خود را بررسی کنید。",
        "daily_limit": "⛔ شما به محدودیت روزانه ۵ درخواست رایگان محدوده آی‌پی رسیده‌اید.\n💰 برای درخواست‌های اضافی از ۱ سکه استفاده کنید یا دوستان خود را دعوت کنید تا سکه بیشتری به دست آورید!",
        "referral_info": "📎 لینک دعوت شما: {}\n\n🎁 دوستان خود را به ربات Ipverse دعوت کنید و برای هر کاربر جدید که با لینک شما ملحق شود، ۱ سکه دریافت کنید!\n💡 این لینک را به اشتراک بگذارید تا موجودی سکه خود را افزایش دهید و درخواست‌های بیشتری برای محدوده آی‌پی باز کنید。",
        "referral_notification": "🎉 کاربر جدید با آیدی {} از طریق لینک دعوت شما به ربات پیوست!\n💰 شما ۱ سکه دریافت کردید. موجودی شما: {} سکه.",
        "account_info": "👤 جزئیات حساب کاربری شما:\n💰 موجودی سکه: {} سکه\n📊 درخواست‌های رایگان روزانه باقی‌مانده: {}\n🔄 درخواست‌های استفاده شده امروز: {}\n\n🔹 روزانه ۵ درخواست رایگان برای محدوده آی‌پی دریافت می‌کنید.\n🔹 درخواست‌های اضافی هر کدام ۱ سکه هزینه دارند.\n🔹 دوستان خود را دعوت کنید تا سکه بیشتری به دست آورید!",
        "admin_panel": "🛠 پنل مدیریت ربات",
        "admin_stats": "📈 داشبورد ربات Ipverse\n👥 تعداد کل کاربران: {}\n📄 تعداد فایل‌های آی‌پی تولید شده: {}\n🔄 تعداد فایل‌های آی‌پی کش شده: {}\n💰 تعداد سکه‌های مصرف شده: {}\n\n🔧 برای مدیریت ربات Ipverse یکی از گزینه‌های زیر را انتخاب کنید:",
        "manage_channels": "📢 مدیریت کانال‌ها\n\nکانال‌های کنونی:\n{}\n\n🔧 یک اقدام برای مدیریت کانال‌ها انتخاب کنید:",
        "manage_channels_button": "کنترل کانال‌ها",
        "toggle_force_join": "🔒 تغییر وضعیت اجبار به عضویت ({})",
        "broadcast": "📣 ارسال پیام همگانی",
        "add_channel": "➕ افزودن کانال جدید",
        "add_channel_prompt": "📢 لطفاً نام کاربری کانال (مثل @ChannelName) را برای افزودن وارد کنید:",
        "remove_channel": "🗑 حذف کانال",
        "back": "⬅ بازگشت",
        "channel_list": "📋 کانال‌های کنونی:\n{}\n\n🔧 یک اقدام را انتخاب کنید:",
        "enter_channel": "📢 لطفاً نام کاربری کانال (مثل @ChannelName) را برای افزودن وارد کنید:",
        "not_admin": "⚠ ربات Ipverse در {} ادمین نیست. لطفاً ربات را ادمین کنید و دوباره بررسی کنید.",
        "check_again": "🔄 دوباره بررسی کنید",
        "select_remove_channel": "🗑 انتخاب کانال برای حذف:\n\n{}\n\nیک کانال را برای حذف از ربات انتخاب کنید:",
        "channel_added": "🎉 کانال {} با موفقیت اضافه شد! اکنون بخشی از Ipverse است.",
        "channel_removed": "✅ کانال {} با موفقیت حذف شد! دیگر نیازی به آن نیست.",
        "force_join_toggled": "🔄 اجبار به عضویت به {} تغییر یافت!",
        "broadcast_prompt": "📣 لطفاً پیام (متن، عکس، ویدیو و غیره) را برای ارسال همگانی به همه کاربران بفرستید:",
        "broadcast_progress": "📣 ارسال همگانی در حال انجام:\n👥 ارسال شده: {}/{} کاربر\n⏱ زمان تخمینی باقی‌مانده: {:.1f} ثانیه",
        "broadcast_done": "✅ ارسال همگانی تکمیل شد: {}/{} ارسال شد، {} ناموفق",
        "spam_warning": "⚠ کمی آرام‌تر! شما بیش از حد سریع پیام می‌فرستید. لطفاً {} ثانیه صبر کنید و دوباره امتحان کنید.",
        "rate_limit_warning": "⛔ شما از محدودیت {} درخواست در دقیقه عبور کرده‌اید. لطفاً {} ثانیه دیگر دوباره امتحان کنید.",
        "file_locked": "⏳ لیست آی‌پی برای {} در حال تولید است. لطفاً چند دقیقه دیگر دوباره امتحان کنید یا فایل کشور دیگری را درخواست کنید."
    }
}