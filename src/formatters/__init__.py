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

def format_show_episodes(seasons: list[dict[str, Any]]) -> str:
    """
    Format show episodes organized by season for display.
    """
    if not seasons:
        return "📺 No episodes found for this show."

    regular_seasons = [s for s in seasons if s.get("number", 0) > 0]
    specials = [s for s in seasons if s.get("number", 0) == 0]

    if not regular_seasons and not specials:
        return "📺 No episodes available for this show yet."

    total_episodes = sum(len(s.get("episodes", [])) for s in regular_seasons)
    total_aired = sum(s.get("aired_episodes", 0) for s in regular_seasons)

    formatted = [
        f"📺 **Show Episodes Overview**\n",
        f"**Total:** {len(regular_seasons)} season{'s' if len(regular_seasons) != 1 else ''} • "
        f"{total_episodes} episodes ({total_aired} aired)\n"
    ]

    for season_data in regular_seasons:
        season_num = season_data.get("number", 0)
        episodes = season_data.get("episodes", [])
        aired_count = season_data.get("aired_episodes", 0)
        rating = season_data.get("rating", 0)

        formatted.append(
            f"\n**Season {season_num}** "
            f"({len(episodes)} episodes, {aired_count} aired) "
            f"{'⭐ ' + f'{rating:.1f}/10' if rating > 0 else ''}"
        )

        for ep in episodes:
            ep_num = ep.get("number", "?")
            title = ep.get("title", "Untitled")
            first_aired = ep.get("first_aired", "")
            air_date = first_aired[:10] if first_aired else "TBA"
            ep_trakt_id = ep.get("ids").get("trakt")

            formatted.append(
                f"  {season_num}x{ep_num:02d} - **{title}** "
                f"(aired: {air_date})"
                f"• ID: {ep_trakt_id}"
            )

    if specials:
        for special_season in specials:
            episodes = special_season.get("episodes", [])
            if episodes:
                formatted.append(f"\n**Specials** ({len(episodes)} episodes)")
                for ep in episodes[:5]:  # Show max 5 specials
                    title = ep.get("title", "Untitled")
                    first_aired = ep.get("first_aired", "")
                    air_date = first_aired[:10] if first_aired else "TBA"
                    formatted.append(f"  Special - **{title}** (aired: {air_date})")

                if len(episodes) > 5:
                    formatted.append(f"  ... and {len(episodes) - 5} more specials")

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