# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from functools import partial

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi
from starlette.requests import Request
from starlette.responses import JSONResponse

from horizon.backend.settings.server.openapi import OpenAPISettings


async def custom_openapi(request: Request) -> JSONResponse:
    app = request.app
    root_path = request.scope.get("root_path", "").rstrip("/")
    server_urls = set(filter(None, (server_data.get("url") for server_data in app.servers)))

    if root_path not in server_urls:
        if root_path and app.root_path_in_servers:
            app.servers.insert(0, {"url": root_path})
            server_urls.add(root_path)

    return JSONResponse(app.openapi())


def custom_openapi_schema(application: FastAPI, settings: OpenAPISettings) -> dict:
    if application.openapi_schema:
        return application.openapi_schema

    openapi_schema = get_openapi(
        title=application.title,
        version=application.version,
        summary=application.summary,
        description=application.description,
        routes=application.routes,
    )
    # https://redocly.com/docs/api-reference-docs/specification-extensions/x-logo/
    openapi_schema["info"]["x-logo"] = {
        "url": str(settings.logo.url),
        "altText": str(settings.logo.alt_text),
        "backgroundColor": f"#{settings.logo.background_color}",  # noqa: WPS237
        "href": str(settings.logo.href),
    }
    application.openapi_schema = openapi_schema
    return application.openapi_schema


async def custom_swagger_ui_html(request: Request):
    app = request.app
    openapi = app.state.settings.server.openapi
    return get_swagger_ui_html(
        openapi_url=openapi.url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=str(openapi.swagger.js_url),
        swagger_css_url=str(openapi.swagger.css_url),
        swagger_favicon_url=str(openapi.favicon.url),
    )


async def custom_swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


async def custom_redoc_html(request: Request):
    app = request.app
    openapi = app.state.settings.server.openapi
    return get_redoc_html(
        openapi_url=openapi.url,
        title=f"{app.title} - ReDoc",
        redoc_js_url=openapi.redoc.js_url,
        redoc_favicon_url=openapi.favicon.url,
    )


def apply_openapi_middleware(app: FastAPI, settings: OpenAPISettings) -> FastAPI:
    """Add OpenAPI middleware to the application."""
    # https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/#include-the-custom-docs
    if settings.enabled:
        app.openapi_url = "/openapi.json"
        app.add_route(app.openapi_url, custom_openapi, include_in_schema=False)

    if settings.swagger.enabled:
        app.docs_url = "/docs"
        app.swagger_ui_oauth2_redirect_url = "/docs/oauth2-redirect"
        app.add_route(app.docs_url, custom_swagger_ui_html, include_in_schema=False)
        app.add_route(app.swagger_ui_oauth2_redirect_url, custom_swagger_ui_redirect, include_in_schema=False)

    if settings.redoc.enabled:
        app.redoc_url = "/redoc"
        app.add_route(app.redoc_url, custom_redoc_html, include_in_schema=False)

    app.openapi = partial(custom_openapi_schema, application=app, settings=settings)  # type: ignore[method-assign]
    return app
