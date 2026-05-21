#!/bin/bash
# Raft Simulator - Startup Script for Windows

echo "=================================="
echo "    RAFT SIMULATOR - STARTUP"
echo "=================================="
echo ""
echo "Initializing Raft Simulator..."
echo ""

# Check Python installation
python --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found. Please install Python 3.8+"
    exit 1
fi

echo "[✓] Python found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python -m venv venv
fi

echo "[✓] Virtual environment ready"

# Activate venv and install dependencies
echo "[*] Installing/verifying dependencies..."
./venv/Scripts/pip install -q -r requirements.txt 2>/dev/null
echo "[✓] Dependencies installed"

# Run the app
echo ""
echo "=================================="
echo "[*] Starting Flask server..."
echo ""
echo "    URL: http://localhost:5000"
echo ""
echo "    Lab 1: http://localhost:5000/lab1"
echo "    Lab 2: http://localhost:5000/lab2"
echo "    Lab 3: http://localhost:5000/lab3"
echo "    Lab 4: http://localhost:5000/lab4"
echo ""
echo "Press CTRL+C to stop server"
echo "=================================="
echo ""

./venv/Scripts/python app.py
