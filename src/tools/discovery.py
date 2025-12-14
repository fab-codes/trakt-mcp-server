from typing import Annotated
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from pydantic import Field

from src.server import AppContext
from src.formatters import format_search_results, format_trending_shows
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_discovery_tools(mcp: FastMCP) -> None:
    """Register all history tools"""

    # ================================================================
    # SEARCH SHOWS
    # ================================================================
    @mcp.tool()
    async def search_shows(
        query: Annotated[str, Field(
            description="Search query (show title or keywords)",
            min_length=1
        )],
        ctx: Context[ServerSession, AppContext]
    ) -> str:
        """
        Search for TV shows in the Trakt.tv database by title or keywords.

        **What it does:**
        - Searches Trakt's extensive TV show database
        - Returns matching shows with IDs, titles, years, and ratings
        - Useful for finding show IDs needed for other operations

        **When to use:**
        - User mentions a show name without specifics
        - Need to find a show's Trakt ID for watchlist operations
        - User asks 'Is there a show called...?'
        - Looking up show information or verifying title

        **Example queries:**
        - 'Search for The Office'
        - 'Find shows about dragons'
        - 'Is there a show called Dark?'

        Returns top 10 matching shows with IDs for further operations.
        """
        logger.info(f"Searching for: {query}")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.search_shows(query)

        return format_search_results(query, data)

    # ================================================================
    # GET TRENDING SHOWS
    # ================================================================
    @mcp.tool()
    async def get_trending_shows(
        ctx: Context[ServerSession, AppContext],
        limit: Annotated[int, Field(
            default=10,
            ge=1,
            le=20,
            description="Number of shows to return (1-20)"
        )] = 10
    ) -> str:
        """
        Get currently trending TV shows on Trakt.tv based on community activity.

        **What it does:**
        - Returns shows that are currently popular on Trakt
        - Based on real-time watchers, ratings, and activity
        - Updated frequently based on community engagement

        **When to use:**
        - User asks 'What's trending?' or 'What are people watching?'
        - User wants to discover popular current shows
        - Looking for zeitgeist recommendations

        **Example queries:**
        - 'What shows are trending right now?'
        - 'What's popular on TV?'
        - 'What is everyone watching?'

        Returns top trending shows with viewer counts and ratings.
        """
        logger.info(f"Fetching {limit} trending shows...")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_trending_shows(limit)

        return format_trending_shows(data)