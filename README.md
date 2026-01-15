# Block Blast - ESP32

A Block Blast clone game that runs on ESP32, served via a WiFi access point. Connect your phone or browser to the ESP32's hotspot and play!

## Features

- **8x8 grid puzzle game** - Drag and drop Tetris-like pieces
- **Scoring system** - Matching Block Blast mechanics with combos
- **Block Blast colors** - Authentic color scheme matching the original game
- **Touch support** - Works on mobile devices
- **WiFi Access Point** - Open access point for easy connection
- **High score tracking** - Local storage saves your best score

## How to Play

1. **Connect to WiFi** - Join the "BlockBlast-ESP32" network (no password)
2. **Open browser** - Navigate to `http://192.168.4.1`
3. **Drag pieces** - Pick up pieces from the bottom and drag them onto the grid
4. **Clear lines** - Complete full rows or columns to clear them and score points
5. **Combos** - Clear multiple lines at once for bonus points!
6. **Game over** - Game ends when no pieces can fit on the grid

## Requirements

### Hardware
- ESP32 development board
- USB cable for programming

### Software
- Python 3.7+
- MicroPython firmware on ESP32
- One of the following upload tools:
  - `rshell` (recommended): `pip install rshell`
  - `ampy`: `pip install adafruit-ampy`
  - `mpfshell`: `pip install mpfshell`

## Setup

### 1. Install MicroPython on ESP32

If you haven't already, flash MicroPython to your ESP32:

```bash
# Install esptool
pip install esptool

# Download MicroPython firmware from:
# https://micropython.org/download/ESP32_GENERIC/

# Flash the firmware
esptool --chip esp32 --port /dev/tty.usbserial-XXX write_flash -z 0x1000 esp32-micropython.bin
```

### 2. Install Upload Tool

```bash
pip install rshell
```

### 3. Test Your Setup

Run the test script to verify everything is ready:

```bash
python3 test.py
```

### 4. Upload to ESP32

```bash
python3 upload.py
```

The script will auto-detect your ESP32 and upload the game.

## Manual Upload

If the upload script doesn't work, use rshell directly:

```bash
# Find your serial port
# macOS: /dev/cu.usbserial-XXX or /dev/cu.usbmodem-XXX
# Linux: /dev/ttyUSB0
# Windows: COM3, COM4, etc.

# Upload main.py
rshell --port /dev/cu.usbserial-XXX cp main.py /pyboard/main.py
```

## Playing the Game

1. Connect your phone/tablet/computer to WiFi network: **BlockBlast-ESP32**
2. Open a web browser and go to: **http://192.168.4.1**
3. Start playing!

## Game Mechanics

### Scoring

- **1 block placed** = 1 point
- **1 line cleared** = 10 points × combo multiplier
- **Multiple lines** = Bonus points
- **Combo multiplier** = Up to 5x for consecutive clears

### Combos

- Clear lines on consecutive placements to build your combo
- Higher combo = More points
- Combo resets when you place a piece without clearing lines

### Game Over

The game ends when:
- No remaining pieces can fit on the grid
- You still have pieces to place but no valid moves

## File Structure

```
block-blast-esp32/
├── index.html      # Game HTML structure (development)
├── style.css       # Game styling (development)
├── game.js         # Game logic (development)
├── main.py         # ESP32 MicroPython server (embedded HTML)
├── upload.py       # Upload script
├── test.py         # Test suite
└── README.md       # This file
```

## Development

The `index.html`, `style.css`, and `game.js` files are for development and testing. The `main.py` file contains a minified/embedded version of the game that runs on the ESP32.

To modify the game:

1. Edit the source files (`index.html`, `style.css`, `game.js`)
2. Test in your browser
3. Update `main.py` with the new content (the HTML is embedded in `HTML_CONTENT`)
4. Re-upload to ESP32

## Troubleshooting

### ESP32 not detected
- Check USB connection
- Install drivers for your ESP32 board
- Try a different USB cable

### Upload fails
- Make sure only one tool is accessing the serial port
- Close Arduino IDE or other serial monitors
- Try a different upload tool (ampy, mpfshell)

### Can't connect to WiFi
- Wait 10-20 seconds after upload for the AP to start
- Check your device's WiFi list for "BlockBlast-ESP32"
- Try `http://192.168.4.1` or `http://192.168.4.1:80`

### Game page doesn't load
- Clear browser cache
- Try a different browser
- Check serial monitor for errors

## Sources

- [Block Blast Strategy Guide](https://blockblastsolver.app/strategy.html)
- [Block Blast High Score Tips](https://blockblast.co/high-score)
- [Block Blast on Google Play](https://play.google.com/store/apps/details?id=com.sevag.block.blast.puzzle)
- [Block Blast Online](https://blockblastgame.io/)

## License

This is a personal project for educational purposes. Block Blast is a trademark of its respective owners.

## Credits

- Game inspired by [Block Blast](https://blockblastgame.io/)
- Built for ESP32 with MicroPython
