# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap
from typing import Any, Dict, Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class SwaggerSettings(BaseModel):
    """Swagger UI settings.

    SwaggerUI is served at ``/docs`` endpoint.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__OPENAPI__SWAGGER__ENABLED=True
        HORIZON__SERVER__OPENAPI__SWAGGER__JS_URL=/static/swagger/swagger-ui-bundle.js
        HORIZON__SERVER__OPENAPI__SWAGGER__CSS_URL=/static/swagger/swagger-ui.css
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable Swagger UI endpoint")
    js_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        description="URL for Swagger UI JS",
    )
    css_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        description="URL for Swagger UI CSS",
    )
    extra_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description=textwrap.dedent(
            """
            Additional parameters to pass to Swagger UI.
            See `FastAPI documentation <https://fastapi.tiangolo.com/how-to/configure-swagger-ui/>`_.
            """,
        ),
    )


class RedocSettings(BaseModel):
    """ReDoc settings.

    ReDOc is served at ``/redoc`` endpoint.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__OPENAPI__REDOC__ENABLED=True
        HORIZON__SERVER__OPENAPI__REDOC__JS_URL=/static/redoc/redoc.standalone.js
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable Redoc UI endpoint")
    js_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        description="URL for Redoc UI JS, ``None`` to use default CDN URL",
    )


class LogoSettings(BaseModel):
    """OpenAPI's ``x-logo`` documentation settings.

    See `OpenAPI spec <https://redocly.com/docs/api-reference-docs/specification-extensions/x-logo/>`_
    for more details.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__OPENAPI__LOGO__URL=/static/logo.svg
        HORIZON__SERVER__OPENAPI__LOGO__BACKGROUND_COLOR=ffffff
        HORIZON__SERVER__OPENAPI__LOGO__ALT_TEXT=Horizon logo
        HORIZON__SERVER__OPENAPI__LOGO__HREF=http://mycompany.domain.com
    """

    url: str = Field(
        default="/static/logo.svg",
        description="URL for application logo",
    )
    background_color: str = Field(
        default="ffffff",
        description="Background color in HEX RGB format, without ``#`` prefix",
    )
    alt_text: Optional[str] = Field(
        default="Horizon logo",
        description="Alternative text for ``<img>`` tag",
    )
    href: Optional[AnyHttpUrl] = Field(  # type: ignore[assignment]
        default="https://github.com/MobileTeleSystems/horizon",
        description="Clicking on logo will redirect to this URL",
    )


class FaviconSettings(BaseModel):
    """Favicon documentation settings.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__OPENAPI__FAVICON__URL=/static/icon.svg
    """

    url: str = Field(
        default="/static/icon.svg",
        description="URL for application favicon",
    )


class OpenAPISettings(BaseModel):
    """OpenAPI Settings.

    OpenAPI.json is served at ``/openapi.json`` endpoint.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__OPENAPI__ENABLED=True
        HORIZON__SERVER__OPENAPI__SWAGGER__ENABLED=True
        HORIZON__SERVER__OPENAPI__REDOC__ENABLED=True
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable OpenAPI.json endpoint")
    swagger: SwaggerSettings = Field(
        default_factory=SwaggerSettings,
        description="Swagger UI settings",
    )
    redoc: RedocSettings = Field(
        default_factory=RedocSettings,
        description="ReDoc UI settings",
    )
    logo: LogoSettings = Field(
        default_factory=LogoSettings,
        description="Application logo settings",
    )
    favicon: FaviconSettings = Field(
        default_factory=FaviconSettings,
        description="Application favicon settings",
    )
