"""
IP Processing Module for IpverseBot

This module handles the core functionality of fetching, processing, and caching
IP range data from ipinfo.io. It provides comprehensive IP range reports for
different countries by querying ASN (Autonomous System Number) data.

Key Features:
- Fetch ASN data from ipinfo.io with proper headers and rate limiting
- Process multiple pages of data with progress tracking
- Generate comprehensive IP range reports
- Cache results for efficient reuse
- Handle rate limiting and retry logic
- Support for real-time progress updates

Functions:
    fetch_asn_data(session, country, page): Fetch ASN data for a specific page
    process_country(bot, message, country, user_id, lang): Main processing function
    
Developed by Matrix Team
"""

import aiohttp
import os
import random
import time
from datetime import datetime
from typing import Optional, Tuple
from aiogram import Bot
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import IP_CACHE_DIR, LANGUAGES
from utils.db import load_ip_files, save_ip_files, load_users, save_users
from utils.logging import write_log
import asyncio

async def fetch_asn_data(session: aiohttp.ClientSession, country: str, page: int) -> Optional[dict]:
    """
    Fetch ASN data for a given country and page from ipinfo.io.
    
    Args:
        session (aiohttp.ClientSession): HTTP session for making requests
        country (str): 2-letter country code (e.g., 'US', 'IR')
        page (int): Page number to fetch (pagination)
        
    Returns:
        Optional[dict]: JSON response containing ASN data, or None if failed
    """
    url = f"https://ipinfo.io/api/data/asns?country={country}&amount=20&page={page}"
    headers = {
        'authority': 'ipinfo.io',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.7',
        'cookie': '__stripe_mid=2c0a8917-0e62-49e8-95fe-2b0abbb53b5ae9d36d; __stripe_sid=f55ca662-5b49-4eb9-a4b4-7e9f8adcf40bd6d86b',
        'if-none-match': '"1730lzseg2n1q7"',
        'referer': 'https://ipinfo.io/countries/' + country,
        'sec-ch-ua': '"Not A(Brand";v="99", "Brave";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    attempts = 0
    while attempts < 3:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 429:
                    attempts += 1
                    write_log(f"Rate limited for page {page}. Retrying {attempts}/3...")
                    await asyncio.sleep(5)
                    continue
                if response.status != 200:
                    write_log(f"Error: Received status code {response.status} for page {page}")
                    return None
                return await response.json()
        except Exception as e:
            write_log(f"Exception in fetch_asn_data: {e}")
            return None
    return None

async def fetch_asn_details(session: aiohttp.ClientSession, asn: str) -> Optional[str]:
    """Fetch IP details for a specific ASN."""
    try:
        asn_url = f"https://raw.githubusercontent.com/ipverse/asn-ip/master/as/{asn}/ipv4-aggregated.txt"
        async with session.get(asn_url) as response:
            if response.status == 404:
                write_log(f"ASN {asn}: File not found (404).")
                return None
            text = await response.text()
            return "\n".join(text.split("\n")[3:])
    except Exception as e:
        write_log(f"Exception in fetch_asn_details for ASN {asn}: {e}")
        return None

async def process_country(bot: Bot, message: Message, session: aiohttp.ClientSession, country: str, user_id: str, lang: str) -> Optional[Tuple[str, int, int, float]]:
    """Process IP ranges for a given country and return file path and stats."""
    write_log(f"Processing country {country} for user {user_id}, message_id {message.message_id}")
    ip_files = load_ip_files()
    today = datetime.now().strftime("%Y-%m-%d")
    cache_file = os.path.join(IP_CACHE_DIR, f"ips-{country}-{today}.txt")
    users = load_users()

    # Check cache
    if os.path.exists(cache_file):
        write_log(f"Using cached file for {country}: {cache_file}")
        ip_files[country] = ip_files.get(country, {})
        stats = ip_files[country].get(today, {})

        # Initialize stats if not present or incomplete
        if not stats or not stats.get("asns") or not stats.get("cached"):
            try:
                with open(cache_file, "r") as f:
                    content = f.read()
                if not content.strip():
                    write_log(f"Cached file {cache_file} is empty")
                    await bot.send_message(message.chat.id, LANGUAGES[lang]["invalid_country"], parse_mode="Markdown")
                    return None
                stats = {
                    "file_path": cache_file,
                    "asns": random.randint(10, 50),
                    "ips": random.randint(100, 500),
                    "time": 0.0,  # Placeholder for real processing time
                    "cached": True,
                    "locked": False
                }
                ip_files[country][today] = stats
                save_ip_files(ip_files)
                write_log(f"Initialized stats for {country}: asns={stats['asns']}, ips={stats['ips']}, time={stats['time']}")
            except Exception as e:
                write_log(f"Error reading cached file {cache_file}: {e}")
                await bot.send_message(message.chat.id, LANGUAGES[lang]["invalid_country"], parse_mode="Markdown")
                return None

        # Process cached file
        try:
            # Validate file accessibility
            if not os.path.exists(cache_file):
                write_log(f"Cached file {cache_file} does not exist")
                await bot.send_message(message.chat.id, LANGUAGES[lang]["invalid_country"], parse_mode="Markdown")
                return None

            # Generate new fake_time for this request
            random.seed(time.time() + message.message_id)  # Dynamic seed for better randomness
            fake_time = random.uniform(5.0, 25.0)
            total_asns = stats["asns"]
            total_ips = stats["ips"]
            pages = total_asns // 20 + 1
            steps = int(fake_time) if fake_time >= 1 else 1  # Number of updates
            step_time = fake_time / steps if steps > 0 else fake_time
            write_log(f"Generated new fake_time: {fake_time} seconds for {country}")

            # Send initial processing message
            msg = await bot.send_message(
                message.chat.id,
                LANGUAGES[lang]["processing"].format(country.upper(), 0, 0, 0, 0),
                parse_mode="Markdown"
            )
            users[user_id]["last_message_id"] = msg.message_id
            save_users(users)
            write_log(f"Sent initial processing message for cached file, message_id: {msg.message_id}")

            # Simulate progress
            for step in range(steps):
                progress = (step + 1) / steps
                current_pages = int(pages * progress)
                current_asns = int(total_asns * progress)
                current_ips = int(total_ips * progress)
                current_time = step_time * (step + 1)
                try:
                    await bot.edit_message_text(
                        text=LANGUAGES[lang]["processing"].format(
                            country.upper(), current_pages, current_asns, current_ips, current_time
                        ),
                        chat_id=message.chat.id,
                        message_id=msg.message_id,
                        parse_mode="Markdown"
                    )
                    write_log(f"Updated processing message: pages={current_pages}, asns={current_asns}, ips={current_ips}, time={current_time}")
                except Exception as e:
                    write_log(f"Failed to update processing message for {country}: {e}")
                await asyncio.sleep(step_time)

            # Mark processing complete
            try:
                await bot.edit_message_text(
                    text=LANGUAGES[lang]["processing_complete"].format(country.upper()),
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    parse_mode="Markdown"
                )
                write_log(f"Edited message to processing_complete for {country}")
            except Exception as e:
                write_log(f"Failed to edit processing_complete message for {country}: {e}")
                msg = await bot.send_message(
                    message.chat.id,
                    LANGUAGES[lang]["processing_complete"].format(country.upper()),
                    parse_mode="Markdown"
                )
                users[user_id]["last_message_id"] = msg.message_id
                save_users(users)

            # Send the file
            try:
                file = FSInputFile(cache_file)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
                ])
                msg = await message.answer_document(
                    file,
                    caption=LANGUAGES[lang]["done"].format(
                        country.upper(), current_time, pages, total_asns, total_ips, fake_time
                    ),
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                users[user_id]["last_message_id"] = msg.message_id
                save_users(users)
                write_log(f"Sent cached file {cache_file} with stats: pages={pages}, asns={total_asns}, ips={total_ips}, time={fake_time}")
                return cache_file, total_asns, total_ips, fake_time
            except Exception as e:
                write_log(f"Error sending cached file {cache_file}: {e}")
                await bot.send_message(message.chat.id, LANGUAGES[lang]["invalid_country"], parse_mode="Markdown")
                return None
        except Exception as e:
            write_log(f"Unexpected error in cached file handling for {country}: {e}")
            await bot.send_message(message.chat.id, LANGUAGES[lang]["invalid_country"], parse_mode="Markdown")
            return None

    # Check if file is locked
    if country in ip_files and today in ip_files[country] and ip_files[country][today].get("locked", False):
        await bot.send_message(message.chat.id, LANGUAGES[lang]["file_locked"].format(country.upper()), parse_mode="Markdown")
        return None

    # Lock the file
    ip_files[country] = ip_files.get(country, {})
    ip_files[country][today] = ip_files[country].get(today, {})
    ip_files[country][today]["locked"] = True
    save_ip_files(ip_files)

    # Real processing
    page = 1
    aggregated_content = ""
    total_asns = 0
    total_ips = 0
    start_time = datetime.now()

    msg = await bot.send_message(message.chat.id, LANGUAGES[lang]["processing"].format(country.upper(), 0, 0, 0, 0), parse_mode="Markdown")
    users[user_id]["last_message_id"] = msg.message_id
    save_users(users)

    while True:
        page_data = await fetch_asn_data(session, country, page)
        if not page_data:
            if page == 1:
                await bot.edit_message_text(
                    text=LANGUAGES[lang]["invalid_country"],
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    parse_mode="Markdown"
                )
                ip_files[country][today]["locked"] = False
                save_ip_files(ip_files)
                return None
            write_log(f"Stopping at page {page}. No data returned.")
            break

        asns = [item['asn'].replace('AS', '') for item in page_data if item['type'] != 'inactive' and item['numberOfIps'] != 0]
        total_asns += len(asns)
        write_log(f"Page {page}: Found {len(asns)} ASNs.")

        for asn in asns:
            details = await fetch_asn_details(session, asn)
            if details:
                aggregated_content += details
                total_ips += len(details.split("\n"))

        elapsed_time = (datetime.now() - start_time).total_seconds()
        await bot.edit_message_text(
            text=LANGUAGES[lang]["processing"].format(country.upper(), page, total_asns, total_ips, elapsed_time),
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="Markdown"
        )
        page += 1
        await asyncio.sleep(0.1)  # Prevent overwhelming the API

    if not aggregated_content.strip():
        await bot.edit_message_text(
            text=LANGUAGES[lang]["invalid_country"],
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="Markdown"
        )
        ip_files[country][today]["locked"] = False
        save_ip_files(ip_files)
        return None

    file_path = cache_file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        file.write(aggregated_content)

    elapsed_time = (datetime.now() - start_time).total_seconds()
    ip_files[country][today] = {
        "file_path": file_path,
        "asns": total_asns,
        "ips": total_ips,
        "time": elapsed_time,  # Store real processing time
        "cached": True,
        "locked": False
    }
    save_ip_files(ip_files)
    write_log(f"Generated file {file_path} with size {len(aggregated_content)} bytes.")

    # Send the file for real processing
    try:
        file = FSInputFile(file_path)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=LANGUAGES[lang]["back"], callback_data="back_main")]
        ])
        msg = await message.answer_document(
            file,
            caption=LANGUAGES[lang]["done"].format(
                country.upper(), current_time, total_asns // 20 + 1, total_asns, total_ips, elapsed_time
            ),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        users[user_id]["last_message_id"] = msg.message_id
        save_users(users)
        write_log(f"Sent real processed file {file_path} with stats: pages={total_asns // 20 + 1}, asns={total_asns}, ips={total_ips}, time={elapsed_time}")
    except Exception as e:
        write_log(f"Error sending real processed file {file_path}: {e}")
        await bot.send_message(message.chat.id, LANGUAGES[lang]["invalid_country"], parse_mode="Markdown")
        return None

    return file_path, total_asns, total_ips, elapsed_time