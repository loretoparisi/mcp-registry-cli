"""Interactive CLI interface for MCP Registry."""

import os
import sys
from typing import List, Optional, Dict, Any
import time

# Check for required dependencies
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich.progress import track
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .api import MCPRegistryAPI, Server


class InteractiveCLI:
    """Interactive CLI for navigating MCP Registry."""
    
    def __init__(self):
        self.console = Console()
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
        
    def create_header(self) -> Panel:
        """Create the header panel."""
        title_text = Text()
        title_text.append("🚀 MCP Registry Interactive CLI", style="bold cyan")
        
        status_text = Text()
        status_text.append(f"Servers: {len(self.current_servers)} | ", style="dim")
        if self.search_query:
            status_text.append(f"Search: '{self.search_query}' | ", style="yellow")
        if self.status_filter:
            status_text.append(f"Status: {self.status_filter} | ", style="green")
        status_text.append("Press 'h' for help", style="dim")
        
        header_content = Text()
        header_content.append(title_text)
        header_content.append("\n")
        header_content.append(status_text)
        
        return Panel(header_content, title="MCP Registry", border_style="blue")
    
    def create_server_table(self) -> Table:
        """Create the server list table."""
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("", width=3)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=False, min_width=30)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Version", justify="center", width=8)
        table.add_column("Description", style="dim", no_wrap=False)
        
        for i, server in enumerate(self.current_servers):
            # Selection indicator
            indicator = "▶" if i == self.selected_index else " "
            
            # Status styling
            status_style = {
                "active": "green",
                "inactive": "red", 
                "deprecated": "yellow"
            }.get(server.status.lower(), "white")
            
            # Truncate description
            desc = server.description
            if len(desc) > 60:
                desc = desc[:57] + "..."
            
            # Highlight selected row
            if i == self.selected_index:
                table.add_row(
                    f"[bold yellow]{indicator}[/bold yellow]",
                    f"[bold white]{server.name}[/bold white]",
                    f"[bold {status_style}]{server.status}[/bold {status_style}]",
                    f"[bold white]{server.version or 'N/A'}[/bold white]",
                    f"[bold white]{desc}[/bold white]"
                )
            else:
                table.add_row(
                    indicator,
                    server.name,
                    f"[{status_style}]{server.status}[/{status_style}]",
                    server.version or "N/A",
                    desc
                )
        
        return table
    
    def create_help_panel(self) -> Panel:
        """Create the help panel."""
        help_text = Text()
        help_text.append("Navigation:\n", style="bold")
        help_text.append("↑/↓ or k/j   - Navigate servers\n")
        help_text.append("Enter        - View server details\n") 
        help_text.append("i            - Install selected server\n")
        help_text.append("s            - Search servers\n")
        help_text.append("f            - Filter by status\n")
        help_text.append("c            - Clear filters\n")
        help_text.append("n            - Load next page\n")
        help_text.append("r            - Refresh server list\n")
        help_text.append("h            - Show/hide help\n")
        help_text.append("q            - Quit\n")
        
        return Panel(help_text, title="Help", border_style="green")
    
    def create_layout(self, show_help: bool = False) -> Layout:
        """Create the main layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="main")
        )
        
        layout["header"].update(self.create_header())
        
        if show_help:
            layout["main"].split_row(
                Layout(name="servers", ratio=2),
                Layout(name="help", ratio=1)
            )
            layout["servers"].update(self.create_server_table())
            layout["help"].update(self.create_help_panel())
        else:
            layout["main"].update(self.create_server_table())
        
        return layout
    
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
            self.console.print(f"[red]Error loading servers: {e}[/red]")
            self.current_servers = []
    
    def show_server_details(self, server: Server):
        """Show detailed server information."""
        self.clear_screen()
        
        # Main info panel
        info_text = Text()
        info_text.append(f"Name: {server.name}\n", style="bold cyan")
        info_text.append(f"Status: ", style="bold")
        
        status_style = {
            "active": "green",
            "inactive": "red",
            "deprecated": "yellow"
        }.get(server.status.lower(), "white")
        info_text.append(f"{server.status}\n", style=status_style)
        
        if server.version:
            info_text.append(f"Version: {server.version}\n", style="bold")
        
        info_text.append(f"\nDescription:\n{server.description}", style="white")
        
        self.console.print(Panel(info_text, title="Server Information", border_style="blue"))
        
        # Repository info
        if server.repository:
            repo_text = Text()
            repo_text.append(f"Type: {server.repository.get('url', 'N/A')}\n", style="cyan")
            repo_text.append(f"URL: {server.repository.get('url', 'N/A')}\n", style="cyan")
            if server.repository.get('ref'):
                repo_text.append(f"Ref: {server.repository.get('ref')}\n", style="cyan")
            
            self.console.print(Panel(repo_text, title="Repository", border_style="green"))
        
        # Packages info
        if server.packages:
            packages_table = Table(show_header=True, header_style="bold magenta")
            packages_table.add_column("Registry", style="cyan")
            packages_table.add_column("Package", style="yellow")
            packages_table.add_column("Version", style="green")
            
            for package in server.packages:
                packages_table.add_row(
                    package.get("registry", "N/A"),
                    package.get("package", "N/A"),
                    package.get("version", "N/A")
                )
            
            self.console.print(Panel(packages_table, title="Installation Packages", border_style="cyan"))
        
        # Controls
        self.console.print("\n[dim]Press any key to return to server list...[/dim]")
        
        # Wait for key press
        try:
            input()
        except KeyboardInterrupt:
            pass
    
    def search_servers(self):
        """Interactive search."""
        query = Prompt.ask("🔍 Enter search term", default=self.search_query)
        if query != self.search_query:
            self.search_query = query
            self.load_servers(search=self.search_query, status=self.status_filter)
    
    def filter_by_status(self):
        """Interactive status filter."""
        status = Prompt.ask(
            "📊 Filter by status",
            choices=["active", "inactive", "deprecated", "clear", ""],
            default=self.status_filter or "active"
        )
        
        if status == "clear" or status == "":
            self.status_filter = ""
        else:
            self.status_filter = status
            
        self.load_servers(search=self.search_query, status=self.status_filter)
    
    def install_server(self, server: Server):
        """Interactive server installation."""
        if not server.packages:
            self.console.print(f"[red]No installation packages available for {server.name}[/red]")
            input("Press any key to continue...")
            return
        
        self.console.print(f"[cyan]Installing {server.name}...[/cyan]")
        
        # Show available packages
        packages_table = Table(show_header=True, header_style="bold magenta")
        packages_table.add_column("Option", style="cyan")
        packages_table.add_column("Registry", style="yellow") 
        packages_table.add_column("Package", style="green")
        packages_table.add_column("Command", style="dim")
        
        install_options = []
        for i, package in enumerate(server.packages):
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
            
            install_options.append(cmd)
            packages_table.add_row(str(i + 1), registry, package_name, cmd)
        
        self.console.print(packages_table)
        
        # Get user choice
        if len(install_options) == 1:
            choice = "1"
        else:
            choice = Prompt.ask(
                f"Choose package to install (1-{len(install_options)})",
                choices=[str(i) for i in range(1, len(install_options) + 1)]
            )
        
        selected_cmd = install_options[int(choice) - 1]
        
        # Confirm installation
        if Confirm.ask(f"Execute: [bold]{selected_cmd}[/bold]?"):
            try:
                import subprocess
                self.console.print(f"[cyan]Executing: {selected_cmd}[/cyan]")
                
                result = subprocess.run(selected_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    self.console.print(f"[green]✓ Successfully installed {server.name}[/green]")
                else:
                    self.console.print(f"[red]✗ Installation failed: {result.stderr}[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]✗ Installation error: {str(e)}[/red]")
        
        input("Press any key to continue...")
    
    def get_key_input(self) -> str:
        """Get single key input (cross-platform) with better fallback."""
        try:
            # Try to import getch for single key input
            if sys.platform == "win32":
                import msvcrt
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':
                        return 'k'  # Up arrow
                    elif key == b'P':
                        return 'j'  # Down arrow
                return key.decode('utf-8').lower()
            else:
                # Unix/Linux/macOS
                try:
                    import tty, termios
                    fd = sys.stdin.fileno()
                    
                    # Check if stdin is a tty
                    if not os.isatty(fd):
                        return self._smart_input()
                        
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(fd, termios.TCSANOW)  # Use setraw instead of cbreak
                        ch = sys.stdin.read(1)
                        
                        # Handle arrow keys (escape sequences)
                        if ch == '\x1b':  # ESC sequence
                            ch2 = sys.stdin.read(1)
                            if ch2 == '[':
                                ch3 = sys.stdin.read(1)
                                if ch3 == 'A':
                                    return 'k'  # Up arrow
                                elif ch3 == 'B':
                                    return 'j'  # Down arrow
                                elif ch3 == 'C':
                                    return 'l'  # Right arrow (unused)
                                elif ch3 == 'D':
                                    return 'h'  # Left arrow (unused)
                        
                        # Handle Ctrl+C
                        if ord(ch) == 3:
                            raise KeyboardInterrupt
                        
                        return ch.lower()
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except (ImportError, AttributeError, OSError, termios.error):
                    # Fallback for systems without tty support
                    return self._smart_input()
        except Exception:
            return self._smart_input()
    
    def _smart_input(self) -> str:
        """Smart input method that works well without single-key input."""
        self.console.print("\n[cyan]Command:[/cyan] ", end="")
        
        try:
            user_input = input().lower().strip()
            
            # Handle empty input
            if not user_input:
                return 'h'  # Show help if empty
            
            # Handle escape sequences that might come through
            if '^[[A' in user_input or '\x1b[A' in user_input:
                return 'k'  # Up arrow
            elif '^[[B' in user_input or '\x1b[B' in user_input:
                return 'j'  # Down arrow
            
            # Clean up escape sequences
            user_input = user_input.replace('^[[A', '').replace('^[[B', '')
            user_input = user_input.replace('\x1b[A', '').replace('\x1b[B', '')
            user_input = user_input.strip()
            
            # Map full words to single characters
            command_map = {
                'up': 'k', 'k': 'k', 'u': 'k',
                'down': 'j', 'j': 'j', 'd': 'j', 
                'enter': '\n', 'details': '\n', 'view': '\n',
                'install': 'i', 'i': 'i',
                'search': 's', 's': 's', 'find': 's',
                'filter': 'f', 'f': 'f',
                'clear': 'c', 'c': 'c',
                'next': 'n', 'n': 'n', 'more': 'n',
                'refresh': 'r', 'r': 'r', 'reload': 'r',
                'help': 'h', 'h': 'h', '?': 'h',
                'quit': 'q', 'q': 'q', 'exit': 'q'
            }
            
            return command_map.get(user_input, user_input if user_input else 'h')
                    
        except (KeyboardInterrupt, EOFError):
            return 'q'
    
    def run(self):
        """Run the interactive CLI."""
        self.console.print("[bold cyan]🚀 Loading MCP Registry...[/bold cyan]")
        
        # Initial load
        self.load_servers()
        
        show_help = False
        
        try:
            while self.running:
                self.clear_screen()
                layout = self.create_layout(show_help)
                self.console.print(layout)
                
                if not self.current_servers:
                    self.console.print("[yellow]No servers found. Press 'r' to refresh or 'q' to quit.[/yellow]")
                
                # Status bar
                status_line = f"[dim]Selected: {self.selected_index + 1}/{len(self.current_servers)} | "
                if self.current_cursor:
                    status_line += "More available (press 'n') | "
                status_line += "Press 'h' for help[/dim]"
                self.console.print(status_line)
                
                # Get user input
                key = self.get_key_input()
                
                # Handle navigation
                if key in ['k', '\x1b[A']:  # Up arrow or k
                    if self.selected_index > 0:
                        self.selected_index -= 1
                elif key in ['j', '\x1b[B']:  # Down arrow or j  
                    if self.selected_index < len(self.current_servers) - 1:
                        self.selected_index += 1
                elif key in ['\r', '\n']:  # Enter
                    if self.current_servers:
                        server = self.current_servers[self.selected_index]
                        self.show_server_details(server)
                elif key == 'i':  # Install
                    if self.current_servers:
                        server = self.current_servers[self.selected_index]
                        self.install_server(server)
                elif key == 's':  # Search
                    self.search_servers()
                elif key == 'f':  # Filter
                    self.filter_by_status()
                elif key == 'c':  # Clear filters
                    self.search_query = ""
                    self.status_filter = ""
                    self.load_servers()
                elif key == 'n':  # Next page
                    if self.current_cursor:
                        self.load_servers(
                            search=self.search_query,
                            status=self.status_filter,
                            cursor=self.current_cursor
                        )
                elif key == 'r':  # Refresh
                    self.load_servers(search=self.search_query, status=self.status_filter)
                elif key == 'h':  # Help
                    show_help = not show_help
                elif key == 'q':  # Quit
                    self.running = False
                
                # Small delay to prevent flickering
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            pass
        
        self.console.print("\n[cyan]Thanks for using MCP Registry CLI! 👋[/cyan]")


def main():
    """Entry point for interactive CLI."""
    if not RICH_AVAILABLE:
        print("⚠️  Rich library not available. Using simple interactive mode...")
        print("For better experience, install: pip install rich")
        
        # Fall back to simple interactive CLI
        from .interactive_simple import main_simple
        main_simple()
        return
        
    try:
        cli = InteractiveCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()