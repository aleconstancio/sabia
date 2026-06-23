class HorusError(Exception):
    """Base exception for Horus application errors."""

    pass


class ProcessingError(HorusError):
    """Raised when image processing fails."""

    pass


class DownloadError(HorusError):
    """Raised when band download fails."""

    pass


class ExternalAPIError(HorusError):
    """Raised when an external API call fails."""

    pass
