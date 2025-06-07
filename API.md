# IpverseBot API Documentation

## Overview

IpverseBot provides a comprehensive Telegram bot interface for retrieving IP range information for different countries. This document describes the internal API structure and key functions.

## Core Modules

### 1. Main Application (`main.py`)

#### `main()`
- **Description**: Main entry point for the bot
- **Parameters**: None
- **Returns**: None
- **Functionality**: Initializes bot, registers handlers, starts polling

#### `cleanup_cache()`
- **Description**: Background task for cleaning old cache files
- **Parameters**: None
- **Returns**: None
- **Schedule**: Runs every 24 hours

### 2. Configuration (`config/settings.py`)

#### Environment Variables
- `BOT_TOKEN`: Telegram bot token from BotFather
- `ADMIN_ID`: Telegram user ID of the administrator

#### Constants
- `SPAM_THRESHOLD`: 2 seconds (minimum time between requests)
- `RATE_LIMIT_REQUESTS`: 10 (max requests per minute)
- `RATE_LIMIT_PERIOD`: 60 seconds (rate limit window)

### 3. Database Operations (`utils/db.py`)

#### `load_users() -> Dict[str, Any]`
- **Description**: Load user data from JSON database
- **Returns**: Dictionary of user data
- **Structure**:
  ```json
  {
    "user_id": {
      "lang": "en|fa",
      "coins": 0,
      "daily_requests": {"date": "YYYY-MM-DD", "count": 0},
      "referrer": "referrer_user_id",
      "referrals": 0,
      "last_message_id": null,
      "last_message_time": 0,
      "recent_requests": [],
      "processing": false,
      "referral_awarded": false
    }
  }
  ```

#### `save_users(users: Dict[str, Any]) -> None`
- **Description**: Save user data to JSON database
- **Parameters**: User data dictionary

#### `load_settings() -> Dict[str, Any]`
- **Description**: Load bot settings
- **Returns**: Settings dictionary
- **Structure**:
  ```json
  {
    "channels": ["@channel1", "@channel2"],
    "force_join": true
  }
  ```

### 4. IP Processing (`utils/ip_processing.py`)

#### `fetch_asn_data(session, country, page) -> Optional[dict]`
- **Description**: Fetch ASN data from ipinfo.io
- **Parameters**:
  - `session`: aiohttp ClientSession
  - `country`: 2-letter country code
  - `page`: Page number for pagination
- **Returns**: JSON response or None
- **Rate Limiting**: 3 retry attempts with 5-second delays

#### `process_country(bot, message, country, user_id, lang) -> None`
- **Description**: Main IP processing function
- **Parameters**:
  - `bot`: Bot instance
  - `message`: Telegram message
  - `country`: Country code
  - `user_id`: User ID
  - `lang`: User language
- **Functionality**: 
  - Fetches all ASN pages for country
  - Generates comprehensive IP range report
  - Caches results for reuse
  - Sends file to user

### 5. Telegram Utilities (`utils/telegram.py`)

#### `check_channel_membership(bot, user_id) -> bool`
- **Description**: Verify user membership in required channels
- **Parameters**: Bot instance, user ID
- **Returns**: True if member of all channels

#### `check_spam(bot, user_id, is_admin) -> bool`
- **Description**: Anti-spam protection
- **Parameters**: Bot instance, user ID, admin status
- **Returns**: True if request allowed

#### `check_rate_limit(bot, user_id, is_admin) -> bool`
- **Description**: Rate limiting check
- **Parameters**: Bot instance, user ID, admin status
- **Returns**: True if within rate limits

#### `sanitize_country_code(code) -> Optional[str]`
- **Description**: Validate and clean country code
- **Parameters**: Raw country code input
- **Returns**: Sanitized 2-letter code or None

## User Commands

### Basic Commands
- `/start` - Initialize bot, language selection, channel verification
- `<country_code>` - Request IP ranges (e.g., "US", "IR", "DE")

### Callback Actions
- `lang_en` / `lang_fa` - Language selection
- `check_join` - Verify channel membership
- `account` - View account information
- `referral` - Get referral link
- `admin_panel` - Admin dashboard (admin only)

## Admin Features

### Statistics Dashboard
- Total users count
- IP files generated
- Cached files count
- Coins spent by users

### Channel Management
- Add new required channels
- Remove channels
- Toggle force join requirement
- Verify bot admin status in channels

### Broadcasting
- Send messages to all users
- Progress tracking
- Delivery statistics

## Data Flow

### New User Registration
1. User sends `/start`
2. Check for referral parameter
3. Create user record in database
4. Language selection (if new user)
5. Channel membership verification (if enabled)
6. Award referral coins (if applicable)
7. Display welcome message

### IP Range Request
1. User sends country code
2. Validate country code format
3. Check user permissions (daily limit, coins)
4. Check spam/rate limits
5. Process request (fetch ASN data)
6. Generate and cache IP range file
7. Send file to user
8. Update user statistics

### Referral System
1. User gets referral link: `t.me/botname?start=user_id`
2. New user clicks link and starts bot
3. System records referrer in new user data
4. When new user completes verification, referrer gets 1 coin
5. Referrer receives notification

## Error Handling

### Common Errors
- Invalid country codes → User-friendly error message
- Rate limiting → Wait time notification
- Missing permissions → Channel join requirement
- API failures → Retry logic with exponential backoff

### Logging
- All major operations logged with timestamps
- Error tracking for debugging
- User action monitoring
- Performance metrics

## Security Measures

### Input Validation
- Country codes sanitized and validated
- User inputs escaped and cleaned
- Admin verification for sensitive operations

### Rate Limiting
- Per-user request limits
- Spam protection with time windows
- Admin bypass for all limits

### Data Protection
- Sensitive configuration in environment variables
- User data stored locally (no external databases)
- Automatic cleanup of temporary files

## Performance Optimizations

### Caching Strategy
- IP range files cached by country and date
- Automatic cleanup of files older than 1 day
- Reuse of cached files for multiple requests

### Asynchronous Operations
- Non-blocking I/O for all network operations
- Concurrent processing of multiple user requests
- Background cleanup tasks

### Memory Management
- Efficient JSON storage
- Minimal in-memory data structures
- Garbage collection of old cache entries

---

**Matrix Team**
- English Community: [@MatrixORG](https://t.me/MatrixORG)
- Persian Community: [@MatrixFa](https://t.me/MatrixFa)
- Chat Group: [@DD0SChat](https://t.me/DD0SChat)
