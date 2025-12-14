# Trakt MCP Server

A production-ready Model Context Protocol (MCP) server that provides AI assistants with seamless access to the [Trakt.tv](https://trakt.tv) API, enabling intelligent TV show tracking, watchlist management, and personalized viewing recommendations.

## Features

- **Watch History Tracking**: Complete viewing history with episode counts, timestamps, and progress tracking
- **Smart Watchlist Management**: Add, remove, and organize shows across all your devices
- **Advanced Show Discovery**: Powerful search with Trakt's extensive database and trending shows
- **Dual Transport Support**: Production-ready HTTP (Streamable) and development-friendly stdio modes
- **Async Architecture**: Built with FastMCP and httpx for high-performance async operations
- **Lifecycle Management**: Automatic resource initialization and cleanup with async context managers
- **Comprehensive Error Handling**: Detailed exception hierarchy for authentication, network, and API errors
- **Structured Logging**: Configurable logging system for monitoring and debugging

## Architecture

### Project Structure

```
trakt-mcp-server/
├── main.py                      # Application entry point with transport selection
├── src/
│   ├── server.py               # FastMCP server with lifespan management
│   ├── api/
│   │   └── __init__.py         # TraktAPIClient with async HTTP operations
│   ├── config/
│   │   └── __init__.py         # Configuration management and validation
│   ├── exceptions/
│   │   └── __init__.py         # Custom exception hierarchy
│   ├── formatters/
│   │   └── __init__.py         # Output formatters for tool responses
│   ├── tools/
│   │   ├── __init__.py         # Tool registration system
│   │   ├── history.py          # Watch history tools
│   │   ├── watchlist.py        # Watchlist management tools
│   │   └── discovery.py        # Search and trending tools
│   └── utils/
│       └── logger.py           # Structured logging configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
└── README.md                  # This file
```

### Core Components

- **FastMCP Server**: Leverages FastMCP for declarative tool registration and automatic type validation
- **Async API Client**: httpx-based client with connection pooling and automatic retries
- **Lifespan Context**: Ensures proper resource initialization and cleanup across server lifecycle
- **Tool Categories**: Organized into history, watchlist, and discovery modules for maintainability

## Available Tools

### History Tools

#### `get_watched_shows`
Retrieves complete watch history with detailed viewing statistics.

**Returns:**
- All watched TV shows with episode counts
- Last watched timestamps and total plays
- Viewing progress for each series
- Formatted JSON response

**Use Cases:**
- "What shows have I watched recently?"
- "Have I already seen Breaking Bad?"
- Recommendation filtering (avoid suggesting watched content)

---

### Watchlist Tools

#### `get_watchlist`
Fetches the user's curated watchlist - the primary source for personalized recommendations.

**Returns:**
- All bookmarked shows with metadata
- Title, year, rating, genres
- Timestamp when added to watchlist

**Use Cases:**
- "What should I watch tonight?"
- "Show me my saved shows"
- Priority recommendations from user's own list

#### `add_to_watchlist`
Adds a TV show to the user's watchlist with cross-device sync.

**Parameters:**
- `show_id` (string, required): Trakt numeric ID from `search_shows`
  - Pattern: `^[0-9]+$` (validated)

**Returns:** Confirmation with number of shows added

**Workflow:**
1. Call `search_shows` to find the show
2. Extract Trakt ID from results
3. Call `add_to_watchlist` with that ID

**Requirements:** OAuth access token with watchlist permissions

#### `remove_from_watchlist`
Removes a show from the watchlist without affecting watch history.

**Parameters:**
- `show_id` (string, required): Trakt numeric ID

**Returns:** Confirmation with number of shows removed

---

### Discovery Tools

#### `search_shows`
Search Trakt's extensive database by title or keywords.

**Parameters:**
- `query` (string, required): Search term (min length: 1)

**Returns:**
- Top 10 matching shows
- Trakt IDs, titles, years, ratings
- Score-sorted results

**Use Cases:**
- "Search for The Office"
- Finding show IDs for watchlist operations
- "Is there a show called Dark?"

#### `get_trending_shows`
Get real-time trending shows based on community activity.

**Parameters:**
- `limit` (integer, optional): Number of results (1-20, default: 10)

**Returns:**
- Currently popular shows
- Viewer counts and ratings
- Real-time community engagement data

**Use Cases:**
- "What's trending right now?"
- "What are people watching?"
- Zeitgeist recommendations

## Prerequisites

- **Python 3.8+** (recommended: 3.11+ for optimal async performance)
- **Trakt.tv account** (free registration at [trakt.tv](https://trakt.tv))
- **Trakt API credentials** (Client ID and OAuth Access Token)

## Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd trakt-mcp-server
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `mcp` - FastMCP framework for MCP server implementation
- `httpx` - High-performance async HTTP client for Trakt API
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation (dependency of FastMCP)

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required: Trakt API Credentials
TRAKT_CLIENT_ID=your_trakt_client_id_here
TRAKT_ACCESS_TOKEN=your_oauth_access_token_here
TRAKT_API_VERSION=2

# Optional: Logging Configuration
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Getting Trakt API Credentials

### Step-by-Step Guide

1. **Create Application**
   - Navigate to [Trakt.tv Applications](https://trakt.tv/oauth/applications)
   - Click "New Application"
   - Fill in application details (name, description, redirect URI)

2. **Get Client ID**
   - Copy the **Client ID** from your application page
   - Add to `.env` as `TRAKT_CLIENT_ID`

3. **Generate Access Token**
   - In your application settings, generate an OAuth token
   - Required permissions: `public`, `read`, `write` (for watchlist management)
   - Copy the generated token
   - Add to `.env` as `TRAKT_ACCESS_TOKEN`

4. **Verify Configuration**
   ```bash
   python -c "from src.config import AppConfig; print('✓ Configuration valid')"
   ```

## Usage

### Transport Modes

The server supports two transport protocols optimized for different use cases:

#### stdio Transport (Development)

Best for local development and MCP client integrations (Claude Desktop, etc.)

```bash
python main.py
```

**Characteristics:**
- Each client gets dedicated process
- Input/output via standard streams
- Ideal for single-user local development
- Default mode when no flags specified

#### Streamable HTTP Transport (Production)

Recommended for production deployments and network access

```bash
python main.py --http
```

**Characteristics:**
- Full bidirectional communication via HTTP
- Multiple concurrent client support
- Server runs on `0.0.0.0:8000`
- Supports streaming responses
- Production-grade scalability

**Connection:**
```
HTTP Endpoint: http://localhost:8000
Protocol: Streamable HTTP (MCP standard)
```

### Running as Module

```bash
# stdio mode
python -m trakt_mcp_server

# HTTP mode
python -m trakt_mcp_server --http
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TRAKT_CLIENT_ID` | Yes | - | Trakt API Client ID |
| `TRAKT_ACCESS_TOKEN` | Yes | - | OAuth Access Token |
| `TRAKT_API_VERSION` | Yes | `2` | Trakt API version |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

### API Client Configuration

The TraktAPIClient is configured in [src/api/__init__.py](src/api/__init__.py):

```python
httpx.AsyncClient(
    timeout=30.0,           # Request timeout
    follow_redirects=True,   # Auto-follow redirects
    headers={
        "Content-Type": "application/json",
        "User-Agent": "TraktMCPServer/1.0.0",
        "trakt-api-version": "2",
        "trakt-api-key": TRAKT_CLIENT_ID,
        "Authorization": f"Bearer {TRAKT_ACCESS_TOKEN}"
    }
)
```

## MCP Client Integration

### Supported Clients

This server implements the [Model Context Protocol](https://modelcontextprotocol.io/) and works with any compatible client:

- **Custom MCP Clients** - Any client implementing MCP specification
- **Development Tools** - MCP Inspector, testing frameworks

### Integration Steps

**1. Start the Server**
```bash
# For local MCP clients
python main.py

# For network-accessible deployment
python main.py --http
```

**2. Configure Client**

For stdio transport (Claude Desktop example):
```json
{
  "mcpServers": {
    "trakt": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/path/to/trakt-mcp-server",
      "env": {
        "TRAKT_CLIENT_ID": "your_client_id",
        "TRAKT_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

For HTTP transport:
```json
{
  "mcpServers": {
    "trakt": {
      "url": "http://localhost:8000",
      "transport": "streamable-http"
    }
  }
}
```

**3. Available Tools**

Once connected, the client has access to all 6 tools:
- `get_watched_shows`
- `get_watchlist`
- `add_to_watchlist`
- `remove_from_watchlist`
- `search_shows`
- `get_trending_shows`

## Logging

### Configuration

Set logging level via environment variable:

```env
LOG_LEVEL=DEBUG    # Maximum verbosity
LOG_LEVEL=INFO     # Standard operations (default)
LOG_LEVEL=WARNING  # Warnings and errors only
LOG_LEVEL=ERROR    # Errors only
LOG_LEVEL=CRITICAL # Critical failures only
```

### Log Output

The logger ([src/utils/logger.py](src/utils/logger.py)) provides structured output:

```
2025-01-15 14:30:22 [INFO] src.server: Initializing Trakt API client...
2025-01-15 14:30:22 [INFO] src.api: TraktAPIClient initialized successfully
2025-01-15 14:30:23 [INFO] main: Starting stdio server...
```

### Debug Mode

For troubleshooting, enable debug logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

Provides detailed information:
- HTTP request/response details
- API endpoint calls
- Tool invocation parameters
- Exception stack traces

## Error Handling

### Exception Hierarchy

The server implements a comprehensive error handling system ([src/exceptions/__init__.py](src/exceptions/__init__.py)):

```python
TraktAPIError               # Base exception
├── AuthenticationError     # 401 - Invalid credentials
├── ResourceNotFoundError   # 404 - Show/resource not found
└── NetworkError           # Connection/timeout errors
```

### Error Responses

All errors are:
1. **Logged** with full context and stack traces
2. **Formatted** as user-friendly messages
3. **Returned** through MCP protocol to client

**Example:**

```python
# Invalid credentials
AuthenticationError: "Invalid Trakt credentials. Check TRAKT_ACCESS_TOKEN."

# Network timeout
NetworkError: "Failed to connect to Trakt API. Check network connection."

# Show not found
ResourceNotFoundError: "Show ID 99999999 not found in Trakt database."
```

### Automatic Retries

The httpx client automatically handles:
- Connection pooling
- Redirect following
- Timeout management (30s default)

## Development

### Code Organization

```
src/
├── server.py          # FastMCP server + lifespan management
├── api/              # API client layer
├── config/           # Configuration + validation
├── exceptions/       # Custom exception types
├── formatters/       # Response formatting logic
├── tools/            # MCP tool definitions (modular)
│   ├── history.py    # Watch history tools
│   ├── watchlist.py  # Watchlist management
│   └── discovery.py  # Search + trending
└── utils/            # Logging utilities
```

### Adding New Tools

Tools are registered using FastMCP decorators:

```python
@mcp.tool()
async def my_new_tool(
    ctx: Context[ServerSession, AppContext],
    param: Annotated[str, Field(description="Parameter description")]
) -> str:
    """
    Tool description for AI assistant.

    Detailed explanation of what the tool does.
    """
    api = ctx.request_context.lifespan_context.api_client
    result = await api.my_api_method(param)
    return format_result(result)
```

Register in [src/tools/__init__.py](src/tools/__init__.py):

```python
def register_all_tools(mcp: FastMCP) -> None:
    register_watchlist_tools(mcp)
    register_history_tools(mcp)
    register_discovery_tools(mcp)
    register_my_new_tools(mcp)  # Add this
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow existing code style and patterns
4. Add tests for new functionality
5. Submit a pull request