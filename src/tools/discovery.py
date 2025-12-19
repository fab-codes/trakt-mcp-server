from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from fastmcp.server.context import Context  

from src.formatters import format_search_results, format_trending_shows, format_show_episodes
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_discovery_tools(mcp: FastMCP) -> None:
    """Register all history tools"""

    # ================================================================
    # SEARCH SHOWS
    # ================================================================
    @mcp.tool()
    async def search_shows(
        ctx: Context,
        query: Annotated[str, Field(
            description="Search query (show title or keywords)",
            min_length=1
        )]
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
    # GET SHOW EPISODES
    # ================================================================
    @mcp.tool()
    async def get_show_episodes(
        ctx: Context,
        show_id: Annotated[str, Field(
            description="Trakt show ID (numeric) obtained from search_shows",
            pattern=r"^[0-9]+$"
        )]
    ) -> str:
        """
        Retrieve all episodes for a specific TV show organized by season.

        **What it does:**
        - Fetches complete season and episode breakdown for a show
        - Returns episode numbers, titles, air dates, and IDs
        - Provides detailed metadata for each episode in the series
        - Uses Trakt's extended episodes parameter for comprehensive data

        **When to use:**
        - User asks 'What are the episodes of [show name]?'
        - Need to see complete episode list for a series
        - User wants season/episode information
        - Looking up specific episode details or air dates
        - Building watch progress tracking

        **Example queries:**
        - 'Show me all episodes of Breaking Bad'
        - 'What episodes are in The Office season 3?'
        - 'Get episode list for Game of Thrones'
        - 'How many episodes does Stranger Things have?'

        **Input:**
        - Requires a valid Trakt show ID (obtained from search_shows)
        - Accepts both numeric IDs (e.g., '1390') or slugs (e.g., 'game-of-thrones')

        **Output:**
        Returns structured data with seasons, episode numbers, titles, and metadata.
        """
        logger.info(f"Fetching episodes for show ID: {show_id}")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_show_episodes(show_id)

        return format_show_episodes(data)


    # ================================================================
    # GET TRENDING SHOWS
    # ================================================================
    @mcp.tool()
    async def get_trending_shows(
        ctx: Context,
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