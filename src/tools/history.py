from typing import Annotated
from fastmcp import Context, FastMCP
from pydantic import Field

from src.formatters import format_show_progress, format_watched_shows
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_history_tools(mcp: FastMCP) -> None:
    """Register all history tools"""

    # ================================================================
    # GET WATCHED SHOWS
    # ================================================================
    @mcp.tool()
    async def get_watched_shows(
        ctx: Context
    ) -> str:
        """
        Retrieves the complete watch history of TV shows from Trakt.tv.

        **What it does:**
        - Returns all TV shows the user has watched with episode counts
        - Includes last watched timestamps and total plays
        - Shows viewing progress for each series

        **When to use:**
        - User asks 'What shows have I watched?' or 'What series did I finish?'
        - Before making recommendations (to avoid suggesting already-watched content)
        - User asks about their viewing history or statistics
        - Checking if user has seen a specific show

        **Example queries:**
        - 'What shows have I watched recently?'
        - 'Have I already seen Breaking Bad?'
        - 'Show me my watch history'

        Returns JSON array with show titles, years, episode counts, and timestamps.
        """
        logger.info("Fetching watched shows...")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_watched_shows()

        return format_watched_shows(data)

    # ================================================================
    # GET SHOW PROGRESS
    # ================================================================
    @mcp.tool()
    async def get_show_progress(
        ctx: Context,
        show_id: Annotated[str, Field(
            description="Trakt show ID (numeric) obtained from search_shows",
            pattern=r"^[0-9]+$"
        )]
    ) -> str:
        """
        Retrieves the watch progress for a specific TV show from Trakt.tv.

        **What it does:**
        - Returns detailed progress information for a single show
        - Shows which episodes have been watched and which are pending
        - Includes information about the next episode to watch
        - Provides season-by-season progress breakdown

        **When to use:**
        - User asks about their progress on a specific show (e.g., 'Where am I in The Bear?')
        - User wants to know which episode to watch next
        - Checking completion status of a particular series
        - User asks 'What episode am I on?' for a specific show

        **Example queries:**
        - 'What episode am I on in Demon Slayer?'
        - 'How far am I into The Bear?'
        - 'What's the next episode I need to watch?'
        - 'Am I caught up with Pluribus?'

        **Note:** Requires OAuth authentication with user's Trakt account.

        Returns dictionary with show progress details and episode information.
        """
        logger.info(f"Fetching progress for show {show_id}")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_show_progress(show_id)

        return format_show_progress(data)