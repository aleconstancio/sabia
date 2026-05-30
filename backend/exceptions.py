class SpaceEyeError(Exception):
    pass


class ImageNotFoundError(SpaceEyeError):
    pass


class ProcessingError(SpaceEyeError):
    pass


class DownloadError(SpaceEyeError):
    pass


class InvalidPolygonError(SpaceEyeError):
    pass


class CollectionNotFoundError(SpaceEyeError):
    pass
