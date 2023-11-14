# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

LOG_PATH = Path(__file__).parent.resolve()


class LoggingSettings(BaseModel):
    setup: bool = Field(
        default=True,
        description="Setup logging using config file",
    )
    preset: Literal["json", "plain", "colored"] = Field(
        default="plain",
        description="Logging preset",
    )

    custom_config_path: Optional[Path] = Field(
        default=None,
        description=textwrap.dedent(
            """
            Path to custom logging configuration file. If set, overrides :obj:`~preset` value.

            File content should be in YAML format and conform
            `logging.dictConfig <https://docs.python.org/3/library/logging.config.html#logging-config-dictschema>`_.
            """,
        ),
    )

    def get_log_config_path(self) -> Path:
        return self.custom_config_path or LOG_PATH / f"{self.preset}.yml"
