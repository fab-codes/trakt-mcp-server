"""
Trakt.tv MCP Server

A Model Context Protocol server that provides AI assistants with access to Trakt.tv API,
enabling TV show tracking, watchlist management, and viewing history queries.
"""

import sys
from src.utils.logger import get_logger
from src.server import mcp

logger = get_logger(__name__)

def main() -> None:
    """
    Entry point for the Trakt MCP server.
    
    Usage:
        python -m trakt_mcp_server           # stdio (default)
        python -m trakt_mcp_server --http    # Streamable HTTP on port 8000
    """
    
    try:
        if "--http" in sys.argv:
            logger.info(f"Starting Streamable HTTP server on port 8000...")
            mcp.run(transport="streamable-http")
        else:
            logger.info("Starting stdio server...")
            mcp.run(transport="stdio")
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()