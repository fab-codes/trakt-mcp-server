from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import AppConfig
from src.exceptions import (
    AuthenticationError,
    NetworkError,
    ResourceNotFoundError,
    TraktAPIError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# API Constants
TRAKT_API_BASE = "https://api.trakt.tv"
SEARCH_LIMIT = 10


class TraktAPIClient:
    """
    HTTP client for Trakt.tv API interactions.

    - HTTP/2 multiplexing
    - Connection pooling
    - Automatic retries with exponential backoff
    - Comprehensive timeout configuration
    """

    def __init__(self) -> None:
        """Initialize the Trakt API client with advanced configuration."""

        # Configure timeouts
        timeout = httpx.Timeout(
            connect=5.0,  # Connection timeout
            read=30.0,  # Read timeout
            write=10.0,  # Write timeout
            pool=5.0,  # Pool timeout
        )

        # Configure connection pooling
        limits = httpx.Limits(
            max_connections=100,  # Total connections
            max_keepalive_connections=20,  # Keep-alive connections
            keepalive_expiry=30.0,  # Keep-alive timeout
        )

        # Initialize HTTP client with HTTP/2 support
        self.http_client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TraktMCPServer/0.0.3",
                "trakt-api-version": AppConfig.TRAKT_API_VERSION,
                "trakt-api-key": AppConfig.TRAKT_CLIENT_ID,
                "Authorization": f"Bearer {AppConfig.TRAKT_ACCESS_TOKEN}",
            },
            follow_redirects=True,
            http2=True,
        )

        logger.info("TraktAPIClient initialized successfully")

    @retry(
        # Retry on network errors only (not on client errors like 4xx)
        retry=retry_if_exception_type(NetworkError),
        # Stop after 3 attempts
        stop=stop_after_attempt(3),
        # Exponential backoff: 2s, 4s, 8s
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # Reraise the exception after all retries exhausted
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Make an HTTP request to Trakt API
        """
        url = f"{TRAKT_API_BASE}{endpoint}"

        try:
            logger.debug(f"Making {method} request to {endpoint}")

            response = await self.http_client.request(method, url, **kwargs)
            response.raise_for_status()

            # Log HTTP/2 usage for monitoring
            if hasattr(response, "http_version"):
                logger.debug(f"HTTP version: {response.http_version}")

            # Handle empty responses (e.g., 204 No Content)
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except httpx.HTTPStatusError as e:
            # Client errors (4xx) - don't retry
            if e.response.status_code == 401:
                logger.error("Authentication failed - check TRAKT_ACCESS_TOKEN")
                raise AuthenticationError()

            elif e.response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                raise ResourceNotFoundError()

            elif e.response.status_code == 429:
                logger.warning(f"Rate limited on {endpoint}")
                raise TraktAPIError(
                    "Rate limit exceeded. Please try again later.",
                    status_code=429,
                )

            else:
                logger.error(
                    f"HTTP {e.response.status_code} error on {endpoint}: "
                    f"{e.response.text[:200]}"
                )
                raise TraktAPIError(
                    f"HTTP {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code
                )

        except httpx.TimeoutException as e:
            # Network timeout - retryable
            logger.warning(f"Request timeout on {endpoint}: {e}")
            raise NetworkError(f"Request timeout: {e}")

        except httpx.ConnectError as e:
            # Connection error - retryable
            logger.warning(f"Connection error on {endpoint}: {e}")
            raise NetworkError(f"Connection failed: {e}")

        except httpx.RequestError as e:
            # Other network errors - retryable
            logger.warning(f"Request error on {endpoint}: {e}")
            raise NetworkError(str(e))

    # ========================================================================
    # WATCH HISTORY ENDPOINTS
    # ========================================================================

    async def get_watched_shows(self) -> list[dict[str, Any]]:
        """
        Retrieve the user's watch history from Trakt.

        Returns:
            List of watched shows with metadata
        """
        logger.info("Fetching watched shows")
        result = await self._make_request(
            "GET", "/sync/watched/shows", params={"extended": "full"}
        )
        return result if isinstance(result, list) else []

    # ========================================================================
    # WATCHLIST ENDPOINTS
    # ========================================================================

    async def get_watchlist(self) -> list[dict[str, Any]]:
        """
        Retrieve the user's watchlist from Trakt.

        Returns:
            List of watchlist shows with metadata
        """
        logger.info("Fetching watchlist")
        result = await self._make_request(
            "GET", "/sync/watchlist/shows", params={"extended": "full"}
        )
        return result if isinstance(result, list) else []

    async def add_to_watchlist(self, show_id: str) -> dict[str, Any]:
        """
        Add a show to the user's watchlist.

        Returns:
            API response with added count
        """
        logger.info(f"Adding show {show_id} to watchlist")

        payload = {"shows": [{"ids": {"trakt": int(show_id)}}]}

        result = await self._make_request("POST", "/sync/watchlist", json=payload)
        return result if isinstance(result, dict) else {}

    async def remove_from_watchlist(self, show_id: str) -> dict[str, Any]:
        """
        Remove a show from the user's watchlist.

        Returns:
            API response with deleted count
        """
        logger.info(f"Removing show {show_id} from watchlist")

        payload = {"shows": [{"ids": {"trakt": int(show_id)}}]}

        result = await self._make_request(
            "POST", "/sync/watchlist/remove", json=payload
        )
        return result if isinstance(result, dict) else {}

    # ========================================================================
    # DISCOVERY ENDPOINTS
    # ========================================================================

    async def search_shows(self, query: str) -> list[dict[str, Any]]:
        """
        Search for TV shows by title or keywords.

        Returns:
            List of matching shows
        """
        logger.info(f"Searching shows with query: '{query[:50]}'")  # Truncate for logs
        result = await self._make_request(
            "GET", "/search/show", params={"query": query, "limit": SEARCH_LIMIT}
        )
        return result if isinstance(result, list) else []

    async def get_trending_shows(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get currently trending shows on Trakt.

        Returns:
            List of trending shows
        """
        logger.info(f"Fetching {limit} trending shows")
        result = await self._make_request("GET", f"/shows/trending?limit={limit}")
        return result if isinstance(result, list) else []

    # ========================================================================
    # EPISODES ENDPOINTS
    # ========================================================================

    async def get_show_all_episodes(self, show_id: str) -> list[dict[str, Any]]:
        """
        Get all seasons with episodes overview for a show.

        Returns:
            List of seasons with episodes
        """
        logger.info(f"Fetching all seasons overview for show {show_id}")
        result = await self._make_request(
            "GET", f"/shows/{show_id}/seasons", params={"extended": "episodes"}
        )
        return result if isinstance(result, list) else []

    async def get_show_season_episodes(
        self, show_id: str, season: int
    ) -> list[dict[str, Any]]:
        """
        Get detailed episodes for a specific season.

        Returns:
            List of episodes in the season
        """
        logger.info(f"Fetching detailed episodes for show {show_id}, season {season}")
        result = await self._make_request(
            "GET", f"/shows/{show_id}/seasons/{season}", params={"extended": "min"}
        )
        return result if isinstance(result, list) else []

    async def mark_episode_as_watched(self, episode_id: str) -> dict[str, Any]:
        """
        Mark an episode as watched.

        Returns:
            API response with added count
        """
        logger.info(f"Marking episode {episode_id} as watched")

        payload = {"episodes": [{"ids": {"trakt": int(episode_id)}}]}

        result = await self._make_request("POST", "/sync/history", json=payload)
        return result if isinstance(result, dict) else {}

    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================

    async def close(self) -> None:
        """
        Close the HTTP client and cleanup resources.
        """
        logger.info("Closing TraktAPIClient and releasing connections")
        await self.http_client.aclose()
