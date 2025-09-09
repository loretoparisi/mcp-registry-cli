# MCP Registry CLI

A command-line interface for navigating and managing servers from the Model Context Protocol (MCP) registry.

## Features

- 🔍 Browse MCP servers with pagination and search
- 📊 Filter and sort servers by status, name, description
- 📋 View detailed server information including packages and repositories
- 📦 Install servers via CLI with npm/pip support
- 🎨 Rich terminal output with colors and tables
- ⌨️  **Interactive CLI mode** with keyboard navigation
- 🔗 Direct access to MCP Registry API

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Recommended: Using Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv mcp-registry-env
source mcp-registry-env/bin/activate  # On Windows: mcp-registry-env\Scripts\activate

# Install the package
pip install mcp-registry-cli
```

### System-wide Installation

```bash
pip install mcp-registry-cli
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/loretoparisi/mcp-registry-cli.git
cd mcp-registry-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Interactive Mode (Recommended)
```bash
# Start interactive CLI with keyboard navigation
mcp-registry-cli

# Alternative ways to start interactive mode
mcp-registry --interactive
mcp-registry interactive
```

**Interactive Controls:**
- `↑/↓` or `k/j` - Navigate servers
- `Enter` - View server details  
- `i` - Install server
- `s` - Search servers
- `f` - Filter by status
- `h` - Help panel
- `q` - Quit

### Command Line Mode
```bash
# List first 10 servers
mcp-registry list --limit 10

# Search for GitHub-related servers
mcp-registry list --search github

# Show detailed information about a server
mcp-registry show io.github.domdomegg/airtable-mcp-server

# Preview installation commands
mcp-registry install io.github.domdomegg/airtable-mcp-server --dry-run

# Install a server (requires appropriate package manager)
mcp-registry install io.github.domdomegg/airtable-mcp-server
```

## Command Reference

### List Servers
```bash
mcp-registry list [OPTIONS]

Options:
  --limit INTEGER         Number of servers to display (default: 30)
  --cursor TEXT          Pagination cursor for next page
  --search TEXT          Search servers by name or description
  --status TEXT          Filter by status (active, inactive, deprecated)
  --sort [name|status|description]  Sort by field (default: name)
  --reverse              Reverse sort order
```

### Show Server Details
```bash
mcp-registry show <server-name>

Example:
mcp-registry show ai.waystation/gmail
```

### Install Server
```bash
mcp-registry install <server-name> [OPTIONS]

Options:
  --package-manager [npm|pip|auto]  Package manager to use (default: auto)
  --dry-run                        Show commands without executing
```

## Examples

### Explore the Registry
```bash
# List all active servers
mcp-registry list --status active

# Find database-related servers
mcp-registry list --search database --limit 5

# Browse with pagination
mcp-registry list --limit 10
# Use the cursor from output for next page
mcp-registry list --cursor <next-cursor>
```

### Get Server Information
```bash
# View comprehensive server details
mcp-registry show com.pga/pga-golf

# Check available installation packages
mcp-registry show io.github.DeanWard/HAL
```

### Install Servers
```bash
# Preview installation
mcp-registry install xcodebuildmcp --dry-run

# Install with specific package manager
mcp-registry install hal-mcp --package-manager npm

# Auto-detect and install
mcp-registry install reddit-research-mcp
```

## Programmatic Usage

```python
from mcp_registry_cli.api import MCPRegistryAPI

# Initialize API client
api = MCPRegistryAPI()

# List servers
result = api.list_servers(limit=10)
for server in result['servers']:
    print(f"{server.name}: {server.description}")

# Get server details
server = api.get_server_details("ai.waystation/gmail")
print(f"Status: {server.status}")
if server.packages:
    print("Available packages:")
    for pkg in server.packages:
        print(f"  - {pkg.get('registry')}: {pkg.get('package')}")

# Search servers
result = api.search_servers("github", limit=5)
print(f"Found {len(result['servers'])} GitHub-related servers")
```

## Troubleshooting

### Virtual Environment Issues
If you encounter permission errors, ensure you're using a virtual environment:
```bash
python3 -m venv mcp-registry-env
source mcp-registry-env/bin/activate
pip install --upgrade pip
pip install mcp-registry-cli
```

### Package Installation
If server installation fails, check that you have the required package manager:
- **npm servers**: Ensure Node.js and npm are installed
- **pip servers**: Ensure Python and pip are available
- Use `--dry-run` to preview commands before execution

### API Issues
If you encounter API errors:
- Check your internet connection
- The MCP Registry API may be temporarily unavailable
- Try reducing the `--limit` parameter

## Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/loretoparisi/mcp-registry-cli.git
cd mcp-registry-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Development Commands
```bash
# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/

# Test CLI locally
python3 -m src.mcp_registry_cli.cli --help
```

## Requirements

- Python 3.8+
- click >= 8.0.0
- requests >= 2.25.0
- rich >= 12.0.0
- tabulate >= 0.9.0

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### License Summary
- ✅ Free to use for commercial and non-commercial purposes
- ✅ Modify and distribute as needed  
- ✅ Include in your own projects
- ✅ Must include copyright notice

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**Loreto Parisi** - [loretoparisi@gmail.com](mailto:loretoparisi@gmail.com)

## Acknowledgments

- Built for the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) ecosystem
- Uses the official MCP Registry API
- Powered by [Rich](https://github.com/Textualize/rich) for beautiful terminal output