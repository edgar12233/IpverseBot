# IpverseBot - Telegram IP Range Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/aiogram-3.12.0-blue.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[🇺🇸 English](#english) | [🇮🇷 فارسی](README-FA.md)

---

## English

### 📖 Description

IpverseBot is a comprehensive Telegram bot that provides IP range information for different countries. The bot fetches ASN (Autonomous System Number) data from ipinfo.io and generates detailed IP range reports that users can download.

### ✨ Features

- **🌍 Country IP Ranges**: Get comprehensive IP ranges for any country using 2-letter country codes
- **🏆 Multi-language Support**: Full support for English and Persian/Farsi languages
- **💰 Coin System**: Users get 5 free requests daily, additional requests cost coins
- **👥 Referral System**: Earn coins by inviting friends to use the bot
- **📊 Admin Panel**: Complete admin dashboard with statistics and management tools
- **🔒 Channel Management**: Force users to join specific channels before using the bot
- **📢 Broadcast System**: Send messages to all users simultaneously
- **⚡ Rate Limiting**: Built-in spam protection and request rate limiting
- **💾 Smart Caching**: Intelligent file caching system to improve performance
- **📈 User Analytics**: Track user statistics and bot usage metrics

### 🛠️ Installation

#### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Matrix-Community-ORG/IpverseBot.git
cd IpverseBot
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id_here
```

#### Step 4: Run the Bot

```bash
python main.py
```

### 📋 Configuration

The bot configuration is located in `config/settings.py`. Key settings include:

- **SPAM_THRESHOLD**: Time between non-admin commands (default: 2 seconds)
- **RATE_LIMIT_REQUESTS**: Max IP requests per minute per user (default: 10)
- **RATE_LIMIT_PERIOD**: Rate limit window in seconds (default: 60)
- **LOG_ENABLED**: Enable/disable logging (default: False)

### 🎯 Usage

1. **Start the bot**: Send `/start` to begin
2. **Select language**: Choose your preferred language
3. **Join channels**: Join required channels (if force join is enabled)
4. **Request IP ranges**: Send a 2-letter country code (e.g., `US`, `IR`, `DE`)
5. **Download reports**: Get comprehensive IP range files

### 🔧 Admin Commands

Admins have access to special features:

- **Admin Panel**: Access via callback buttons after `/start`
- **Channel Management**: Add/remove required channels
- **Toggle Force Join**: Enable/disable mandatory channel membership
- **Broadcast Messages**: Send messages to all users
- **View Statistics**: Monitor bot usage and user metrics

### 📁 Project Structure

```
IpverseBot/
├── main.py                 # Main bot entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── config/
│   └── settings.py       # Bot configuration and language strings
├── handlers/
│   ├── user.py          # User message handlers
│   ├── admin.py         # Admin panel handlers
│   └── callback.py      # Callback query handlers
├── utils/
│   ├── db.py            # Database operations (JSON-based)
│   ├── ip_processing.py # IP range fetching and processing
│   ├── telegram.py      # Telegram utility functions
│   └── logging.py       # Logging utilities
└── data/
    ├── users.json       # User database
    ├── ip_files.json    # IP files cache database
    ├── settings.json    # Bot settings
    └── ip_cache/        # Cached IP range files
```

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📞 Support

- **English Community**: [@MatrixORG](https://t.me/MatrixORG)
- **Persian Community**: [@MatrixFa](https://t.me/MatrixFa)
- **Chat Group**: [@DD0SChat](https://t.me/DD0SChat)

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by Matrix Team**
