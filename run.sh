#!/bin/bash
# Setup and run ASTHENIA game

echo "⚔️ ASTHENIA Setup ⚔️"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Install pygame if not already installed
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎮 Starting ASTHENIA..."
python3 asthenia.py
