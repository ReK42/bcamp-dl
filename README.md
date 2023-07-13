# bcamp-dl

[![License](https://img.shields.io/github/license/ReK42/bcamp-dl)](https://github.com/ReK42/bcamp-dl/blob/main/LICENSE)
[![PyPi Version](https://img.shields.io/pypi/v/bcamp-dl.svg)](https://pypi.python.org/pypi/bcamp-dl)
[![PyPI Status](https://img.shields.io/pypi/status/bcamp-dl.svg)](https://pypi.python.org/pypi/bcamp-dl)
[![Python Versions](https://img.shields.io/pypi/pyversions/bcamp-dl.svg)](https://pypi.python.org/pypi/bcamp-dl)
[![Last Commit](https://img.shields.io/github/last-commit/ReK42/bcamp-dl/main?logo=github)](https://github.com/ReK42/bcamp-dl/commits/main)
[![Build Status](https://img.shields.io/github/actions/workflow/status/ReK42/bcamp-dl/build.yml?logo=github)](https://github.com/ReK42/bcamp-dl/actions)
[![Linted by Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code Style by Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Download your collection from Bandcamp.

## Installation
```sh
pipx install bcamp-dl
```

## Usage
```
bcamp-dl --browser <BROWSER> --file-format <FORMAT> --directory <DIR> <USERNAME>
```

For all options, run `bcamp-dl --help`

## Development Environment
```sh
git clone https://github.com/ReK42/bcamp-dl.git
cd bcamp-dl
pre-commit install
pip install -e .[tests]
```
