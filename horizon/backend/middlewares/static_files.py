# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from horizon.backend.settings.server.static_files import StaticFilesSettings


def apply_static_files(app: FastAPI, settings: StaticFilesSettings) -> FastAPI:
    """Add static files serving middleware to the application."""
    if not settings.enabled:
        app.openapi_url = None
        return app

    # https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/#serve-the-static-files
    app.mount(settings.endpoint, StaticFiles(directory=settings.directory), name="static")
    return app
