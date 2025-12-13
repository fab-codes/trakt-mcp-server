"""
Trakt.tv MCP Server

A Model Context Protocol server that provides AI assistants with access to Trakt.tv API,
enabling TV show tracking, watchlist management, and viewing history queries.
"""

import asyncio

from src.server import TraktMCPServer
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    """
    Entry point for the Trakt MCP server.

    Initializes and runs the server until interrupted.
    """
    try:
        logger.info("Initializing Trakt MCP Server...")
        server = TraktMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()