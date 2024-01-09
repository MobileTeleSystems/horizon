# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap
from typing import Dict, Set

from pydantic import BaseModel, Field


class MonitoringSettings(BaseModel):
    """Monitoring Settings.

    See `starlette-exporter <https://github.com/stephenhillier/starlette_exporter#options>`_ documentation.

    .. note::

        You can pass here any extra option supported by ``starlette-exporter``,
        even if it is not mentioned in documentation.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__MONITORING__ENABLED=True
        HORIZON__SERVER__MONITORING__SKIP_PATHS=["/some/path"]
        HORIZON__SERVER__MONITORING__SKIP_METHODS=["OPTIONS"]
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable middleware")
    labels: Dict[str, str] = Field(
        default_factory=dict,
        description="""Custom labels added to all metrics, e.g. ``{"instance": "production"}``""",
    )
    skip_paths: Set[str] = Field(
        default_factory=set,
        description="Custom paths should be skipped from metrics, like ``/some/endpoint``",
    )
    skip_methods: Set[str] = Field(
        default={"OPTIONS"},
        description="HTTP methods which should be excluded from metrics",
    )
    # These will be new defaults in starlette-exporter 0.18:
    # https://github.com/stephenhillier/starlette_exporter/issues/79
    group_paths: bool = Field(
        default=True,
        description=textwrap.dedent(
            """
            If ``True`` (recommended), add request path to metrics literally as described
            in OpenAPI schema, e.g. ``/namespace/{id}``, without substitution with path real values.

            If ``False``, all real request paths to metrics, e.g. ``/namespace/123``.
            """,
        ),
    )
    filter_unhandled_paths: bool = Field(
        default=True,
        description=textwrap.dedent(
            """
            If ``True``, add metrics for paths only mentioned in OpenAPI schema.

            If ``False``, add all requested paths to metrics.
            """,
        ),
    )

    class Config:
        extra = "allow"
