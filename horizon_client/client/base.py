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

    def _get_body(self, response: BaseResponse) -> dict:
        try:
            return response.json()
        except Exception as err:
            raise ValueError(response.content) from err

    def _parse_body(self, body: dict, response_class: type[ResponseSchema]) -> ResponseSchema:
        try:
            return parse_obj_as(response_class, body)
        except ValidationError as e:  # noqa: WPS329
            # Response does not match expected schema. Either API was changed, or
            # ValidationError does not contain body, so we attaching it to response.
            raise e from ValueError(body)

    def _handle_response(  # noqa: WPS238
        self,
        response: BaseResponse,
        response_class: type[ResponseSchema] | None,
    ) -> ResponseSchema | None:
        """Convert Response object to expected response class, or raise an exception matching the status code"""
        if response.status_code == http.HTTPStatus.NO_CONTENT.value or not response_class:
            return None

        if response.status_code < http.HTTPStatus.BAD_REQUEST.value:
            body = self._get_body(response)
            return self._parse_body(body, response_class)

        # raise_for_exception will definitely raise something, but mypy does not know that
        # so we create some exception to be bypass it
        http_exception: Exception = AssertionError("If you see this message, something went wrong")
        try:
            response.raise_for_status()
        except Exception as ex:
            http_exception = ex

        error_body = self._get_body(response)
        error_response = get_response_for_status_code(response.status_code)
        if not error_response:
            raise http_exception

        error_value = self._parse_body(error_body, APIErrorSchema[error_response.schema])  # type: ignore[name-defined]
        get_exception = getattr(error_value.error, "to_exception", None)
        if get_exception:
            raise get_exception() from http_exception

        raise http_exception
