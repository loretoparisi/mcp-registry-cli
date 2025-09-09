"""Cross-platform keyboard input handling."""

import sys
import os


class KeyboardInput:
    """Handle cross-platform keyboard input."""
    
    @staticmethod
    def get_key():
        """Get a single key press (blocking)."""
        try:
            if sys.platform == "win32":
                # Windows
                import msvcrt
                key = msvcrt.getch()
                if key == b'\xe0':  # Arrow key prefix
                    key = msvcrt.getch()
                    if key == b'H':
                        return 'UP'
                    elif key == b'P':
                        return 'DOWN'
                    elif key == b'K':
                        return 'LEFT' 
                    elif key == b'M':
                        return 'RIGHT'
                return key.decode('utf-8', errors='ignore')
            else:
                # Unix/Linux/macOS
                import tty, termios
                fd = sys.stdin.fileno()
                
                # Must be a TTY
                if not os.isatty(fd):
                    return None
                
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    key = sys.stdin.read(1)
                    
                    # Handle escape sequences (arrow keys)
                    if key == '\x1b':
                        seq = sys.stdin.read(2)
                        if seq == '[A':
                            return 'UP'
                        elif seq == '[B':
                            return 'DOWN'
                        elif seq == '[C':
                            return 'RIGHT'
                        elif seq == '[D':
                            return 'LEFT'
                        else:
                            return 'ESC'
                    
                    # Handle special keys
                    if ord(key) == 3:  # Ctrl+C
                        raise KeyboardInterrupt
                    elif ord(key) == 4:  # Ctrl+D (EOF)
                        raise EOFError
                    elif ord(key) == 13:  # Enter
                        return 'ENTER'
                    elif ord(key) == 27:  # ESC
                        return 'ESC'
                    elif ord(key) == 127:  # Backspace
                        return 'BACKSPACE'
                    
                    return key
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    
        except (ImportError, OSError, termios.error):
            return None
    
    @staticmethod
    def is_available():
        """Check if single-key input is available."""
        try:
            if sys.platform == "win32":
                import msvcrt
                return True
            else:
                import tty, termios
                return os.isatty(sys.stdin.fileno())
        except (ImportError, OSError):
            return False


def test_keyboard_input():
    """Test the keyboard input functionality."""
    kb = KeyboardInput()
    
    print("🧪 Testing Keyboard Input")
    print("=" * 30)
    
    if kb.is_available():
        print("✅ Single-key input is available!")
        print("Press any key (ESC to quit test): ", end="", flush=True)
        
        while True:
            key = kb.get_key()
            if key == 'ESC':
                print("\nExiting test.")
                break
            elif key == 'UP':
                print("\n↑ UP arrow detected")
            elif key == 'DOWN':
                print("\n↓ DOWN arrow detected")
            elif key == 'ENTER':
                print("\n⏎ ENTER detected")
            elif key:
                print(f"\n'{key}' pressed")
            else:
                print("\nNo key detected")
                break
                
            print("Press any key (ESC to quit): ", end="", flush=True)
    else:
        print("❌ Single-key input not available in this environment")
        print("Terminal type:", os.environ.get('TERM', 'unknown'))
        print("TTY check:", os.isatty(sys.stdin.fileno()) if hasattr(sys.stdin, 'fileno') else 'N/A')


if __name__ == "__main__":
    test_keyboard_input()