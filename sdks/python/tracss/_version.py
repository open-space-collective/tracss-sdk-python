# SPDX-License-Identifier: Apache-2.0
"""Package version, readable at runtime as ``tracss.__version__``."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__: str = _version("tracss")
except PackageNotFoundError:
    __version__ = "0.0.0"
