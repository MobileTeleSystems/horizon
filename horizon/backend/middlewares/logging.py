# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

import logging
from logging.config import dictConfig
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class LoggingSetupError(Exception):
    pass


def setup_logging(config_path: Path) -> None:
    """Parse file with logging configuration, and setup logging accordingly"""
    if not config_path.exists():
        msg = f"Logging configuration file '{config_path}' does not exist"
        raise OSError(msg)

    try:
        config = yaml.safe_load(config_path.read_text())
        dictConfig(config)
    except Exception as e:
        msg = f"Error reading logging configuration '{config_path}'"
        raise LoggingSetupError(msg) from e
