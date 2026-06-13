class SpaceEyeError(Exception):
    """Base exception for SpaceEye application errors."""
    pass


class ProcessingError(SpaceEyeError):
    """Raised when image processing fails."""
    pass


class DownloadError(SpaceEyeError):
    """Raised when band download fails."""
    pass


class ValidationError(SpaceEyeError):
    """Raised when input validation fails."""
    pass


class ExternalAPIError(SpaceEyeError):
    """Raised when an external API call fails."""
    pass


class NotFoundError(SpaceEyeError):
    """Raised when a requested resource is not found."""
    pass
