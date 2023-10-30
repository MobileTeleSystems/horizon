# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import http
from typing import Any, Generic, TypeVar
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, BaseModel, ValidationError, parse_obj_as, validator
from pydantic.generics import GenericModel
from typing_extensions import Protocol

from horizon_client.auth.base import BaseAuth
from horizon_commons.errors import get_response_for_status_code
from horizon_commons.errors.base import APIErrorSchema

SessionClass = TypeVar("SessionClass")
ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)


class BaseResponse(Protocol):
    """Response-like object. Same interface is shared between requests.Response and httpx.Response"""

    @property
    def status_code(self) -> int:
        ...

    @property
    def content(self) -> Any:
        ...

    def json(self) -> Any:
        ...

    def raise_for_status(self) -> None:
        ...


class BaseClient(GenericModel, Generic[SessionClass]):
    """Base Horizon client implementation, designed to be subclassed"""

    base_url: AnyHttpUrl
    auth: BaseAuth
    session: SessionClass | None = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def session_class(cls) -> type[SessionClass]:
        # Get `Session` from `SyncClient(BaseClient[Session])`
        return cls.__bases__[0].__annotations__["session"].__args__[0]

    @validator("base_url")
    def _validate_url(cls, value: AnyHttpUrl, values: dict):
        """``http://localhost:8000/`` -> ``http://localhost:8000``"""
        if value.path:
            return urlparse(value)._replace(path=value.path.rstrip("/")).geturl()  # noqa: WPS437
        return value

    @validator("session", always=True)
    def _default_session(cls, session: SessionClass | None, values: dict):
        """If session is not passed, create it automatically"""
        if session:
            return session

        RealSessionClass = cls.session_class()  # noqa: N806
        return RealSessionClass()

    @validator("session", always=True)
    def _patch_session(cls, session: SessionClass, values: dict):
        """Patch session for chosen auth method, if required"""
        auth: BaseAuth = values.get("auth")  # type: ignore[assignment]
        return auth.patch_session(session)

    def _parse_body(self, body: dict, response_class: type[ResponseSchema]) -> ResponseSchema:
        try:
            return parse_obj_as(response_class, body)
        except ValidationError as e:  # noqa: WPS329
            # Response does not match expected schema. Probably API was changed.
            # ValidationError does not contain body, so we attaching it to response.
            raise e from ValueError(body)

    def _handle_response(  # noqa: WPS238
        self,
        response: BaseResponse,
        response_class: type[ResponseSchema] | None,
    ) -> ResponseSchema | None:
        """Convert Response object to expected response class, or raise an exception matching the status code"""
        if response.status_code == http.HTTPStatus.NO_CONTENT.value:
            return None

        if response.status_code < http.HTTPStatus.BAD_REQUEST.value and response_class:
            return self._parse_body(response.json(), response_class)

        # raise_for_exception will definitely raise something, but mypy does not know that
        # so we create some exception to be bypass it
        http_exception: Exception = AssertionError("If you see this message, something went wrong")
        try:
            response.raise_for_status()
        except Exception as e:
            http_exception = e

        error_response = get_response_for_status_code(response.status_code)
        if not error_response:
            # cannot handle this status code
            raise http_exception

        try:
            error_body = response.json()
        except Exception as format_err:  # noqa: WPS329
            raise format_err from http_exception

        try:
            error_value = parse_obj_as(APIErrorSchema[error_response.schema], error_body)  # type: ignore[name-defined]
        except ValidationError:  # noqa: WPS329
            # Something wrong with API response, probably wrong URL
            raise http_exception

        get_exception = getattr(error_value.error, "to_exception", None)
        if get_exception:
            raise get_exception() from http_exception

        raise http_exception
