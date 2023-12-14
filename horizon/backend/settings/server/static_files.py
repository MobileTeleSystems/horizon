# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from pydantic import BaseModel, Field, validator


class StaticFilesSettings(BaseModel):
    """Static files serving settings.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__STATIC_FILES__ENABLED=True
        HORIZON__SERVER__STATIC_FILES__DIRECTORY=/app/horizon/backend/static
        HORIZON__SERVER__STATIC_FILES__ENDPOINT=/static
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable static file serving")
    directory: Path = Field(
        default=Path("docs/_static"),
        description="Directory containing static files",
    )
    endpoint: str = Field(
        default="/static",
        description="Static files endpoint",
    )

    @validator("directory")
    def _validate_directory(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError(f"Directory '{value}' does not exist")
        if not value.is_dir():
            raise ValueError(f"Path '{value}' is not a directory")
        return value
