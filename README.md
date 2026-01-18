# Block Blast ESP32

A Block Blast puzzle game clone that runs on ESP32, creating a WiFi access point so anyone can play from their phone.

## Features

- **8x8 Grid**: Classic Block Blast gameplay on an 8x8 grid
- **15 Unique Pieces**: All tetromino-like shapes with different colors
- **Line Clearing**: Clear rows and columns to score points
- **High Score**: Persistent high score saved locally
- **Multiplayer Access Point**: Anyone can connect to the ESP32's WiFi and play
- **Touch & Mouse Support**: Works on both mobile and desktop
- **Modern UI**: Clean design with gradients, animations, and glass-morphism effects
- **Memory Optimized**: Minimal footprint for ESP32 constraints

## Hardware

- ESP32 development board
- USB cable for programming

## Software Setup

### 1. Install MicroPython on ESP32

Download and flash MicroPython firmware to your ESP32:

```bash
# Install esptool
pip install esptool

# Flash MicroPython (replace /dev/tty.usbserial-... with your port)
esptool.py --chip esp32 --port /dev/tty.usbserial-... write_flash -z 0x1000 \
  https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin
```

### 2. Upload Files to ESP32

```bash
# Install ampy for file upload
pip install adafruit-ampy

# Upload boot.py
ampy --port /dev/tty.usbserial-... put boot.py

# Upload main.py
ampy --port /dev/tty.usbserial-... put main.py
```

Or use the provided upload script:

```bash
chmod +x upload.sh
./upload.sh /dev/tty.usbserial-...
```

### 3. Connect and Play

1. Power on the ESP32
2. Connect to WiFi: **BlockBlast** (password: `playblockblast`)
3. Open browser: http://192.168.4.1
4. Start playing!

## Local Testing

To test the game without ESP32 hardware, simply open `index.html` in your browser.

## Game Rules

1. Drag pieces from the bottom onto the grid
2. Place pieces to fill entire rows or columns
3. Complete lines clear and award points
4. Game ends when no pieces can be placed
5. Try to beat your high score!

## Customization

Edit `main.py` to change:

- AP SSID: `AP_SSID = "BlockBlast"`
- AP Password: `AP_PASSWORD = "playblockblast"`
- AP IP: `AP_IP = "192.168.4.1"`

## File Structure

```
block-blast-esp32/
├── boot.py          # Auto-start script (runs on boot)
├── main.py          # Main server (WiFi AP + HTTP server + embedded game)
├── index.html       # Standalone version for local testing
├── upload.sh        # Upload script for ESP32
└── README.md        # This file
```

## License

MIT License - Free to use and modify

## Credits

Created with Claude Code
