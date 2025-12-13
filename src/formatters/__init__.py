from typing import Any


def format_watched_shows(shows: list[dict[str, Any]]) -> str:
    """
    Format watched shows for display.
    """
    if not shows:
        return "📺 No watched shows found in your history."

    formatted = [f"📺 **Watch History** (Total: {len(shows)} shows)\n"]

    for item in shows:
        show = item.get("show", {})
        title = show.get("title", "Unknown")
        year = show.get("year", "N/A")

        # Get number of seasons watched
        seasons = item.get("seasons", [])
        seasons_count = len(seasons) if seasons else 0

        # Get last watched date
        last_watched = item.get("last_watched_at", "N/A")
        last_date = last_watched[:10] if last_watched != "N/A" else "N/A"

        formatted.append(
            f"• **{title}** ({year}) — {seasons_count} seasons • Last: {last_date}"
        )

    return "\n".join(formatted)


def format_watchlist(watchlist: list[dict[str, Any]]) -> str:
    """
    Format watchlist for display.
    """
    if not watchlist:
        return "📝 Your watchlist is empty. Add shows you want to watch later!"

    formatted = [f"📝 **Your Watchlist** (Total: {len(watchlist)} shows)\n"]

    for item in watchlist:
        show = item.get("show", {})
        title = show.get("title", "Unknown")
        year = show.get("year", "N/A")

        # Get number of aired episodes (from extended metadata)
        aired_episodes = show.get("aired_episodes", 0)

        # Get when it was added to watchlist
        added_at = item.get("listed_at", "")
        added_date = added_at[:10] if added_at else "N/A"

        formatted.append(
            f"• **{title}** ({year}) — {aired_episodes} episodes • Added: {added_date}"
        )

    return "\n".join(formatted)


def format_search_results(query: str, results: list[dict[str, Any]]) -> str:
    """
    Format search results for display.
    """
    if not results:
        return f"🔍 No shows found matching '{query}'"

    formatted = [f"🔍 **Search Results for '{query}'** (Top {len(results)} matches)\n"]

    for item in results:
        show = item.get("show", {})
        trakt_id = show.get("ids", {}).get("trakt")
        year = show.get("year", "N/A")
        rating = show.get("rating", 0)

        formatted.append(
            f"• **{show.get('title')}** ({year}) "
            f"— ⭐ {rating:.1f}/10 • ID: {trakt_id}"
        )

    return "\n".join(formatted)


def format_trending_shows(trending: list[dict[str, Any]]) -> str:
    """
    Format trending shows for display.
    """
    if not trending:
        return "📈 No trending shows available at the moment."

    formatted = [f"📈 **Trending Shows** (Top {len(trending)})\n"]

    for idx, item in enumerate(trending, 1):
        show = item.get("show", {})
        watchers = item.get("watchers", 0)
        year = show.get("year", "N/A")

        formatted.append(
            f"{idx}. **{show.get('title')}** ({year}) "
            f"— 👥 {watchers:,} watchers"
        )

    return "\n".join(formatted)