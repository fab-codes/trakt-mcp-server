from fastmcp import Context, FastMCP

from src.formatters import format_watched_shows
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