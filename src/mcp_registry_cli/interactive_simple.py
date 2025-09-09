"""Simple interactive CLI fallback without Rich dependencies."""

import os
import sys
from typing import List, Optional
import time

from .api import MCPRegistryAPI, Server


class SimpleInteractiveCLI:
    """Simple interactive CLI for systems without Rich."""
    
    def __init__(self):
        self.api = MCPRegistryAPI()
        self.current_servers: List[Server] = []
        self.selected_index = 0
        self.search_query = ""
        self.status_filter = ""
        self.current_cursor = None
        self.page_size = 15
        self.running = True
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def display_servers(self):
        """Display the server list in simple format."""
        print("=" * 80)
        print("🚀 MCP Registry Interactive CLI (Simple Mode)")
        print("=" * 80)
        
        if self.search_query:
            print(f"Search: '{self.search_query}'")
        if self.status_filter:
            print(f"Status Filter: {self.status_filter}")
        
        print(f"\nServers ({len(self.current_servers)} found):")
        print("-" * 80)
        
        for i, server in enumerate(self.current_servers):
            marker = "▶" if i == self.selected_index else " "
            status_icon = "🟢" if server.status == "active" else "🔴"
            
            print(f"{marker} {i+1:2}. {status_icon} {server.name}")
            print(f"     Status: {server.status} | Version: {server.version or 'N/A'}")
            print(f"     {server.description[:70]}...")
            print()
        
        print("-" * 80)
        print(f"Selected: {self.selected_index + 1}/{len(self.current_servers)}")
        if self.current_cursor:
            print("More results available (press 'n' for next page)")
        print("🎮 Commands: up/k↑ down/j↓ enter/details i=install s=search f=filter h=help q=quit")
        print("💡 Arrow keys ↑↓ will be detected automatically if pressed")
        
    def show_help(self):
        """Show help information."""
        print("\n" + "=" * 50)
        print("🎮 INTERACTIVE CLI HELP")
        print("=" * 50)
        print("📍 NAVIGATION:")
        print("  k, up, u      - Move selection up")
        print("  j, down, d    - Move selection down") 
        print("  enter, view   - View server details")
        print()
        print("🔧 ACTIONS:")
        print("  i, install    - Install selected server")
        print("  s, search     - Search servers")
        print("  f, filter     - Filter by status")
        print("  c, clear      - Clear filters")
        print()
        print("📄 NAVIGATION:")
        print("  n, next       - Load next page")
        print("  r, refresh    - Refresh server list")
        print("  h, help, ?    - Show this help")
        print("  q, quit, exit - Quit")
        print("=" * 50)
        print("💡 TIP: You can use full words or single letters")
        print("   Example: 'up' or 'k' both move selection up")
        print("=" * 50)
        input("Press Enter to continue...")
        
    def load_servers(self, search: str = "", status: str = "", cursor: str = None):
        """Load servers from API."""
        try:
            if search:
                result = self.api.search_servers(search, cursor=cursor, limit=self.page_size)
            else:
                result = self.api.list_servers(cursor=cursor, limit=self.page_size)
                
            servers = result["servers"]
            
            # Apply status filter if set
            if status:
                servers = [s for s in servers if s.status.lower() == status.lower()]
            
            self.current_servers = servers
            self.current_cursor = result.get("next_cursor")
            self.selected_index = 0
            
        except Exception as e:
            print(f"❌ Error loading servers: {e}")
            self.current_servers = []
    
    def show_server_details(self, server: Server):
        """Show detailed server information."""
        self.clear_screen()
        print("=" * 80)
        print(f"SERVER DETAILS: {server.name}")
        print("=" * 80)
        print(f"Name: {server.name}")
        print(f"Status: {server.status}")
        print(f"Version: {server.version or 'N/A'}")
        print(f"\nDescription:")
        print(server.description)
        
        if server.repository:
            print(f"\nRepository:")
            print(f"  URL: {server.repository.get('url', 'N/A')}")
            print(f"  Type: {server.repository.get('type', 'N/A')}")
        
        if server.packages:
            print(f"\nAvailable Packages:")
            for i, pkg in enumerate(server.packages, 1):
                registry = pkg.get("registry", "N/A")
                package = pkg.get("package", "N/A") 
                version = pkg.get("version", "N/A")
                print(f"  {i}. {registry}: {package} (v{version})")
        
        print("=" * 80)
        input("Press Enter to return to server list...")
    
    def search_servers(self):
        """Interactive search."""
        current = self.search_query or ""
        query = input(f"🔍 Enter search term [{current}]: ").strip()
        if query:
            self.search_query = query
            self.load_servers(search=self.search_query, status=self.status_filter)
        elif not current:
            print("Search cancelled.")
    
    def filter_by_status(self):
        """Interactive status filter."""
        print("📊 Filter by status:")
        print("1. active")
        print("2. inactive") 
        print("3. deprecated")
        print("4. clear filter")
        
        choice = input("Choose (1-4): ").strip()
        
        status_map = {"1": "active", "2": "inactive", "3": "deprecated", "4": ""}
        if choice in status_map:
            self.status_filter = status_map[choice]
            self.load_servers(search=self.search_query, status=self.status_filter)
        else:
            print("Invalid choice.")
    
    def install_server(self, server: Server):
        """Interactive server installation."""
        if not server.packages:
            print(f"❌ No installation packages available for {server.name}")
            input("Press Enter to continue...")
            return
        
        print(f"\n🚀 Installing {server.name}")
        print("Available packages:")
        
        for i, package in enumerate(server.packages, 1):
            registry = package.get("registry", "")
            package_name = package.get("package", "")
            version = package.get("version", "")
            
            if registry == "npm":
                cmd = f"npm install {package_name}"
                if version:
                    cmd += f"@{version}"
            elif registry == "pypi":
                cmd = f"pip install {package_name}"
                if version:
                    cmd += f"=={version}"
            else:
                cmd = f"# Unknown registry: {registry}"
            
            print(f"  {i}. {registry}: {package_name} → {cmd}")
        
        if len(server.packages) == 1:
            choice = "1"
        else:
            choice = input(f"Choose package (1-{len(server.packages)}): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(server.packages):
                package = server.packages[idx]
                registry = package.get("registry", "")
                package_name = package.get("package", "")
                version = package.get("version", "")
                
                if registry == "npm":
                    cmd = f"npm install {package_name}"
                    if version:
                        cmd += f"@{version}"
                elif registry == "pypi":
                    cmd = f"pip install {package_name}"
                    if version:
                        cmd += f"=={version}"
                else:
                    print("❌ Unknown package registry")
                    input("Press Enter to continue...")
                    return
                
                confirm = input(f"Execute: {cmd}? [y/N]: ").strip().lower()
                if confirm == 'y':
                    import subprocess
                    print(f"Executing: {cmd}")
                    try:
                        result = subprocess.run(cmd.split(), capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"✅ Successfully installed {server.name}")
                        else:
                            print(f"❌ Installation failed: {result.stderr}")
                    except Exception as e:
                        print(f"❌ Installation error: {e}")
                else:
                    print("Installation cancelled.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
        
        input("Press Enter to continue...")
    
    def get_single_key(self) -> str:
        """Try to get single key input with better compatibility."""
        # Try different methods in order of preference
        
        # Method 1: Try getch-style input
        try:
            if sys.platform == "win32":
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\xe0':  # Special key prefix
                        key = msvcrt.getch()
                        if key == b'H':
                            return 'k'  # Up arrow
                        elif key == b'P':
                            return 'j'  # Down arrow
                    return key.decode('utf-8').lower()
            else:
                # Unix/Linux/macOS - try termios approach
                import tty, termios
                fd = sys.stdin.fileno()
                
                if os.isatty(fd):
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd, termios.TCSANOW)
                        ch = sys.stdin.read(1)
                        
                        # Handle arrow keys
                        if ch == '\x1b':
                            ch2 = sys.stdin.read(1)
                            if ch2 == '[':
                                ch3 = sys.stdin.read(1)
                                if ch3 == 'A':
                                    return 'k'
                                elif ch3 == 'B':
                                    return 'j'
                                elif ch3 == 'C':
                                    return 'l'
                                elif ch3 == 'D':
                                    return 'h'
                        
                        if ord(ch) == 3:  # Ctrl+C
                            raise KeyboardInterrupt
                        
                        return ch.lower()
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            pass
        
        # Method 2: Try pynput if available (better cross-platform)
        try:
            from pynput import keyboard
            
            print("🎮 Press any key (ESC to enter command mode): ", end="", flush=True)
            
            pressed_key = None
            
            def on_press(key):
                nonlocal pressed_key
                try:
                    if key == keyboard.Key.up:
                        pressed_key = 'k'
                    elif key == keyboard.Key.down:
                        pressed_key = 'j'
                    elif key == keyboard.Key.enter:
                        pressed_key = '\n'
                    elif key == keyboard.Key.esc:
                        pressed_key = 'COMMAND_MODE'
                    elif hasattr(key, 'char') and key.char:
                        pressed_key = key.char.lower()
                    else:
                        pressed_key = str(key).lower()
                except AttributeError:
                    pressed_key = str(key).lower()
                return False  # Stop listener
            
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join(timeout=30)  # 30 second timeout
                
            if pressed_key == 'COMMAND_MODE':
                return self._get_command_input()
            elif pressed_key:
                print(f"'{pressed_key}'")
                return pressed_key
                
        except ImportError:
            pass
        
        # Method 3: Fallback to enhanced command input
        return self._get_enhanced_input()
    
    def _get_enhanced_input(self) -> str:
        """Enhanced command input with better UX."""
        print("\n🎮 Navigation: ", end="", flush=True)
        print("Press: [k]↑ [j]↓ [enter]view [i]install [s]search [h]help [q]quit")
        print("Command: ", end="", flush=True)
        
        try:
            cmd = input().strip().lower()
            
            # Process the command immediately without waiting for another prompt
            if not cmd:
                return 'k'  # Default to up if just Enter pressed
            
            # Handle escape sequences
            if '^[[A' in cmd or '\x1b[A' in cmd:
                return 'k'
            elif '^[[B' in cmd or '\x1b[B' in cmd:
                return 'j'
            
            # Quick mappings
            shortcuts = {
                'k': 'k', 'up': 'k', 'u': 'k',
                'j': 'j', 'down': 'j', 'd': 'j',
                'i': 'i', 'install': 'i',
                's': 's', 'search': 's',
                'h': 'h', 'help': 'h', '?': 'h',
                'q': 'q', 'quit': 'q', 'exit': 'q',
                'n': 'n', 'next': 'n',
                'r': 'r', 'refresh': 'r',
                'f': 'f', 'filter': 'f',
                'c': 'c', 'clear': 'c'
            }
            
            # Check for enter/view commands
            if cmd in ['', 'enter', 'view', 'details', 'show']:
                return '\n'
            
            return shortcuts.get(cmd, cmd)
            
        except (KeyboardInterrupt, EOFError):
            return 'q'
    
    def _get_command_input(self) -> str:
        """Get full command input as fallback."""
        print("\n🎮 Command mode: ", end="", flush=True)
        try:
            cmd = input().lower().strip()
            
            # Handle escape sequences that might come through in fallback mode
            if '\x1b[A' in cmd or cmd == '\x1b[A':
                print("↑ (up arrow detected)", end="", flush=True)
                return 'k'  # Up arrow
            elif '\x1b[B' in cmd or cmd == '\x1b[B':
                print("↓ (down arrow detected)", end="", flush=True)
                return 'j'  # Down arrow
            elif '\x1b[C' in cmd:
                return 'l'  # Right arrow (unused)
            elif '\x1b[D' in cmd:
                return 'h'  # Left arrow (unused)
            
            # Handle raw escape sequences that show up as text
            if '^[[a' in cmd.lower() or '^[[A' in cmd:
                print("↑ (up arrow detected)", end="", flush=True)
                return 'k'  # Up arrow
            elif '^[[b' in cmd.lower() or '^[[B' in cmd:
                print("↓ (down arrow detected)", end="", flush=True) 
                return 'j'  # Down arrow
            
            # Clean up command by removing any escape sequences
            cmd = cmd.replace('^[[A', '').replace('^[[B', '').replace('^[[C', '').replace('^[[D', '')
            cmd = cmd.replace('\x1b[A', '').replace('\x1b[B', '').replace('\x1b[C', '').replace('\x1b[D', '')
            cmd = cmd.strip()
            
            # Map common shortcuts and alternatives
            shortcuts = {
                "up": 'k', "u": 'k', "k": 'k',
                "down": 'j', "d": 'j', "j": 'j',
                "enter": '\n', "details": '\n', "view": '\n', "": '\n',
                "install": 'i', "i": 'i',
                "search": 's', "s": 's', "find": 's',
                "filter": 'f', "f": 'f',
                "clear": 'c', "c": 'c',
                "next": 'n', "n": 'n', "more": 'n',
                "refresh": 'r', "r": 'r', "reload": 'r',
                "help": 'h', "h": 'h', "?": 'h',
                "quit": 'q', "q": 'q', "exit": 'q', "bye": 'q'
            }
            
            return shortcuts.get(cmd, cmd if cmd else 'k')  # Default to 'k' if empty after cleanup
        except (KeyboardInterrupt, EOFError):
            return 'q'
    
    def get_command(self) -> str:
        """Get user command with single-key support."""
        return self.get_single_key()
    
    def run(self):
        """Run the simple interactive CLI."""
        print("🚀 MCP Registry Interactive CLI (Simple Mode)")
        print("💡 Using command-based input for maximum compatibility")
        print("   Type commands like: up, down, enter, install, search, help, quit")
        print("   Or use shortcuts: k, j, i, s, h, q")
        print("\nLoading MCP Registry...")
        self.load_servers()
        
        while self.running:
            self.clear_screen()
            self.display_servers()
            
            if not self.current_servers:
                print("No servers found. Press 'r' to refresh or 'q' to quit.")
            
            cmd = self.get_command()
            
            # Handle commands
            if cmd in ['k', 'up']:
                if self.selected_index > 0:
                    self.selected_index -= 1
            elif cmd in ['j', 'down']:
                if self.selected_index < len(self.current_servers) - 1:
                    self.selected_index += 1
            elif cmd in ['', '\n', '\r', 'enter', 'details']:
                if self.current_servers:
                    server = self.current_servers[self.selected_index]
                    self.show_server_details(server)
            elif cmd == 'i':
                if self.current_servers:
                    server = self.current_servers[self.selected_index]
                    self.install_server(server)
            elif cmd == 's':
                self.search_servers()
            elif cmd == 'f':
                self.filter_by_status()
            elif cmd == 'c':
                self.search_query = ""
                self.status_filter = ""
                self.load_servers()
            elif cmd == 'n':
                if self.current_cursor:
                    self.load_servers(
                        search=self.search_query,
                        status=self.status_filter,
                        cursor=self.current_cursor
                    )
            elif cmd == 'r':
                self.load_servers(search=self.search_query, status=self.status_filter)
            elif cmd == 'h':
                self.show_help()
            elif cmd in ['q', 'quit', 'exit']:
                self.running = False
            else:
                print(f"Unknown command: {cmd}. Press 'h' for help.")
                time.sleep(1)
        
        print("\n👋 Thanks for using MCP Registry CLI!")


def main_simple():
    """Entry point for simple interactive CLI."""
    try:
        cli = SimpleInteractiveCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main_simple()