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

def format_show_all_episodes(seasons: list[dict[str, Any]]) -> str:
    """
    Format all seasons overview with episodes for display.
    """
    if not seasons:
        return "📺 No episodes found for this show."

    # Format all seasons overview
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

    # Format regular seasons
    for season_data in regular_seasons:
        formatted.append(_format_single_season_detail(season_data, season_data.get("number", 0), compact=True))

    # Format specials
    if specials:
        for special_season in specials:
            formatted.append(_format_single_season_detail(
                special_season,
                season_num=0,
                compact=True,
            ))

    return "\n".join(formatted)


def format_show_season_episodes(episodes: list[dict[str, Any]], season_num: int) -> str:
    """
    Format single season episodes with detailed view.
    """
    if not episodes:
        return f"📺 No episodes found for season {season_num}."

    # Calculate metadata from episodes
    aired_count = sum(1 for ep in episodes if ep.get("first_aired"))
    ratings = [ep.get("rating", 0) for ep in episodes if ep.get("rating", 0) > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    season_type = "Specials" if season_num == 0 else f"Season {season_num}"

    formatted = [
        f"📺 **{season_type} Episodes**\n",
        f"**Total:** {len(episodes)} episodes ({aired_count} aired)"
        f"{' • ⭐ ' + f'{avg_rating:.1f}/10' if avg_rating > 0 else ''}\n"
    ]

    for ep in episodes:
        formatted.append(_format_episode_line(ep, season_num, compact=False))

    return "\n".join(formatted)


def _format_single_season_detail(
    season_data: dict[str, Any],
    season_num: int,
    compact: bool = False,
) -> str:
    """
    Format a single season's episodes with flexible styling.

    Args:
        season_data: Single season data from Trakt API
        season_num: Season number for display
        compact: If True, inline format; if False, detailed multi-line format
        max_episodes: Optional limit on number of episodes to show (for specials preview)
    """
    episodes = season_data.get("episodes", [])
    aired_count = season_data.get("aired_episodes", 0)
    rating = season_data.get("rating", 0)

    if not episodes:
        return f"📺 No episodes found for Season {season_num}." if not compact else ""

    season_type = "Specials" if season_num == 0 else f"Season {season_num}"

    if compact:
        # Compact format for overview (inline with other seasons)
        formatted = [
            f"\n**{season_type}** "
            f"({len(episodes)} episodes, {aired_count} aired) "
            f"{'⭐ ' + f'{rating:.1f}/10' if rating > 0 else ''}"
        ]

        for ep in episodes:
            label = "Special" if season_num == 0 else None
            formatted.append(_format_episode_line(ep, season_num, compact=True, label=label))

        return "\n".join(formatted)
    else:
        # Detailed format for single season view
        formatted = [
            f"📺 **{season_type} Episodes**\n",
            f"**Total:** {len(episodes)} episodes ({aired_count} aired)"
            f"{' • ⭐ ' + f'{rating:.1f}/10' if rating > 0 else ''}\n"
        ]

        for ep in episodes:
            formatted.append(_format_episode_line(ep, season_num, compact=False))

        return "\n".join(formatted)


def _format_episode_line(
    episode: dict[str, Any],
    season_num: int,
    compact: bool = True,
    label: str | None = None
) -> str:
    """
    Format a single episode line with consistent styling.
    """
    ep_num = episode.get("number", "?")
    ep_id = episode.get("ids", {}).get("trakt", "N/A")
    title = episode.get("title", "Untitled")
    first_aired = episode.get("first_aired", "")
    air_date = first_aired[:10] if first_aired else "TBA"
    ep_rating = episode.get("rating", 0)

    if compact:
        # Single-line compact format
        prefix = f"  {label} - " if label else f"  {season_num}x{ep_num:02d} - "
        return f"{prefix}**{title}** (aired: {air_date}) • ID: {ep_id}"
    else:
        # Multi-line detailed format
        rating_str = f" • ⭐ {ep_rating:.1f}/10" if ep_rating > 0 else ""
        return (
            f"{season_num}x{ep_num:02d} - **{title}**\n"
            f"  Aired: {air_date}{rating_str}\n"
            f"  Episode ID: {ep_id}"
        )

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