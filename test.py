#!/usr/bin/env python3
"""
Block Blast ESP32 Test Script
Tests the game locally and checks ESP32 connection
"""

import os
import sys
import subprocess
import glob
import socket
import time

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.GREEN}{Colors.BOLD}✓{Colors.END} {msg}")


def print_error(msg):
    print(f"{Colors.RED}{Colors.BOLD}✗{Colors.END} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}{Colors.BOLD}ℹ{Colors.END} {msg}")


def print_test(msg):
    print(f"{Colors.CYAN}{Colors.BOLD}▶{Colors.END} Testing {msg}...")


def test_file_exists(filepath):
    """Test if a file exists"""
    return os.path.exists(filepath)


def test_html_syntax():
    """Test HTML file has valid structure"""
    if not test_file_exists('index.html'):
        return False, "index.html not found"

    with open('index.html', 'r') as f:
        content = f.read()

    required = ['<!DOCTYPE html>', '<html', '<head>', '<body>', '</html>', '<canvas', '</canvas>']
    missing = [r for r in required if r not in content]

    if missing:
        return False, f"Missing HTML elements: {', '.join(missing)}"

    return True, "HTML structure valid"


def test_css_exists():
    """Test CSS file exists and has styles"""
    if not test_file_exists('style.css'):
        return False, "style.css not found"

    with open('style.css', 'r') as f:
        content = f.read()

    required = ['.game-container', '#gameCanvas', '.piece-slot']
    missing = [r for r in required if r not in content]

    if missing:
        return False, f"Missing CSS classes: {', '.join(missing)}"

    return True, "CSS styles found"


def test_js_syntax():
    """Test JavaScript file has game logic"""
    if not test_file_exists('game.js'):
        return False, "game.js not found"

    with open('game.js', 'r') as f:
        content = f.read()

    required = ['GRID_SIZE', 'drawGrid()', 'placePiece(', 'checkAndClearLines()']
    missing = [r for r in required if r not in content]

    if missing:
        return False, f"Missing JS functions: {', '.join(missing)}"

    return True, "JavaScript game logic found"


def test_micropython_file():
    """Test MicroPython file exists"""
    if not test_file_exists('main.py'):
        return False, "main.py not found"

    with open('main.py', 'r') as f:
        content = f.read()

    required = ['network.WLAN', 'socket.socket', 'HTML_CONTENT']
    missing = [r for r in required if r not in content]

    if missing:
        return False, f"Missing MicroPython elements: {', '.join(missing)}"

    return True, "MicroPython server code found"


def test_file_sizes():
    """Test file sizes are reasonable for ESP32"""
    max_html_size = 50 * 1024  # 50KB max for embedded HTML

    with open('main.py', 'r') as f:
        content = f.read()
        html_size = len(content.encode('utf-8'))

    if html_size > max_html_size:
        return False, f"HTML content too large: {html_size} bytes (max: {max_html_size})"

    return True, f"Embedded HTML size: {html_size} bytes"


def test_serial_connection():
    """Test if ESP32 is connected"""
    port = find_serial_port()

    if not port:
        return False, "No ESP32 detected on serial port"

    # Try to open the port
    try:
        import serial
        ser = serial.Serial(port, 115200, timeout=1)
        ser.close()
        return True, f"ESP32 detected on {port}"
    except ImportError:
        return False, "pyserial not installed (pip install pyserial)"
    except Exception as e:
        return False, f"Cannot connect to ESP32: {e}"


def find_serial_port():
    """Find ESP32 serial port"""
    if sys.platform == 'darwin':  # macOS
        ports = glob.glob('/dev/cu.usbserial*') + glob.glob('/dev/cu.usbmodem*')
        if ports:
            return ports[0]
    elif sys.platform.startswith('linux'):
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        if ports:
            return ports[0]
    elif sys.platform == 'win32':
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'USB' in port.description or 'Serial' in port.description:
                    return port.device
        except ImportError:
            pass
    return None


def test_upload_tool():
    """Test if upload tool is available"""
    tools = ['rshell', 'ampy', 'mpfshell']

    for tool in tools:
        try:
            subprocess.run(['which', tool], capture_output=True, check=True)
            return True, f"Upload tool available: {tool}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    return False, "No upload tool found (install rshell, ampy, or mpfshell)"


def run_all_tests():
    """Run all tests and report results"""
    print()
    print("=" * 50)
    print(f"{Colors.BOLD}Block Blast ESP32 Test Suite{Colors.END}")
    print("=" * 50)
    print()

    tests = [
        ("HTML Structure", test_html_syntax),
        ("CSS Styles", test_css_exists),
        ("JavaScript Logic", test_js_syntax),
        ("MicroPython Code", test_micropython_file),
        ("File Sizes", test_file_sizes),
        ("Serial Connection", test_serial_connection),
        ("Upload Tool", test_upload_tool),
    ]

    passed = 0
    failed = 0
    warnings = 0

    for name, test_func in tests:
        print_test(name)

        try:
            success, message = test_func()

            if success:
                print_success(message)
                passed += 1
            else:
                if "Warning" in message:
                    print_warning(message)
                    warnings += 1
                else:
                    print_error(message)
                    failed += 1
        except Exception as e:
            print_error(f"Test error: {e}")
            failed += 1

        print()

    # Summary
    print("=" * 50)
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print("=" * 50)
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.YELLOW}Warnings: {warnings}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print()

    # Recommendations
    if failed > 0:
        print(f"{Colors.YELLOW}Recommendations:{Colors.END}")
        print("  1. Fix failed tests above")
        print("  2. Ensure ESP32 is connected via USB")
        print("  3. Install upload tool: pip install rshell")
        print()
    elif warnings > 0:
        print(f"{Colors.YELLOW}⚠ Some warnings detected, but tests passed{Colors.END}")
        print()

    if failed == 0:
        print_success("All tests passed! Ready to upload.")
        print()
        print(f"{Colors.BOLD}Next steps:{Colors.END}")
        print("  1. Upload to ESP32: python upload.py")
        print("  2. Connect to WiFi: BlockBlast-ESP32")
        print("  3. Open browser: http://192.168.4.1")
        print()

    return failed == 0


def main():
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print_info("Tests cancelled.")
        sys.exit(0)


if __name__ == '__main__':
    main()
