"""Utility functions for MCP Registry CLI."""

from typing import Dict, Any, List
from .api import Server


def format_server_summary(server: Server) -> str:
    """Format a server for summary display."""
    return f"{server.name} ({server.status}) - {server.description[:50]}..."


def filter_servers_by_criteria(servers: List[Server], **criteria) -> List[Server]:
    """Filter servers by various criteria."""
    filtered = servers
    
    if criteria.get("status"):
        filtered = [s for s in filtered if s.status.lower() == criteria["status"].lower()]
    
    if criteria.get("has_packages"):
        filtered = [s for s in filtered if s.packages]
    
    if criteria.get("registry_type"):
        registry_type = criteria["registry_type"].lower()
        filtered = [
            s for s in filtered 
            if s.packages and any(
                pkg.get("registry", "").lower() == registry_type 
                for pkg in s.packages
            )
        ]
    
    return filtered


def get_install_commands(server: Server, package_manager: str = "auto") -> List[str]:
    """Get installation commands for a server."""
    commands = []
    
    if not server.packages:
        return commands
    
    for package in server.packages:
        registry = package.get("registry", "")
        package_name = package.get("package", "")
        version = package.get("version", "")
        
        if registry == "npm" and package_manager in ["npm", "auto"]:
            cmd = f"npm install {package_name}"
            if version:
                cmd += f"@{version}"
            commands.append(cmd)
            
        elif registry == "pypi" and package_manager in ["pip", "auto"]:
            cmd = f"pip install {package_name}"
            if version:
                cmd += f"=={version}"
            commands.append(cmd)
    
    return commands