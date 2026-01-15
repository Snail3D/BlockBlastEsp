#!/usr/bin/env python3
"""
Block Blast ESP32 Upload Script
Uploads the game to ESP32 using various methods
"""

import os
import sys
import subprocess
import time
import glob

# Default serial port - will auto-detect if possible
SERIAL_PORT = None
BAUD_RATE = 115200

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.GREEN}{Colors.BOLD}✓{Colors.END} {msg}")


def print_error(msg):
    print(f"{Colors.RED}{Colors.BOLD}✗{Colors.END} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}{Colors.BOLD}ℹ{Colors.END} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠{Colors.END} {msg}")


def find_serial_port():
    """Auto-detect ESP32 serial port"""
    if sys.platform == 'darwin':  # macOS
        ports = glob.glob('/dev/cu.usbserial*') + glob.glob('/dev/cu.usbmodem*')
        if ports:
            return ports[0]
    elif sys.platform.startswith('linux'):
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        if ports:
            return ports[0]
    elif sys.platform == 'win32':
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'USB' in port.description or 'Serial' in port.description:
                return port.device
    return None


def check_command(cmd):
    """Check if a command is available"""
    try:
        subprocess.run(['which', cmd], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def upload_with_rshell(port):
    """Upload using rshell"""
    print_info("Attempting upload with rshell...")

    if not check_command('rshell'):
        return False

    try:
        # Upload main.py
        result = subprocess.run([
            'rshell',
            '--port', port,
            'cp', 'main.py', '/pyboard/main.py'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print_error(f"rshell upload failed: {result.stderr}")
            return False

        print_success("Uploaded with rshell!")
        return True

    except Exception as e:
        print_error(f"rshell error: {e}")
        return False


def upload_with_ampy(port):
    """Upload using ampy"""
    print_info("Attempting upload with ampy (adafruit-ampy)...")

    if not check_command('ampy'):
        return False

    try:
        # Upload main.py
        result = subprocess.run([
            'ampy',
            '--port', port,
            '--baud', str(BAUD_RATE),
            'put', 'main.py', 'main.py'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print_error(f"ampy upload failed: {result.stderr}")
            return False

        print_success("Uploaded with ampy!")
        return True

    except Exception as e:
        print_error(f"ampy error: {e}")
        return False


def upload_with_mpfshell(port):
    """Upload using mpfshell"""
    print_info("Attempting upload with mpfshell...")

    if not check_command('mpfshell'):
        return False

    try:
        # Create commands file
        with open('.mpfshell_cmds.txt', 'w') as f:
            f.write(f"open {port}\n")
            f.write("put main.py\n")
            f.write("exit\n")

        result = subprocess.run([
            'mpfshell', '-n', '.mpfshell_cmds.txt'
        ], capture_output=True, text=True)

        # Clean up
        os.remove('.mpfshell_cmds.txt')

        if result.returncode != 0:
            print_error(f"mpfshell upload failed: {result.stderr}")
            return False

        print_success("Uploaded with mpfshell!")
        return True

    except Exception as e:
        print_error(f"mpfshell error: {e}")
        return False


def reset_esp32(port):
    """Reset the ESP32 to start the server"""
    print_info("Resetting ESP32...")

    try:
        if sys.platform == 'darwin':
            # macOS - toggle DTR
            subprocess.run(['stty', '-f', port, 'hupcl'], capture_output=True)
            time.sleep(0.5)
            subprocess.run(['stty', '-f', port, '-hupcl'], capture_output=True)
        else:
            # Use esptool if available
            if check_command('esptool'):
                subprocess.run([
                    'esptool',
                    '--port', port,
                    'run'
                ], capture_output=True)

        print_success("ESP32 reset!")
        time.sleep(2)  # Wait for boot
        return True

    except Exception as e:
        print_warning(f"Could not reset ESP32: {e}")
        print_info("Press RESET button on ESP32 manually")
        return False


def print_access_instructions():
    """Print instructions for accessing the game"""
    print()
    print("=" * 50)
    print(f"{Colors.GREEN}{Colors.BOLD}Block Blast ESP32 Server{Colors.END}")
    print("=" * 50)
    print()
    print(f"{Colors.BOLD}To play the game:{Colors.END}")
    print(f"1. Connect your phone/device to WiFi: {Colors.YELLOW}BlockBlast-ESP32{Colors.END}")
    print(f"2. Open browser and visit: {Colors.YELLOW}http://192.168.4.1{Colors.END}")
    print()
    print(f"{Colors.BOLD}To stop the server:{Colors.END}")
    print(f"  Press Ctrl+C in serial monitor, or press ESP32 reset button")
    print()
    print("=" * 50)


def main():
    print()
    print("=" * 50)
    print(f"{Colors.BOLD}Block Blast ESP32 Upload Script{Colors.END}")
    print("=" * 50)
    print()

    # Check if main.py exists
    if not os.path.exists('main.py'):
        print_error("main.py not found! Run this script from the project directory.")
        sys.exit(1)

    # Find or prompt for serial port
    global SERIAL_PORT
    SERIAL_PORT = find_serial_port()

    if not SERIAL_PORT:
        print_error("Could not auto-detect serial port!")
        SERIAL_PORT = input(f"{Colors.BOLD}Enter serial port (e.g., /dev/cu.usbserial-1420, COM3):{Colors.END} ").strip()

    print_info(f"Using serial port: {SERIAL_PORT}")
    print()

    # Try different upload methods
    uploaders = [
        upload_with_rshell,
        upload_with_ampy,
        upload_with_mpfshell
    ]

    success = False
    for uploader in uploaders:
        if uploader(SERIAL_PORT):
            success = True
            break

    if not success:
        print()
        print_error("All upload methods failed!")
        print()
        print(f"{Colors.BOLD}To upload manually, install one of:{Colors.END}")
        print("  pip install rshell")
        print("  pip install adafruit-ampy")
        print("  pip install mpfshell")
        print()
        print(f"{Colors.BOLD}Then run:{Colors.END}")
        print(f"  rshell --port {SERIAL_PORT} cp main.py /pyboard/main.py")
        print()
        sys.exit(1)

    # Reset ESP32
    print()
    reset_esp32(SERIAL_PORT)

    # Print access instructions
    print_access_instructions()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_info("Upload cancelled.")
        sys.exit(0)
