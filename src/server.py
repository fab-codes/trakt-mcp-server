from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from fastmcp import FastMCP
from src.api import TraktAPIClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AppContext:
    """
    Application context containing lifecycle-scoped resources.
    """
    api_client: TraktAPIClient


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manages the lifecycle of server resources.
    
    Lifecycle phases:
    - Startup: Initializes the Trakt API client (executed once at server start)
    - Runtime: Makes AppContext available to all tools via context
    - Shutdown: Closes connections gracefully (executed once at server stop)
    """
    logger.info("Initializing Trakt API client...")
    api_client = TraktAPIClient()
    
    try:
        # Yield the context - available during entire server lifetime
        yield AppContext(api_client=api_client)
        logger.info("Server is running")
    finally:
        # Cleanup on server shutdown
        logger.info("Cleaning up resources...")
        await api_client.close()
        logger.info("Cleanup complete")


# Create the FastMCP server with lifespan
mcp = FastMCP(
    name="Trakt.tv MCP Server",
    version='0.0.3',
    lifespan=lifespan
)

# Import and register all tools
from src.tools import register_all_tools
register_all_tools(mcp)