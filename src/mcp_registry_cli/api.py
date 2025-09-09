"""API client for MCP Registry."""

import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Server:
    """Represents an MCP server from the registry."""
    name: str
    description: str
    status: str
    version: Optional[str]
    repository: Optional[Dict[str, Any]]
    remotes: Optional[List[Dict[str, Any]]]
    packages: Optional[List[Dict[str, Any]]]
    meta: Optional[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Server":
        """Create Server instance from API response data."""
        # Normalize packages to have consistent field names
        packages = data.get("packages", [])
        if packages:
            normalized_packages = []
            for pkg in packages:
                normalized_pkg = pkg.copy()
                # Map registry_type to registry for backward compatibility
                if "registry_type" in normalized_pkg and "registry" not in normalized_pkg:
                    normalized_pkg["registry"] = normalized_pkg["registry_type"]
                # Map identifier to package for backward compatibility  
                if "identifier" in normalized_pkg and "package" not in normalized_pkg:
                    normalized_pkg["package"] = normalized_pkg["identifier"]
                normalized_packages.append(normalized_pkg)
            packages = normalized_packages
        
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=data.get("status", ""),
            version=data.get("version"),
            repository=data.get("repository"),
            remotes=data.get("remotes"),
            packages=packages,
            meta=data.get("_meta")
        )


class MCPRegistryAPI:
    """Client for interacting with the MCP Registry API."""
    
    BASE_URL = "https://registry.modelcontextprotocol.io"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "mcp-registry-cli/0.1.0"
        })
    
    def list_servers(self, cursor: Optional[str] = None, limit: int = 30) -> Dict[str, Any]:
        """
        List servers from the registry with pagination.
        
        Args:
            cursor: Optional cursor for pagination
            limit: Number of servers to return (default: 30)
            
        Returns:
            Dict containing servers list and pagination info
        """
        url = f"{self.BASE_URL}/v0/servers"
        params = {"limit": limit}
        
        if cursor:
            params["cursor"] = cursor
            
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert server data to Server objects
        servers = [Server.from_dict(server_data) for server_data in data.get("servers", [])]
        
        # Extract metadata
        metadata = data.get("metadata", {})
        
        return {
            "servers": servers,
            "next_cursor": metadata.get("next_cursor"),
            "count": metadata.get("count", len(servers))
        }
    
    def get_server_details(self, server_id: str) -> Server:
        """
        Get detailed information about a specific server.
        
        Args:
            server_id: The server identifier
            
        Returns:
            Server object with detailed information
        """
        url = f"{self.BASE_URL}/v0/servers/{server_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        return Server.from_dict(data)
    
    def search_servers(self, query: str, cursor: Optional[str] = None, limit: int = 30) -> Dict[str, Any]:
        """
        Search servers by name or description.
        
        Args:
            query: Search query string
            cursor: Optional cursor for pagination
            limit: Number of servers to return
            
        Returns:
            Dict containing filtered servers list and pagination info
        """
        query_lower = query.lower()
        filtered_servers = []
        current_cursor = cursor
        fetch_limit = min(max(limit * 2, 30), 30)  # Use smaller batches to avoid API errors
        
        # Keep fetching until we have enough matches or no more data
        while len(filtered_servers) < limit:
            result = self.list_servers(cursor=current_cursor, limit=fetch_limit)
            
            # Filter the current batch
            batch_matches = [
                server for server in result["servers"]
                if query_lower in server.name.lower() or query_lower in server.description.lower()
            ]
            
            filtered_servers.extend(batch_matches)
            
            # Break if no more data available
            if not result.get("next_cursor"):
                break
                
            current_cursor = result["next_cursor"]
        
        # Trim to requested limit
        final_servers = filtered_servers[:limit]
        
        return {
            "servers": final_servers,
            "next_cursor": current_cursor if len(filtered_servers) > limit else None,
            "count": len(final_servers)
        }