"""Command-line interface for MCP Registry."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Optional

from .api import MCPRegistryAPI, Server


console = Console()
api = MCPRegistryAPI()


@click.group()
@click.version_option(version="0.2.0")
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
@click.pass_context
def main(ctx, interactive):
    """MCP Registry CLI - Navigate and manage MCP servers."""
    if interactive:
        from .interactive_main import main as interactive_main
        interactive_main()
        ctx.exit(0)


@main.command()
@click.option("--limit", "-l", default=30, help="Number of servers to display")
@click.option("--cursor", "-c", help="Pagination cursor")
@click.option("--search", "-s", help="Search servers by name or description")
@click.option("--status", help="Filter by status")
@click.option("--sort", type=click.Choice(["name", "status", "description"]), default="name", help="Sort by field")
@click.option("--reverse", is_flag=True, help="Reverse sort order")
def list(limit: int, cursor: Optional[str], search: Optional[str], status: Optional[str], sort: str, reverse: bool):
    """List MCP servers from the registry."""
    try:
        if search:
            result = api.search_servers(search, cursor=cursor, limit=limit)
        else:
            result = api.list_servers(cursor=cursor, limit=limit)
        
        servers = result["servers"]
        
        # Filter by status if specified
        if status:
            servers = [s for s in servers if s.status.lower() == status.lower()]
        
        # Sort servers
        servers.sort(
            key=lambda x: getattr(x, sort, "").lower(),
            reverse=reverse
        )
        
        if not servers:
            console.print("[yellow]No servers found.[/yellow]")
            return
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=False)
        table.add_column("Status", justify="center")
        table.add_column("Version", justify="center")
        table.add_column("Description", style="dim")
        
        for server in servers:
            status_style = {
                "active": "green",
                "inactive": "red",
                "deprecated": "yellow"
            }.get(server.status.lower(), "white")
            
            table.add_row(
                server.name,
                f"[{status_style}]{server.status}[/{status_style}]",
                server.version or "N/A",
                server.description[:80] + "..." if len(server.description) > 80 else server.description
            )
        
        console.print(table)
        
        # Show pagination info
        if result.get("next_cursor"):
            console.print(f"\n[dim]Next cursor: {result['next_cursor']}[/dim]")
            console.print(f"[dim]Use --cursor {result['next_cursor']} to see more results[/dim]")
        
        console.print(f"\n[dim]Showing {len(servers)} servers[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.argument("server_id")
def show(server_id: str):
    """Show detailed information about a specific server."""
    try:
        server = api.get_server_details(server_id)
        
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
        
        console.print(Panel(info_text, title="Server Information", border_style="blue"))
        
        # Repository info
        if server.repository:
            repo_text = Text()
            repo_text.append(f"Type: {server.repository.get('type', 'N/A')}\n", style="cyan")
            repo_text.append(f"URL: {server.repository.get('url', 'N/A')}\n", style="cyan")
            if server.repository.get('ref'):
                repo_text.append(f"Ref: {server.repository.get('ref')}\n", style="cyan")
            
            console.print(Panel(repo_text, title="Repository", border_style="green"))
        
        # Remotes info
        if server.remotes:
            remotes_table = Table(show_header=True, header_style="bold magenta")
            remotes_table.add_column("Type", style="cyan")
            remotes_table.add_column("URL", style="yellow")
            
            for remote in server.remotes:
                remotes_table.add_row(
                    remote.get("type", "N/A"),
                    remote.get("url", "N/A")
                )
            
            console.print(Panel(remotes_table, title="Remote Connections", border_style="yellow"))
        
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
            
            console.print(Panel(packages_table, title="Installation Packages", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.argument("server_id")
@click.option("--package-manager", "-pm", type=click.Choice(["npm", "pip", "auto"]), default="auto", help="Package manager to use")
@click.option("--dry-run", is_flag=True, help="Show installation commands without executing")
def install(server_id: str, package_manager: str, dry_run: bool):
    """Install an MCP server."""
    try:
        server = api.get_server_details(server_id)
        
        if not server.packages:
            console.print(f"[red]No installation packages available for {server.name}[/red]")
            return
        
        console.print(f"[cyan]Installing {server.name}...[/cyan]")
        
        # Show available packages
        packages_table = Table(show_header=True, header_style="bold magenta")
        packages_table.add_column("Registry", style="cyan")
        packages_table.add_column("Package", style="yellow") 
        packages_table.add_column("Command", style="green")
        
        install_commands = []
        
        for package in server.packages:
            registry = package.get("registry", "")
            package_name = package.get("package", "")
            version = package.get("version", "")
            
            if registry == "npm" and package_manager in ["npm", "auto"]:
                cmd = f"npm install {package_name}"
                if version:
                    cmd += f"@{version}"
                install_commands.append(cmd)
                packages_table.add_row("npm", package_name, cmd)
                
            elif registry == "pypi" and package_manager in ["pip", "auto"]:
                cmd = f"pip install {package_name}"
                if version:
                    cmd += f"=={version}"
                install_commands.append(cmd)
                packages_table.add_row("PyPI", package_name, cmd)
        
        if not install_commands:
            console.print(f"[red]No compatible packages found for package manager: {package_manager}[/red]")
            return
        
        console.print(packages_table)
        
        if dry_run:
            console.print("\n[yellow]Dry run - commands that would be executed:[/yellow]")
            for cmd in install_commands:
                console.print(f"  {cmd}")
        else:
            import subprocess
            
            for cmd in install_commands:
                console.print(f"\n[cyan]Executing: {cmd}[/cyan]")
                try:
                    result = subprocess.run(cmd.split(), capture_output=True, text=True)
                    if result.returncode == 0:
                        console.print(f"[green]✓ Successfully installed {server.name}[/green]")
                    else:
                        console.print(f"[red]✗ Installation failed: {result.stderr}[/red]")
                except Exception as e:
                    console.print(f"[red]✗ Installation error: {str(e)}[/red]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
def interactive():
    """Start interactive mode for navigating MCP servers."""
    from .interactive_main import main as interactive_main
    interactive_main()


if __name__ == "__main__":
    main()