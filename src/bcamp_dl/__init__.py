# -*- coding: utf-8 -*-
"""Download your collection from Bandcamp."""
_name = __name__
_version = "1.0.0"  # https://peps.python.org/pep-0440/
_copyright = "Copyright (c) 2023 ReK42"

__all__ = []


def export(defn):
    """Module-level export decorator."""
    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)
    return defn


from bcamp_dl.bcamp_dl import (
    BandcampDownloader,
    MAX_THREADS,
    ALBUM_INFO_KEYS,
    SUPPORTED_BROWSERS,
    SUPPORTED_FILE_FORMATS,
)
