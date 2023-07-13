# -*- coding: utf-8 -*-
"""Download your collection from Bandcamp."""
import json
import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from html import unescape
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from string import Template
from threading import Event
from time import sleep
from types import TracebackType
from typing import Any, Type
from unicodedata import normalize
from urllib.parse import unquote

import browser_cookie3
import requests
from bs4 import BeautifulSoup, SoupStrainer
from rich import box
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table


ALBUM_INFO_KEYS = [
    "artist",
    "title",
]
SUPPORTED_BROWSERS = [
    "brave",
    "chrome",
    "chromium",
    "edge",
    "firefox",
    "opera",
]
SUPPORTED_FILE_FORMATS = [
    "aac-hi",
    "aiff-lossless",
    "alac",
    "flac",
    "mp3-320",
    "mp3-v0",
    "vorbis",
    "wav",
]
MAX_THREADS = 16

URL_BASE = "https://bandcamp.com"
URL_COLLECTION = URL_BASE + "/api/fancollection/1/collection_items"
URL_USER = URL_BASE + "/"


def sanitize_path(path: Path, replace: str = "_") -> Path:
    """Sanitize a filename for use on the current platform."""
    parent = path.parent
    filename = str(path.stem)
    extension = str(path.suffix)
    if not os.path.supports_unicode_filenames:
        filename = normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
    if sys.platform.startswith("win"):
        filename = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", replace, filename)
        filename = filename.rstrip(". ")
    else:
        filename = re.sub(r"[/\x00-\x1f]", replace, filename)
        filename = filename.rstrip(":")
    return Path(parent, filename + extension)


