# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-10-01

### Added
- **Live filter mode**: Real-time filtering of servers as you type
  - Press `/` to enter live filter mode
  - Filter servers instantly by name or description
  - No API calls - filters current page locally for blazing-fast results
  - Visual feedback with filter text and result count in header
  - Backspace to edit, Enter to accept, Esc to cancel
  - Integrates seamlessly with existing search and status filters
- Enhanced help panel with live filter instructions
- Filter indicator in status bar showing active live filter

### Changed
- Improved server list management with separate filtered and unfiltered views
- Updated keyboard shortcuts documentation in README

## [0.3.2] - 2025-10-01

### Added
- **Multi-version support**: View and install any version of a server
  - Main list now shows only the latest version of each server
  - Detail page displays all available versions with metadata (version, status, publish date)
  - New 'v' command in detail page to select and install specific versions
  - Version table shows which version is marked as latest with ✓ indicator
- New API method `get_server_versions()` to fetch all versions of a server
- Proper URL encoding for server names with special characters

### Changed
- Main server list filtering now removes duplicate versions, showing only latest
- Detail page enhanced with comprehensive version history display
- Install workflow now supports version selection

### Fixed
- Server name URL encoding in version API calls

## [0.3.1] - 2025-10-01

### Fixed
- Update API client to handle new MCP Registry response format
  - Server data now correctly parsed from nested "server" key
  - Status extracted from `_meta.io.modelcontextprotocol.registry/official.status`
  - Metadata cursor handling updated for camelCase "nextCursor"

## [0.3.0] - 2025-09-11

### Added
- Smart pagination with 30 servers per page
- Interactive navigation with arrow keys and keyboard shortcuts
- Rich terminal UI with colors and tables

## [0.2.3] - 2025-09-10

### Added
- Initial release with basic MCP Registry browsing
- List, search, and filter servers
- View server details
- Basic installation support
