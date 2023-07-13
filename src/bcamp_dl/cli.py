#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download your collection from Bandcamp."""
import os
import sys

from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from pathlib import Path

from bcamp_dl import (
    _name,
    _version,
    _copyright,
    BandcampDownloader,
    MAX_THREADS,
    ALBUM_INFO_KEYS,
    SUPPORTED_BROWSERS,
    SUPPORTED_FILE_FORMATS,
)


def int_positive(arg: str) -> int:
    """Validate an integer is positive."""
    try:
        i = int(arg)
    except ValueError:
        raise ArgumentTypeError("Must be an integer")
    if i < 0:
        raise ArgumentTypeError("Integer must be positive")
    return i


def float_positive(arg: str) -> float:
    """Validate a float is positive."""
    try:
        f = float(arg)
    except ValueError:
        raise ArgumentTypeError("Must be a float")
    if f < 0:
        raise ArgumentTypeError("Float must be positive")
    return f


def num_threads(arg: str) -> int:
    """Validate an given number of threads is supported."""
    try:
        i = int(arg)
    except ValueError:
        raise ArgumentTypeError("Must be an integer")
    if i < 0:
        raise ArgumentTypeError("Integer must be positive")
    if i > MAX_THREADS:
        raise ArgumentTypeError(f"Integer must be <= {MAX_THREADS}")
    return i


def path_is_writable_file(arg: str) -> Path:
    """Validate that a path is a writable file."""
    try:
        p = Path(arg)
    except ValueError:
        raise ArgumentTypeError("Must be a path")
    if p.exists():
        if not p.is_file():
            raise ArgumentTypeError("Path exists but is not a file")
        if os.access(p, os.W_OK):
            raise ArgumentTypeError("Path exists but it not writable")
    else:
        if not p.parent.is_dir():
            raise ArgumentTypeError(
                "File does not exist and parent directory does not exist"
            )
        if not os.access(p.parent, os.W_OK):
            raise ArgumentTypeError(
                "File does not exist and parent directory is not writable"
            )
    return p


def main() -> None:
    """Script entry point."""
    parser = ArgumentParser(
        prog=_name,
        add_help=False,
        description=(
            "Download your collection from Bandcamp.\n"
            "\n"
            "To use, login to Bandcamp using one of the supported browsers. All albums"
            " in your collection will be downloaded to the output directory, with"
            " subfolders, based on the filename format selected."
        ),
        epilog="",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "username", type=str, metavar="USERNAME", help="Bandcamp username"
    )
    parser.add_argument(
        "-b",
        "--browser",
        type=str,
        metavar="BROWSER",
        default="firefox",
        choices=SUPPORTED_BROWSERS,
        help=(
            "Browser used to login to Bandcamp, default: %(default)s\n"
            + "Supported browsers: "
            + ", ".join(SUPPORTED_BROWSERS)
        ),
    )
    parser.add_argument(
        "-c",
        "--cookie-path",
        type=str,
        metavar="FILE",
        help="Path to cookies.txt, if no browser was used",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        metavar="DIR",
        default=Path("."),
        help="Directory to download to, default: %(default)s",
    )
    parser.add_argument(
        "-f",
        "--file-format",
        type=str,
        metavar="FORMAT",
        default="mp3-v0",
        choices=SUPPORTED_FILE_FORMATS,
        help=(
            "File format to download, default: %(default)s\n"
            + "Supported formats: "
            + ", ".join(SUPPORTED_FILE_FORMATS)
        ),
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=num_threads,
        metavar="INT",
        default=4,
        help="Number of download threads to spawn, default: %(default)s",
    )
    parser.add_argument(
        "-p",
        "--pause",
        type=float_positive,
        metavar="FLOAT",
        default=1.0,
        help="Pause between successful downloads, default: %(default)s",
    )
    parser.add_argument(
        "-m",
        "--max-retries",
        type=int_positive,
        metavar="INT",
        default=5,
        help="Maximum number of failed download attempts, default: %(default)s",
    )
    parser.add_argument(
        "-r",
        "--retry-wait",
        type=float_positive,
        metavar="FLOAT",
        default=5.0,
        help="Pause between retries, default: %(default)s",
    )
    parser.add_argument(
        "--filename-format",
        type=str,
        metavar="FORMAT",
        default="$artist/$artist - $title",
        help=(
            "Filename format to use, default: %(default)s\n"
            f"Supported variables: {', '.join([f'${k}' for k in ALBUM_INFO_KEYS])}"
        ),
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-download and overwrite existing albums"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose information"
    )
    parser.add_argument("--debug", action="store_true", help="Show debug information")
    parser.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show version information and exit",
        version=f"{_name} v{_version}: {_copyright}",
    )
    args = parser.parse_args()
    with BandcampDownloader(**vars(args)) as app:
        sys.exit(app.run())


if __name__ == "__main__":
    main()