class BandcampDownloader(object):
    """Download your collection from Bandcamp.

    To use, login to Bandcamp using one of the supported browsers. All albums in your
    collection will be downloaded to the output directory, with subfolders, based on the
    filename format selected.
    """

    def __init__(
        self,
        username: str = "",
        browser: str = "",
        directory: Path = Path("."),
        cookie_path: str = "",
        filename_format: str = "$artist/$artist - $title",
        file_format: str = "mp3-320",
        threads: int = 4,
        pause: float = 1.0,
        max_retries: int = 5,
        retry_wait: float = 5.0,
        force: bool = False,
        verbose: bool = False,
        debug: bool = False,
    ):
        if not username:
            raise ValueError("username is required")
        if browser not in SUPPORTED_BROWSERS:
            raise ValueError(f"browser {browser} not supported")
        if threads < 1 or threads > MAX_THREADS:
            raise ValueError(f"threads must be between 1 and {MAX_THREADS}")
        if pause < 0.0:
            raise ValueError("pause must be positive")
        if max_retries < 1:
            raise ValueError("max_retries must be greater than or equal to 1")
        if retry_wait < 0.0:
            raise ValueError("retry_wait must be positive")

        self.username = username
        self.browser = browser
        self.directory = directory
        self.filename_format = Template(filename_format)
        self.file_format = file_format
        self.threads = threads
        self.pause = pause
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.force = force
        self.verbose = verbose
        self.debug = debug

        self.event_stop = Event()
        self.user_info: dict[str, str | int] = {}
        self.links: list[str] = []
        self.job_progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            TransferSpeedColumn(),
            DownloadColumn(),
            TaskProgressColumn(),
            expand=True,
        )
        self.overall_progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            expand=True,
        )
        table = Table.grid(expand=True)
        table.add_row(Panel(self.job_progress, box=box.SIMPLE))
        table.add_row(Panel(self.overall_progress, box=box.SIMPLE))
        self.view = Live(table, refresh_per_second=10)

        if self.force and self.verbose:
            self.view.console.print(
                "Force flag set, existing files will be overwritten."
            )

        if cookie_path:
            cookie_jar = MozillaCookieJar(cookie_path)
            cookie_jar.load()
            self.cookies = cookie_jar
        else:
            func = getattr(browser_cookie3, self.browser)
            self.cookies = func(domain_name="bandcamp.com")

    def __enter__(self) -> "BandcampDownloader":
        self.view.start(refresh=True)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.view.stop()

    def run(self) -> int:
        """Primary execution thread."""
        self._get_albums()
        if not self.links:
            self.view.console.print(
                f"ERROR: No album links found for user {self.username}."
            )
            return 1
        if self.verbose:
            self.view.console.print(
                f"Found {len(self.links)} links in {self.username}'s collection."
            )
            self.view.console.print("Starting album downloads...")
        self.view.console.print("To cancel, press CTRL+BREAK")
        self.main_task = self.overall_progress.add_task(
            "Downloading albums...",
            total=len(self.links),
        )
        with ThreadPoolExecutor(max_workers=self.threads) as pool:
            pool.map(self._get_album, self.links)
        if self.event_stop.is_set():
            self.view.console.print("ERROR: Process aborted by user...")
            return 1
        if self.verbose:
            self.view.console.print("Done")
        return 0

    def _get_pagedata(self, url) -> dict[str, Any]:
        with requests.get(url, cookies=self.cookies) as resp:  # type: ignore
            resp.raise_for_status()
            soup = BeautifulSoup(
                resp.text, "html.parser", parse_only=SoupStrainer("div", id="pagedata")
            )
            div = soup.find("div")
        if not div:
            raise IOError(f"No div#pagedata found at {url}")
        return json.loads(unescape(div.get("data-blob")))  # type: ignore

    def _get_albums(self) -> None:
        data = self._get_pagedata(URL_USER + self.username)
        user_id = data["fan_data"]["fan_id"]
        collection_count = data["collection_count"]
        last_token = data["collection_data"]["last_token"]
        links = [*data["collection_data"]["redownload_urls"].values()]
        req = json.dumps(
            {
                "fan_id": user_id,
                "count": collection_count,
                "older_than_token": last_token,
            }
        )
        with requests.post(URL_COLLECTION, data=req, cookies=self.cookies) as resp:  # type: ignore
            resp.raise_for_status()
            data = json.loads(resp.text)
            links += data["redownload_urls"].values()
        self.links = links

    def _get_album(self, url: str) -> None:
        """Attempt to download an album."""
        if self.event_stop.is_set():
            return None
        try:
            data = self._get_pagedata(url)["download_items"][0]
            album = data["title"]
            if "downloads" not in data:
                raise IOError(f"Album {album} has no downloads available")
            if self.file_format not in data["downloads"]:
                raise IOError(
                    f"Album {album} does not have a download for format"
                    f" {self.file_format}"
                )
            url = data["downloads"][self.file_format]["url"]
            info = {k: data[k] for k in ALBUM_INFO_KEYS}
            task_id = self.job_progress.add_task(album)
            self._download_album(task_id, url, info)
        except Exception:
            self.view.console.print(f"ERROR: Failed to download album: {url}")
        finally:
            try:
                self.overall_progress.advance(self.main_task)
                self.job_progress.remove_task(task_id)
            except Exception:
                pass
            sleep(self.pause)

    def _download_album(
        self, task_id: TaskID, url: str, info: dict[str, str], attempt: int = 1
    ) -> None:
        if self.event_stop.is_set():
            return None
        try:
            with requests.get(url, cookies=self.cookies, stream=True) as resp:  # type: ignore
                resp.raise_for_status()
                content_length = int(resp.headers["content-length"])
                match = re.search(
                    r"filename\*=UTF-8\'\'.*(\..*)$",
                    resp.headers["content-disposition"],
                )
                if match:
                    extension = unquote(match.group(1))
                else:
                    extension = url.split("/")[-1]
                path = sanitize_path(
                    Path(
                        self.directory,
                        self.filename_format.substitute(info) + extension,
                    )
                )
                if path.exists():
                    if not self.force and path.stat().st_size == content_length:
                        if self.verbose:
                            self.view.console.print(
                                f"Skipping album, file already exists: {path}"
                            )
                        return None
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open(mode="wb") as f:
                    self.job_progress.reset(task_id, total=content_length)
                    self.job_progress.start_task(task_id)
                    for data in resp.iter_content(chunk_size=10):
                        if self.event_stop.is_set():
                            return None
                        f.write(data)
                        self.job_progress.advance(task_id, advance=len(data))
                if path.stat().st_size != content_length:
                    raise IOError("File does not match expected size")
        except IOError as e:
            if attempt < self.max_retries:
                if self.verbose:
                    self.view.console.print(
                        f"Download attempt {attempt} of {self.max_retries} failed:"
                        f" {url}"
                    )
                sleep(self.retry_wait)
                self._download_album(task_id, url, info, attempt=attempt + 1)
            else:
                raise IOError("Max retries exceeded") from e
