# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field


class PaginationArgs(BaseModel):
    page: int = Field(gt=0, default=1)
    page_size: int = Field(gt=0, le=50, default=20)  # noqa: WPS432
