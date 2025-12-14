from mcp.server.fastmcp import FastMCP

from src.tools.watchlist import register_watchlist_tools
from src.tools.history import register_history_tools
from src.tools.discovery import register_discovery_tools


def register_all_tools(mcp: FastMCP) -> None:
    """Register all tools"""
    register_watchlist_tools(mcp)
    register_history_tools(mcp)
    register_discovery_tools(mcp)