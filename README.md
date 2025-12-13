# Trakt MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with access to the Trakt.tv API, enabling TV show tracking, watchlist management, and viewing history queries.

## Features

- **Viewing History**: Retrieve complete watch history of TV shows with episode counts and timestamps
- **Watchlist Management**: Add and remove shows from your personal watchlist
- **Show Search**: Search for TV shows in the Trakt.tv database by title or keywords
- **Trending Shows**: Discover what shows are popular based on community activity
- **MCP Integration**: Works with any Model Context Protocol compatible client
- **Multiple Transports**: Supports both stdio (default) and HTTP Streamable transport

## Available Tools

### `get_watched_shows`
Retrieves the complete watch history of TV shows from Trakt.tv.
- Returns all watched shows with episode counts
- Includes last watched timestamps and total plays
- Shows viewing progress for each series

### `get_watchlist`
Fetches the user's personal Trakt.tv watchlist of TV shows saved for later.
- Returns all shows bookmarked by the user
- Includes metadata (title, year, rating, genres)
- Primary source for personalized recommendations

### `search_shows`
Search for TV shows in the Trakt.tv database by title or keywords.
- Searches Trakt's extensive TV show database
- Returns matching shows with IDs, titles, years, and ratings
- Useful for finding IDs needed for other operations

**Parameters:**
- `query` (required): Search term or show title

### `add_to_watchlist`
Adds a TV show to the user's Trakt.tv watchlist.
- Adds a show to the personal watchlist
- Syncs across all Trakt-connected apps and devices
- Requires authentication (OAuth token)

**Parameters:**
- `show_id` (required): Trakt numeric show ID (obtained from `search_shows`)

### `remove_from_watchlist`
Removes a TV show from the user's Trakt.tv watchlist.
- Removes a show from the watchlist
- Does not affect watch history
- Syncs across all devices

**Parameters:**
- `show_id` (required): Trakt numeric show ID

### `get_trending_shows`
Gets currently trending TV shows on Trakt.tv.
- Returns popular shows based on community activity
- Based on real-time watchers, ratings, and activity
- Updated frequently

**Parameters:**
- `limit` (optional): Number of shows to return (1-20, default: 10)

## Prerequisites

- Python 3.8 or higher
- Trakt.tv account
- Trakt.tv API credentials (Client ID and Access Token)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trakt-mcp-server
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your Trakt credentials:
```env
TRAKT_CLIENT_ID=your_trakt_client_id
TRAKT_ACCESS_TOKEN=your_trakt_access_token
TRAKT_API_VERSION=2
LOG_LEVEL=INFO
```

## Getting Trakt API Credentials

1. Go to [Trakt.tv Applications](https://trakt.tv/oauth/applications)
2. Create a new application
3. Copy the **Client ID**
4. Generate an **Access Token** with appropriate permissions
5. Add both to your `.env` file

## Usage

### Running with stdio transport (default)

```bash
python main.py
```

### Running with HTTP transport

```bash
python main.py --http
```

## Project Structure

```
trakt-mcp-server/
├── main.py                 # Application entry point
├── src/
│   ├── server.py          # Main MCP server implementation
│   ├── api/               # Trakt.tv API client
│   ├── config/            # Configuration management
│   ├── exceptions/        # Custom exceptions
│   ├── formatters/        # Output formatters
│   ├── tools/             # MCP tool definitions
│   └── utils/             # Utility functions and logger
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## MCP Client Integration

This server is compatible with any client that supports the Model Context Protocol. To integrate:

1. Start the server with the desired transport
2. Configure your MCP client to connect to the server
3. The client will have access to all available tools

## Dependencies

- `python-dotenv`: Environment variable management
- `httpx`: Asynchronous HTTP client for API calls
- `mcp`: Model Context Protocol SDK

## Logging

The server includes a configurable logging system. Set the log level in the `.env` file:

```env
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Error Handling

The server handles various types of errors:
- Trakt API errors (authentication, rate limiting, etc.)
- Missing or invalid parameters
- Network errors
- Configuration errors

All errors are logged and returned as user-friendly messages through MCP.