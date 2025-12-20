from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from src.formatters import (
    format_search_results,
    format_show_all_episodes,
    format_show_season_episodes,
    format_trending_shows,
)
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
    # GET ALL SHOW EPISODES (ALL SEASONS)
    # ================================================================
    @mcp.tool()
    async def get_show_all_episodes(
        ctx: Context,
        show_id: Annotated[str, Field(
            description="Trakt show ID (numeric) obtained from search_shows",
            pattern=r"^[0-9]+$"
        )]
    ) -> str:
        """
        Retrieve complete episodes overview for all seasons of a TV show.

        **What it does:**
        - Fetches all seasons with their episodes in a comprehensive overview
        - Returns season numbers, episode counts, air dates, and Trakt IDs
        - Shows complete show structure with all seasons and episodes
        - Provides compact view optimized for browsing entire show catalog

        **When to use:**
        - User asks 'What are all the episodes of [show name]?'
        - User wants to see complete show structure
        - User requests 'Show me all Breaking Bad episodes'
        - Looking up complete episode catalog
        - Need overview before diving into specific season

        **Example queries:**
        - 'Show me all episodes of Breaking Bad'
        - 'Get complete episode list for Game of Thrones'
        - 'What episodes are available for The Office?'
        - 'List all Stranger Things episodes'

        **Input:**
        - show_id: Trakt show ID (obtained from search_shows)

        **Output:**
        Returns formatted overview with all seasons, episode numbers, titles, air dates, and IDs.
        Includes episode IDs needed for mark_episode_as_watched tool.
        """
        logger.info(f"Fetching all episodes overview for show ID: {show_id}")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_show_all_episodes(show_id)

        return format_show_all_episodes(data)

    # ================================================================
    # GET SINGLE SEASON EPISODES
    # ================================================================
    @mcp.tool()
    async def get_show_season_episodes(
        ctx: Context,
        show_id: Annotated[str, Field(
            description="Trakt show ID (numeric) obtained from search_shows",
            pattern=r"^[0-9]+$"
        )],
        season: Annotated[int, Field(
            ge=0,
            description="Season number (0=specials, 1+=regular seasons)"
        )]
    ) -> str:
        """
        Retrieve detailed episodes for a specific season of a TV show.

        **What it does:**
        - Fetches detailed episode information for a single season
        - Returns comprehensive episode metadata including ratings
        - Shows detailed view with full episode descriptions
        - Optimized for exploring specific season content

        **When to use:**
        - User asks 'What episodes are in The Office season 3?'
        - User wants detailed information about a specific season
        - User requests 'Show me Breaking Bad S05 episodes'
        - Looking up specific season details before watching
        - Need episode information for a particular season

        **Example queries:**
        - 'What episodes are in The Office season 3?' → season=3
        - 'Show me Breaking Bad season 5 episodes' → season=5
        - 'How many episodes in Stranger Things S01?' → season=1
        - 'Get Game of Thrones season 8 episode list' → season=8

        **Input:**
        - show_id: Trakt show ID (obtained from search_shows)
        - season: Season number (0=specials, 1+=regular seasons)

        **Output:**
        Returns detailed episode information with titles, air dates, ratings, and IDs.
        Includes episode IDs needed for mark_episode_as_watched tool.
        """
        logger.info(f"Fetching detailed episodes for show ID: {show_id}, season {season}")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_show_season_episodes(show_id, season)

        return format_show_season_episodes(data, season)

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