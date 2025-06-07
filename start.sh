#!/bin/bash

# IpverseBot Startup Script
# Author: Matrix Team
# Description: Setup and run the IpverseBot with all dependencies

set -e  # Exit on any error

echo "🤖 IpverseBot Setup Script"
echo "=========================="

# Parse command line arguments
DOCKER_MODE=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--docker)
            DOCKER_MODE=true
            shift
            ;;
        -h|--help)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ "$HELP" = true ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --docker    Run using Docker"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run normally"
    echo "  $0 --docker     # Run with Docker"
    exit 0
fi

if [ "$DOCKER_MODE" = true ]; then
    echo "🐳 Docker mode selected"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        echo "❌ Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found. Creating from template..."
        cp .env.example .env
        echo "📝 Please edit .env file with your bot token and admin ID"
        exit 1
    fi
    
    echo "🚀 Starting IpverseBot with Docker..."
    $COMPOSE_CMD up --build
    exit 0
fi

# Regular installation mode
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

# Check if .env file exists
echo "🔧 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your bot token and admin ID:"
    echo "   BOT_TOKEN=your_telegram_bot_token_here"
    echo "   ADMIN_ID=your_telegram_user_id_here"
    echo ""
    echo "💡 Get your bot token from @BotFather on Telegram"
    echo "💡 Get your user ID from @userinfobot on Telegram"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Validate .env file
echo "🔍 Validating configuration..."
source .env

if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
    echo "❌ BOT_TOKEN not set in .env file"
    exit 1
fi

if [ -z "$ADMIN_ID" ] || [ "$ADMIN_ID" = "your_telegram_user_id_here" ]; then
    echo "❌ ADMIN_ID not set in .env file"
    exit 1
fi

echo "✅ Configuration validated"

# Install dependencies
echo "📦 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

# Create data directory
echo "📁 Setting up data directory..."
mkdir -p data/ip_cache

# Start the bot
echo "🚀 Starting IpverseBot..."
echo "Press Ctrl+C to stop the bot"
echo "=========================="

python3 main.py
