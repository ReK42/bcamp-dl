# bcamp-dl
[![PyPi Version](https://img.shields.io/pypi/v/bcamp-dl.svg)](https://pypi.python.org/pypi/bcamp-dl)
[![PyPI Status](https://img.shields.io/pypi/status/bcamp-dl.svg)](https://pypi.python.org/pypi/bcamp-dl)
[![Python Versions](https://img.shields.io/pypi/pyversions/bcamp-dl.svg)](https://pypi.python.org/pypi/bcamp-dl)
[![License](https://img.shields.io/github/license/ReK42/bcamp-dl)](https://github.com/ReK42/bcamp-dl/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/ReK42/bcamp-dl/main?logo=github)](https://github.com/ReK42/bcamp-dl/commits/main)
[![Build Status](https://img.shields.io/github/actions/workflow/status/ReK42/bcamp-dl/build.yml?logo=github)](https://github.com/ReK42/bcamp-dl/actions)
[![Linted by Ruff](https://img.shields.io/badge/linting-ruff-purple?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Code Style by Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Download your collection from Bandcamp.

## Installation
Install [Python](https://www.python.org/downloads/), then install `pipx` and use it to install `bcamp-dl`:
```sh
python -m pip install --upgrade pip setuptools pipx
pipx install bcamp-dl
```

## Usage
To use, login to Bandcamp using one of the supported browsers. All albums in your collection will be downloaded to the output directory, with subfolders, based on the filename format selected. If not specified, the defaults are to use Firefox and download as MP3 V0 to per-artist subfolders in the current directory.
```sh
bcamp-dl --browser <BROWSER> --file-format <FORMAT> --directory <DIR> <USERNAME>
```

For all options, run `bcamp-dl --help`

## Development Environment
```sh
git clone https://github.com/ReK42/bcamp-dl.git
cd bcamp-dl
python -m venv .env
source .env/bin/activate
python -m pip install --upgrade pip setuptools pre-commit
pre-commit install
pip install -e .[tests]
```
