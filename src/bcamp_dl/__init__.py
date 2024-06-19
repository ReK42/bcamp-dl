"""Download your collection from Bandcamp."""

from typing import Any

__all__ = []


def export(defn: Any) -> None:  # noqa: ANN401
    """Module-level export decorator."""
    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)  # noqa: PYI056
    return defn


__copyright__ = "Copyright (c) 2023 ReK42"
from bcamp_dl._version import __version__
from bcamp_dl.bcamp_dl import (
    BandcampDownloader,
    MAX_THREADS,
    ALBUM_INFO_KEYS,
    SUPPORTED_BROWSERS,
    SUPPORTED_FILE_FORMATS,
)
