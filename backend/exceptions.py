class SpaceEyeError(Exception):
    """Base exception for SpaceEye application errors."""

    pass


class ProcessingError(SpaceEyeError):
    """Raised when image processing fails."""

    pass


class DownloadError(SpaceEyeError):
    """Raised when band download fails."""

    pass


class ExternalAPIError(SpaceEyeError):
    """Raised when an external API call fails."""

    pass
