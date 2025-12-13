from typing import Any
import httpx
from src.config import AppConfig
from src.exceptions import (
    TraktAPIError,
    AuthenticationError,
    ResourceNotFoundError,
    NetworkError
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# API Constants
TRAKT_API_BASE = "https://api.trakt.tv"
SEARCH_LIMIT = 10

class TraktAPIClient:
    """
    HTTP client for Trakt.tv API interactions.

    Handles authentication, request formation, and error handling.
    """

    def __init__(self) -> None:
        """Initialize the Trakt API client with authentication headers."""
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TraktMCPServer/1.0.0",
                "trakt-api-version": AppConfig.TRAKT_API_VERSION,
                "trakt-api-key": AppConfig.TRAKT_CLIENT_ID,
                "Authorization": f"Bearer {AppConfig.TRAKT_ACCESS_TOKEN}"
            },
            follow_redirects=True
        )

        logger.info("TraktAPIClient initialized successfully")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make an HTTP request to Trakt API with error handling.
        """
        url = f"{TRAKT_API_BASE}{endpoint}"

        try:
            response = await self.http_client.request(method, url, **kwargs)
            response.raise_for_status()

            # Handle empty responses (e.g., 204 No Content)
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError()
            elif e.response.status_code == 404:
                raise ResourceNotFoundError()
            else:
                raise TraktAPIError(
                    f"HTTP {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code
                )
        except httpx.RequestError as e:
            raise NetworkError(str(e))

    async def get_watched_shows(self) -> list[dict[str, Any]]:
        """
        Retrieve the user's watch history from Trakt.
        """
        logger.info("Fetching watched shows")
        return await self._make_request(
            "GET",
            "/sync/watched/shows",
            params={"extended": "full"}
        )

    async def get_watchlist(self) -> list[dict[str, Any]]:
        """
        Retrieve the user's watchlist from Trakt.
        """
        logger.info("Fetching watchlist")
        return await self._make_request(
            "GET",
            "/sync/watchlist/shows",
            params={"extended": "full"}
        )

    async def search_shows(self, query: str) -> list[dict[str, Any]]:
        """
        Search for TV shows by title or keywords.
        """
        logger.info(f"Searching shows with query: {query}")
        return await self._make_request(
            "GET",
            "/search/show",
            params={"query": query, "limit": SEARCH_LIMIT}
        )

    async def add_to_watchlist(self, show_id: str) -> dict[str, Any]:
        """
        Add a show to the user's watchlist.
        """
        logger.info(f"Adding show {show_id} to watchlist")

        payload = {
            "shows": [
                {"ids": {"trakt": int(show_id)}}
            ]
        }

        return await self._make_request("POST", "/sync/watchlist", json=payload)

    async def remove_from_watchlist(self, show_id: str) -> dict[str, Any]:
        """
        Remove a show from the user's watchlist.
        """
        logger.info(f"Removing show {show_id} from watchlist")

        payload = {
            "shows": [
                {"ids": {"trakt": int(show_id)}}
            ]
        }

        return await self._make_request("POST", "/sync/watchlist/remove", json=payload)

    async def get_trending_shows(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get currently trending shows on Trakt.
        """
        logger.info(f"Fetching {limit} trending shows")
        return await self._make_request("GET", f"/shows/trending?limit={limit}")

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        logger.info("Closing TraktAPIClient")
        await self.http_client.aclose()