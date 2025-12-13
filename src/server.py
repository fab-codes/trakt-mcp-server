from typing import Any

from mcp.server import Server
from mcp.server.lowlevel.server import RequestT
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.api import TraktAPIClient
from src.exceptions import TraktAPIError
from src.formatters import (
    format_watched_shows,
    format_watchlist,
    format_search_results,
    format_trending_shows
)
from src.tools import get_tool_definitions
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TraktMCPServer:
    """
    MCP Server for Trakt.tv integration.

    Provides tools for AI assistants to interact with Trakt.tv API,
    including watchlist management, viewing history, and show search.
    """

    def __init__(self) -> None:
        """Initialize the Trakt MCP server with API client and handlers."""
        self.server = Server[dict[str, Any], RequestT]("trakt-mcp-server")
        self.api_client = TraktAPIClient()

        # Register MCP handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)

        logger.info("TraktMCPServer initialized successfully")

    async def list_tools(self) -> list[Tool]:
        """
        List all available tools for the AI assistant.
        """
        return get_tool_definitions()

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """
        Route tool calls to appropriate handlers with error handling.
        """
        logger.info(f"Calling tool: {name} with arguments: {arguments}")

        try:
            # Route to appropriate handler
            if name == "get_watched_shows":
                return await self._handle_get_watched_shows()
            elif name == "get_watchlist":
                return await self._handle_get_watchlist()
            elif name == "search_shows":
                return await self._handle_search_shows(arguments["query"])
            elif name == "add_to_watchlist":
                return await self._handle_add_to_watchlist(arguments["show_id"])
            elif name == "remove_from_watchlist":
                return await self._handle_remove_from_watchlist(arguments["show_id"])
            elif name == "get_trending_shows":
                limit = arguments.get("limit", 10)
                return await self._handle_get_trending_shows(limit)
            else:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]

        except KeyError as e:
            error_msg = f"Missing required parameter: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        except TraktAPIError as e:
            error_msg = f"Trakt API error: {e.message}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception(error_msg)
            return [TextContent(type="text", text=error_msg)]

    # Tool Handlers
    async def _handle_get_watched_shows(self) -> list[TextContent]:
        """Handle get_watched_shows tool call."""
        data = await self.api_client.get_watched_shows()
        formatted_output = format_watched_shows(data)
        return [TextContent(type="text", text=formatted_output)]

    async def _handle_get_watchlist(self) -> list[TextContent]:
        """Handle get_watchlist tool call."""
        data = await self.api_client.get_watchlist()
        formatted_output = format_watchlist(data)
        return [TextContent(type="text", text=formatted_output)]

    async def _handle_search_shows(self, query: str) -> list[TextContent]:
        """Handle search_shows tool call."""
        data = await self.api_client.search_shows(query)
        formatted_output = format_search_results(query, data)
        return [TextContent(type="text", text=formatted_output)]

    async def _handle_add_to_watchlist(self, show_id: str) -> list[TextContent]:
        """Handle add_to_watchlist tool call."""
        data = await self.api_client.add_to_watchlist(show_id)
        added = data.get("added", {}).get("shows", 0)
        message = f"✓ Successfully added {added} show(s) to your watchlist."
        logger.info(message)
        return [TextContent(type="text", text=message)]

    async def _handle_remove_from_watchlist(self, show_id: str) -> list[TextContent]:
        """Handle remove_from_watchlist tool call."""
        data = await self.api_client.remove_from_watchlist(show_id)
        deleted = data.get("deleted", {}).get("shows", 0)
        message = f"✓ Successfully removed {deleted} show(s) from your watchlist."
        logger.info(message)
        return [TextContent(type="text", text=message)]

    async def _handle_get_trending_shows(self, limit: int) -> list[TextContent]:
        """Handle get_trending_shows tool call."""
        data = await self.api_client.get_trending_shows(limit)
        formatted_output = format_trending_shows(data)
        return [TextContent(type="text", text=formatted_output)]

    async def cleanup(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("Cleaning up TraktMCPServer resources")
        await self.api_client.close()

    async def run(self) -> None:
        """Start the MCP server with stdio transport."""
        logger.info("Starting Trakt MCP Server")

        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            await self.cleanup()