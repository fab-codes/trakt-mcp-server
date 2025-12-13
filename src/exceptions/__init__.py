class TraktAPIError(Exception):
    """Exception raised when Trakt API requests fail."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(TraktAPIError):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication required. Please configure TRAKT_ACCESS_TOKEN."):
        super().__init__(message, status_code=401)


class ResourceNotFoundError(TraktAPIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found on Trakt"):
        super().__init__(message, status_code=404)


class NetworkError(TraktAPIError):
    """Exception raised when network requests fail."""

    def __init__(self, message: str):
        super().__init__(f"Network error: {message}", status_code=None)