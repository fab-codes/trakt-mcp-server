from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """
    Get all available tool definitions for the Trakt MCP server.
    """
    return [
        Tool(
            name="get_watched_shows",
            description=(
                "Retrieves the complete watch history of TV shows from Trakt.tv.\n\n"
                "**What it does:**\n"
                "- Returns all TV shows the user has watched with episode counts\n"
                "- Includes last watched timestamps and total plays\n"
                "- Shows viewing progress for each series\n\n"
                "**When to use:**\n"
                "- User asks 'What shows have I watched?' or 'What series did I finish?'\n"
                "- Before making recommendations (to avoid suggesting already-watched content)\n"
                "- User asks about their viewing history or statistics\n"
                "- Checking if user has seen a specific show\n\n"
                "**Example queries:**\n"
                "- 'What shows have I watched recently?'\n"
                "- 'Have I already seen Breaking Bad?'\n"
                "- 'Show me my watch history'\n\n"
                "**Returns:** JSON array with show titles, years, episode counts, and timestamps."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_watchlist",
            description=(
                "Fetches the user's personal Trakt.tv watchlist of TV shows saved for later.\n\n"
                "**What it does:**\n"
                "- Returns all shows the user has bookmarked to watch\n"
                "- Shows are manually curated by the user (their 'to-watch' list)\n"
                "- Includes show metadata (title, year, rating, genres)\n\n"
                "**When to use:**\n"
                "- User asks 'What should I watch?' or 'Give me recommendations'\n"
                "- ALWAYS check this FIRST before suggesting external recommendations\n"
                "- User mentions 'my list' or 'saved shows' or 'bookmarked series'\n"
                "- User wants to pick from their own curated content\n\n"
                "**Priority:** This should be your PRIMARY source for recommendations!\n"
                "Always prioritize suggesting shows from the user's own watchlist rather than\n"
                "making external recommendations. The user has already expressed interest in these.\n\n"
                "**Example queries:**\n"
                "- 'What should I watch tonight?'\n"
                "- 'What's on my watchlist?'\n"
                "- 'Recommend something from my list'\n\n"
                "**Returns:** JSON array with show titles, years, and when they were added."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="search_shows",
            description=(
                "Search for TV shows in the Trakt.tv database by title or keywords.\n\n"
                "**What it does:**\n"
                "- Searches Trakt's extensive TV show database\n"
                "- Returns matching shows with IDs, titles, years, and ratings\n"
                "- Useful for finding show IDs needed for other operations\n\n"
                "**When to use:**\n"
                "- User mentions a show name without specifics\n"
                "- Need to find a show's Trakt ID for watchlist operations\n"
                "- User asks 'Is there a show called...?'\n"
                "- Looking up show information or verifying title\n\n"
                "**Example queries:**\n"
                "- 'Search for The Office'\n"
                "- 'Find shows about dragons'\n"
                "- 'Is there a show called Dark?'\n\n"
                "**Parameters:**\n"
                "- query (required): Search term or show title\n\n"
                "**Returns:** Top 10 matching shows with IDs for further operations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (show title or keywords)",
                        "minLength": 1
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_to_watchlist",
            description=(
                "Add a TV show to the user's Trakt.tv watchlist for later viewing.\n\n"
                "**What it does:**\n"
                "- Adds a show to the user's personal watchlist\n"
                "- Show will appear in get_watchlist results\n"
                "- Syncs across all Trakt-connected apps and devices\n\n"
                "**When to use:**\n"
                "- User says 'Add [show] to my list' or 'Save this for later'\n"
                "- User wants to bookmark a recommended show\n"
                "- User asks to 'remember' or 'save' a show\n\n"
                "**Important:**\n"
                "- Requires authentication (OAuth token)\n"
                "- You must get the show_id first using search_shows\n"
                "- Use the Trakt numeric ID, not slug or IMDb ID\n\n"
                "**Example workflow:**\n"
                "1. User: 'Add Breaking Bad to my watchlist'\n"
                "2. You: Call search_shows with query='Breaking Bad'\n"
                "3. You: Extract the Trakt ID from results\n"
                "4. You: Call add_to_watchlist with that show_id\n\n"
                "**Parameters:**\n"
                "- show_id (required): Trakt numeric show ID (get from search_shows)\n\n"
                "**Returns:** Confirmation message with number of shows added."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "show_id": {
                        "type": "string",
                        "description": "Trakt show ID (numeric) obtained from search_shows",
                        "pattern": "^[0-9]+$"
                    }
                },
                "required": ["show_id"]
            }
        ),
        Tool(
            name="remove_from_watchlist",
            description=(
                "Remove a TV show from the user's Trakt.tv watchlist.\n\n"
                "**What it does:**\n"
                "- Removes a show from the user's watchlist\n"
                "- Does not affect watch history (only the to-watch list)\n"
                "- Syncs across all devices\n\n"
                "**When to use:**\n"
                "- User says 'Remove [show] from my list' or 'Delete from watchlist'\n"
                "- User wants to clean up their watchlist\n"
                "- User is no longer interested in a saved show\n\n"
                "**Parameters:**\n"
                "- show_id (required): Trakt numeric show ID\n\n"
                "**Returns:** Confirmation message with number of shows removed."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "show_id": {
                        "type": "string",
                        "description": "Trakt show ID (numeric) to remove",
                        "pattern": "^[0-9]+$"
                    }
                },
                "required": ["show_id"]
            }
        ),
        Tool(
            name="get_trending_shows",
            description=(
                "Get currently trending TV shows on Trakt.tv based on community activity.\n\n"
                "**What it does:**\n"
                "- Returns shows that are currently popular on Trakt\n"
                "- Based on real-time watchers, ratings, and activity\n"
                "- Updated frequently based on community engagement\n\n"
                "**When to use:**\n"
                "- User asks 'What's trending?' or 'What are people watching?'\n"
                "- User wants to discover popular current shows\n"
                "- Looking for zeitgeist recommendations\n\n"
                "**Example queries:**\n"
                "- 'What shows are trending right now?'\n"
                "- 'What's popular on TV?'\n"
                "- 'What is everyone watching?'\n\n"
                "**Returns:** Top trending shows with viewer counts and ratings."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of shows to return (1-20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": []
            }
        )
    ]