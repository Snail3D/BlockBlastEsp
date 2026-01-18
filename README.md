# Block Blast ESP32

A Block Blast puzzle game clone that runs on ESP32, creating a WiFi access point so anyone can play from their phone.

## Features

- **8x8 Grid**: Classic Block Blast gameplay on an 8x8 grid
- **20+ Unique Pieces**: Tetromino and polyomino shapes with different colors
- **Line Clearing**: Clear rows and columns to score points
- **High Score**: Persistent high score saved locally
- **Multiplayer Access Point**: Anyone can connect to the ESP32's WiFi and play simultaneously
- **Touch & Mouse Support**: Works on both mobile and desktop browsers
- **Modern UI**: Clean design with gradients, animations, and glass-morphism effects
- **Visual Feedback**: Green highlight for valid placement, red for invalid
- **Memory Optimized**: Minimal footprint for ESP32 constraints

## Hardware Setup

### Requirements

- ESP32 development board
- USB cable for programming

### 1. Install MicroPython on ESP32

Download and flash MicroPython firmware to your ESP32:

```bash
# Install esptool
pip install esptool

# Flash MicroPython (replace /dev/tty.usbserial-... with your port)
esptool.py --chip esp32 --port /dev/tty.usbserial-... erase_flash
esptool.py --chip esp32 --port /dev/tty.usbserial-... write_flash -z 0x1000 \
  https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin
```

### 2. Upload Files to ESP32

```bash
# Install mpremote for file upload
pip install mpremote

# Upload boot.py
mpremote connect /dev/tty.usbserial-... cp boot.py :boot.py

# Upload main.py
mpremote connect /dev/tty.usbserial-... cp main.py :main.py
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

## Local Testing (No Hardware)

To test the game without ESP32 hardware, simply open `index.html` in your browser.

## Game Rules

1. **Drag pieces** from the bottom onto the grid
2. **Fill entire rows or columns** to clear them and score points
3. **Green preview** = valid placement, **Red preview** = invalid
4. **Game ends** when no pieces can be placed
5. **Try to beat your high score!**

## Pieces Available

- 2-block: horizontal (I2), vertical (I2|), small L shapes
- 3-block: horizontal (I3), vertical (I3|), L shapes
- 4-block: I (horizontal/vertical), O (square), T, L, J, S, Z tetrominoes
- 5-block: I (pentomino)

*Note: No 1x1 single piece - that's not in Block Blast!*

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
├── .gitignore       # Git ignore file
└── README.md        # This file
```

## Troubleshooting

**Game not loading?**
- Make sure ESP32 is connected and powered
- Check that you're connected to the BlockBlast WiFi network
- Try refreshing the browser page (hard refresh: Ctrl+Shift+R)

**Pieces not placing?**
- Hard refresh your browser to clear cache
- Make sure you're dropping on a green-highlighted cell

**Can't connect to WiFi?**
- ESP32 may take 10-15 seconds to start the AP after powering on
- Check that ESP32 is running (the blue LED should be on)

## License

MIT License - Free to use and modify

## Credits

Created with Claude Code
