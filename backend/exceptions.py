class SabiáError(Exception):
    """Base exception for Sabiá application errors."""

    pass


class ProcessingError(SabiáError):
    """Raised when image processing fails."""

    pass


class DownloadError(SabiáError):
    """Raised when band download fails."""

    pass


class ExternalAPIError(SabiáError):
    """Raised when an external API call fails."""

    pass
