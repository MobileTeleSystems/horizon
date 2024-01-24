# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

# _raw_version could contain pre-release version, like 0.0.1dev123
# value is updated automatically by `poetry version ...` and poetry-bumpversion plugin
_raw_version = "0.0.13"

# version always contain only release number like 0.0.1
__version__ = ".".join(_raw_version.split(".")[:3])  # noqa: WPS410

# version tuple always contains only integer parts, like (0, 0, 1)
__version_tuple__ = tuple(map(int, __version__.split(".")))
