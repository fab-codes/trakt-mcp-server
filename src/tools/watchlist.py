from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from src.formatters import format_watchlist
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_watchlist_tools(mcp: FastMCP) -> None:
    """Register all watchlist tools"""

    # ================================================================
    # ADD TO WATCHLIST
    # ================================================================
    @mcp.tool()
    async def add_to_watchlist(
        ctx: Context,
        show_id: Annotated[str, Field(
            description="Trakt show ID (numeric) obtained from search_shows",
            pattern=r"^[0-9]+$"
        )]
    ) -> str:
        """
        Add a TV show to the user's Trakt.tv watchlist for later viewing.

        **What it does:**
        - Adds a show to the user's personal watchlist
        - Show will appear in get_watchlist results
        - Syncs across all Trakt-connected apps and devices

        **When to use:**
        - User says 'Add [show] to my list' or 'Save this for later'
        - User wants to bookmark a recommended show
        - User asks to 'remember' or 'save' a show

        **Important:**
        - Requires authentication (OAuth token)
        - You must get the show_id first using search_shows
        - Use the Trakt numeric ID, not slug or IMDb ID

        **Example workflow:**
        1. User: 'Add Breaking Bad to my watchlist'
        2. You: Call search_shows with query='Breaking Bad'
        3. You: Extract the Trakt ID from results
        4. You: Call add_to_watchlist with that show_id

        Returns confirmation message with number of shows added.
        """
        logger.info(f"Adding show {show_id} to watchlist...")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.add_to_watchlist(show_id)
        
        added = data.get("added", {}).get("shows", 0)
        return f"✓ Successfully added {added} show(s) to your watchlist."

    # ================================================================
    # REMOVE FROM WATCHLIST
    # ================================================================
    @mcp.tool()
    async def remove_from_watchlist(
        ctx: Context,
        show_id: Annotated[str, Field(
            description="Trakt show ID (numeric) to remove",
            pattern=r"^[0-9]+$"
        )]
    ) -> str:
        """
        Remove a TV show from the user's Trakt.tv watchlist.

        **What it does:**
        - Removes a show from the user's watchlist
        - Does not affect watch history (only the to-watch list)
        - Syncs across all devices

        **When to use:**
        - User says 'Remove [show] from my list' or 'Delete from watchlist'
        - User wants to clean up their watchlist
        - User is no longer interested in a saved show

        Returns confirmation message with number of shows removed.
        """
        logger.info(f"Removing show {show_id} from watchlist...")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.remove_from_watchlist(show_id)
        
        deleted = data.get("deleted", {}).get("shows", 0)
        return f"✓ Successfully removed {deleted} show(s) from your watchlist."

    # ================================================================
    # GET WATCHLIST
    # ================================================================
    @mcp.tool()
    async def get_watchlist(
        ctx: Context
    ) -> str:
        """
        Fetches the user's personal Trakt.tv watchlist of TV shows saved for later.

        **What it does:**
        - Returns all shows the user has bookmarked to watch
        - Shows are manually curated by the user (their 'to-watch' list)
        - Includes show metadata (title, year, rating, genres)

        **When to use:**
        - User asks 'What should I watch?' or 'Give me recommendations'
        - ALWAYS check this FIRST before suggesting external recommendations
        - User mentions 'my list' or 'saved shows' or 'bookmarked series'
        - User wants to pick from their own curated content

        **Priority:** This should be your PRIMARY source for recommendations!
        Always prioritize suggesting shows from the user's own watchlist rather than
        making external recommendations. The user has already expressed interest in these.

        **Example queries:**
        - 'What should I watch tonight?'
        - 'What's on my watchlist?'
        - 'Recommend something from my list'

        Returns JSON array with show titles, years, and when they were added.
        """
        logger.info("Fetching watchlist...")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.get_watchlist()

        return format_watchlist(data)

    # ================================================================
    # MARK AS WATCHED
    # ================================================================
    @mcp.tool()
    async def mark_episode_as_watched(
        ctx: Context,
        episode_id: Annotated[str, Field(
            description="Trakt episode ID (numeric) obtained from get_show_episodes",
            pattern=r"^[0-9]+$"
        )]
    ) -> str:
        """
        Mark a specific TV episode as watched in the user's Trakt.tv history.

        **What it does:**
        - Records the episode as watched with current timestamp
        - Updates user's watch progress for the show
        - Syncs viewing history across all Trakt-connected apps and devices
        - May automatically remove show from watchlist if all episodes are watched

        **When to use:**
        - User says 'Mark [show] episode as watched'
        - User confirms they finished watching an episode
        - User wants to manually update their viewing progress
        - User asks to 'record' or 'log' episode completion

        **Important:**
        - You must get the episode_id first using get_show_episodes
        - Use the Trakt numeric episode ID (not season/episode number)
        - Marking episodes updates show progress statistics

        **Example workflow:**
        1. User: 'Mark Breaking Bad S01E01 as watched'
        2. You: Call get_show_episodes with show_id and season=1
        3. You: Extract the episode ID for episode 1 from results
        4. You: Call mark_episode_as_watched with that episode_id

        Returns confirmation message with number of episodes marked as watched.
        """
        logger.info(f"Marking episode {episode_id} as watched")

        api = ctx.request_context.lifespan_context.api_client
        data = await api.mark_episode_as_watched(episode_id)
        
        added = data.get("added", {}).get("episodes", 0)
        return f"✓ Successfully marked {added} episode(s) as watched."