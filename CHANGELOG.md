# Changelog

All notable changes to IpverseBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-07

### Added
- **Core Features**
  - IP range fetching for any country using 2-letter country codes
  - ASN data retrieval from ipinfo.io with comprehensive reports
  - Multi-language support (English and Persian/Farsi)
  - User management system with coin-based economy
  - Referral system for earning coins through invitations
  - Daily free request limits (5 per day) with coin-based additional requests

- **Admin Panel**
  - Complete administrative dashboard with statistics
  - Channel management (add/remove required channels)
  - Force join toggle functionality
  - Broadcast messaging system to all users
  - User analytics and bot usage metrics

- **Security & Performance**
  - Rate limiting and spam protection
  - Smart caching system for IP range files
  - Environment variable configuration for sensitive data
  - Input validation and sanitization
  - Automated cleanup of old cache files

- **User Experience**
  - Interactive inline keyboards for navigation
  - Real-time progress tracking for IP processing
  - Account information display with coin balance
  - Referral link generation and tracking
  - Error handling with user-friendly messages

- **Technical Infrastructure**
  - JSON-based database system for user and cache data
  - Modular code structure with separation of concerns
  - Comprehensive logging system
  - Docker support for containerized deployment
  - Automated setup script for easy installation

- **Documentation**
  - Bilingual README (English and Persian)
  - Comprehensive code documentation with docstrings
  - Contributing guidelines for open source development
  - Docker deployment instructions
  - API documentation for all major functions

### Technical Details
- **Framework**: aiogram 3.12.0 for Telegram Bot API
- **HTTP Client**: aiohttp 3.10.5 for API requests
- **Configuration**: python-dotenv for environment management
- **Python Version**: 3.8+ support
- **Architecture**: Asynchronous with proper error handling

### Security Features
- Environment variable configuration for tokens
- Input validation for all user inputs
- Rate limiting to prevent abuse
- Secure admin verification
- Data sanitization for country codes

### Supported Languages
- English (en) - Complete translation
- Persian/Farsi (fa) - Complete translation with cultural considerations

---

**Matrix Team**
- English Community: [@MatrixORG](https://t.me/MatrixORG)
- Persian Community: [@MatrixFa](https://t.me/MatrixFa)
- Chat Group: [@DD0SChat](https://t.me/DD0SChat)
