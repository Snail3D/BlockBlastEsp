#!/bin/bash
# Block Blast ESP32 Upload Script
# Usage: ./upload.sh /dev/tty.usbserial-... (or your serial port)

set -e

# Check for port argument
if [ -z "$1" ]; then
    echo "Usage: $0 <serial-port>"
    echo "Example: $0 /dev/tty.usbserial-... or /dev/ttyUSB0"
    exit 1
fi

PORT=$1

# Check if ampy is installed
if ! command -v ampy &> /dev/null; then
    echo "Error: ampy not found. Install with: pip install adafruit-ampy"
    exit 1
fi

echo "Uploading Block Blast ESP32 to $PORT..."

# Upload boot.py
echo "Uploading boot.py..."
ampy --port $PORT put boot.py

# Upload main.py
echo "Uploading main.py..."
ampy --port $PORT put main.py

echo "Done! Reset your ESP32 or reconnect to start the game."
echo "Connect to WiFi: BlockBlast (password: playblockblast)"
echo "Then visit: http://192.168.4.1"
