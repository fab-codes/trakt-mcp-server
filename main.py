"""
Trakt.tv MCP Server

A Model Context Protocol server that provides AI assistants with access to Trakt.tv API,
enabling TV show tracking, watchlist management, and viewing history queries.
"""

import asyncio
from src.server import TraktMCPServer
from src.utils.logger import get_logger
import sys

logger = get_logger(__name__)

def main() -> None:
    """
    Entry point for the Trakt MCP server.
    Initializes and runs the server until interrupted.
    Supports both stdio and Streamable HTTP transports.
    """
    try:
        logger.info("Initializing Trakt MCP Server...")
        
        # Check transport type
        if "--http" in sys.argv:
            run_http()
        else:
            run_stdio()
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise

def run_stdio() -> None:
    """Run the server with stdio transport (default)"""
    logger.info("Starting stdio server...")
    server = TraktMCPServer()
    asyncio.run(server.run())

def run_http() -> None:
    """Run the server with Streamable HTTP transport"""
    logger.info("Starting http server...")

if __name__ == "__main__":
    main()