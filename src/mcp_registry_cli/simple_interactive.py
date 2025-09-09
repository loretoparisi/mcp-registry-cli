"""Simplified interactive CLI that works in any terminal."""

import os
import sys
from typing import List, Optional
import time

from .api import MCPRegistryAPI, Server


class SimpleNavigationCLI:
    """Simple interactive CLI with streamlined navigation."""
    
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
        """Display the server list."""
        print("=" * 80)
        print("🚀 MCP Registry Interactive CLI")
        
        if self.search_query:
            print(f"🔍 Search: '{self.search_query}'")
        if self.status_filter:
            print(f"📊 Status Filter: {self.status_filter}")
            
        print("=" * 80)
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
            print("More results available")
            
        print("\n🎮 Quick Commands:")
        print("  Type: k (up), j (down), enter (view), i (install), s (search), q (quit)")
        print("  Or just press Enter and type full commands like: up, down, help")
    
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
        
        if server.packages:
            print(f"\nAvailable Packages:")
            for i, pkg in enumerate(server.packages, 1):
                registry = pkg.get("registry", "N/A")
                package = pkg.get("package", "N/A") 
                version = pkg.get("version", "N/A")
                print(f"  {i}. {registry}: {package} (v{version})")
        
        print("=" * 80)
    
    def get_command(self) -> str:
        """Get user command with improved interface."""
        print("\n> ", end="", flush=True)
        
        try:
            cmd = input().strip().lower()
            
            # Handle empty input
            if not cmd:
                return 'help'
            
            # Handle arrow key escape sequences
            if '^[[A' in cmd or '\x1b[A' in cmd:
                return 'k'
            elif '^[[B' in cmd or '\x1b[B' in cmd:
                return 'j'
            
            # Clean up any escape sequences
            cmd = cmd.replace('^[[A', '').replace('^[[B', '').replace('^[[C', '').replace('^[[D', '')
            cmd = cmd.replace('\x1b[A', '').replace('\x1b[B', '').replace('\x1b[C', '').replace('\x1b[D', '')
            cmd = cmd.strip()
            
            # Map commands
            command_map = {
                # Navigation
                'k': 'k', 'up': 'k', 'u': 'k',
                'j': 'j', 'down': 'j', 'd': 'j',
                
                # Actions
                'enter': 'enter', 'view': 'enter', 'details': 'enter', 'show': 'enter',
                'i': 'install', 'install': 'install',
                's': 'search', 'search': 'search', 'find': 'search',
                'f': 'filter', 'filter': 'filter',
                'c': 'clear', 'clear': 'clear',
                'n': 'next', 'next': 'next', 'more': 'next',
                'r': 'refresh', 'refresh': 'refresh', 'reload': 'refresh',
                'h': 'help', 'help': 'help', '?': 'help',
                'q': 'quit', 'quit': 'quit', 'exit': 'quit'
            }
            
            return command_map.get(cmd, cmd)
            
        except (KeyboardInterrupt, EOFError):
            return 'quit'
    
    def run(self):
        """Run the simplified interactive CLI."""
        print("🚀 MCP Registry Interactive CLI - Simple Mode")
        print("💡 Optimized for any terminal environment")
        print("\nLoading servers...")
        
        self.load_servers()
        
        while self.running:
            self.clear_screen()
            self.display_servers()
            
            if not self.current_servers:
                print("No servers found. Commands: refresh, search, quit")
            
            cmd = self.get_command()
            
            # Process commands immediately
            if cmd == 'k':  # Up
                if self.selected_index > 0:
                    self.selected_index -= 1
                    
            elif cmd == 'j':  # Down
                if self.selected_index < len(self.current_servers) - 1:
                    self.selected_index += 1
                    
            elif cmd == 'enter':  # View details
                if self.current_servers:
                    server = self.current_servers[self.selected_index]
                    self.show_server_details(server)
                    input("\nPress Enter to continue...")
                    
            elif cmd == 'install':  # Install
                if self.current_servers:
                    server = self.current_servers[self.selected_index]
                    self.install_server(server)
                    
            elif cmd == 'search':  # Search
                query = input("🔍 Enter search term: ").strip()
                if query:
                    self.search_query = query
                    self.load_servers(search=self.search_query, status=self.status_filter)
                    
            elif cmd == 'filter':  # Filter
                print("📊 Filter options: active, inactive, deprecated, clear")
                status = input("Choose status: ").strip().lower()
                if status == 'clear':
                    self.status_filter = ""
                elif status in ['active', 'inactive', 'deprecated']:
                    self.status_filter = status
                self.load_servers(search=self.search_query, status=self.status_filter)
                
            elif cmd == 'clear':  # Clear filters
                self.search_query = ""
                self.status_filter = ""
                self.load_servers()
                
            elif cmd == 'next':  # Next page
                if self.current_cursor:
                    self.load_servers(
                        search=self.search_query,
                        status=self.status_filter,
                        cursor=self.current_cursor
                    )
                    
            elif cmd == 'refresh':  # Refresh
                self.load_servers(search=self.search_query, status=self.status_filter)
                
            elif cmd == 'help':  # Help
                self.show_help()
                
            elif cmd == 'quit':  # Quit
                self.running = False
                
            else:
                print(f"❓ Unknown command: '{cmd}'. Type 'help' for available commands.")
                time.sleep(1)
        
        print("\n👋 Thanks for using MCP Registry CLI!")
    
    def show_help(self):
        """Show help."""
        self.clear_screen()
        print("=" * 50)
        print("🎮 MCP Registry CLI Help")
        print("=" * 50)
        print("NAVIGATION:")
        print("  k, up          - Move selection up")
        print("  j, down        - Move selection down")
        print("  enter, view    - View server details")
        print()
        print("ACTIONS:")
        print("  i, install     - Install selected server")
        print("  s, search      - Search servers")
        print("  f, filter      - Filter by status")
        print("  c, clear       - Clear search/filters")
        print()
        print("SYSTEM:")
        print("  n, next        - Load next page")
        print("  r, refresh     - Refresh server list")
        print("  h, help        - Show this help")
        print("  q, quit        - Exit")
        print("=" * 50)
        print("💡 Just press Enter and type any command!")
        print("💡 Arrow keys may work automatically in some terminals")
        print("=" * 50)
        input("\nPress Enter to continue...")
    
    def install_server(self, server: Server):
        """Install a server."""
        if not server.packages:
            print(f"❌ No packages available for {server.name}")
            input("Press Enter to continue...")
            return
            
        print(f"\n🚀 Installing {server.name}")
        print("Available packages:")
        
        for i, pkg in enumerate(server.packages, 1):
            registry = pkg.get("registry", "")
            package_name = pkg.get("package", "")
            print(f"  {i}. {registry}: {package_name}")
        
        try:
            if len(server.packages) == 1:
                choice = 1
            else:
                choice = int(input(f"Choose package (1-{len(server.packages)}): "))
            
            if 1 <= choice <= len(server.packages):
                pkg = server.packages[choice - 1]
                registry = pkg.get("registry", "")
                package_name = pkg.get("package", "")
                version = pkg.get("version", "")
                
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
                
                confirm = input(f"Execute: {cmd}? (y/N): ")
                if confirm.lower() == 'y':
                    print(f"Run this command: {cmd}")
                    print("(Package installation not implemented in demo mode)")
        except (ValueError, IndexError):
            print("Invalid choice")
        
        input("Press Enter to continue...")


def main():
    """Run the simple interactive CLI."""
    try:
        cli = SimpleNavigationCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()