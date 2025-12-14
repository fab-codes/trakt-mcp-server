from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP
from src.api import TraktAPIClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AppContext:
    """Used in all tools with lifespan"""
    api_client: TraktAPIClient


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manages the lifecycle of resources:
    - Startup: initializes the API client
    - Shutdown: closes the connections
    """
    logger.info("Initializing Trakt API client...")
    api_client = TraktAPIClient()
    
    try:
        yield AppContext(api_client=api_client)
    finally:
        logger.info("Cleaning up resources...")
        await api_client.close()


# Crea il server FastMCP con lifespan
mcp = FastMCP(
    name="Trakt.tv MCP Server/1.0.0",
    lifespan=lifespan
)


# Import and register all tools
from src.tools import register_all_tools
register_all_tools(mcp)