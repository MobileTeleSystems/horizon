# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from enum import Enum


class Role(str, Enum):  # noqa: WPS60
    DEVELOPER = "DEVELOPER"
    MAINTAINER = "MAINTAINER"
    OWNER = "OWNER"
