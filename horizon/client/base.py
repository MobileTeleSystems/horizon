# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import http
import logging
import pprint
import warnings
from typing import Any, Generic, Optional, Tuple, TypeVar
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, BaseModel, PrivateAttr, ValidationError
from pydantic import __version__ as pydantic_version
from pydantic import parse_obj_as, validator

if pydantic_version >= "2":
    from pydantic import BaseModel as GenericModel  # noqa: WPS474
else:
    from pydantic.generics import GenericModel  # type: ignore[no-redef] # noqa: WPS440

from typing_extensions import Protocol

import horizon
from horizon.client.auth.base import BaseAuth
from horizon.commons.errors import get_response_for_status_code
from horizon.commons.errors.base import APIErrorSchema

logger = logging.getLogger(__name__)

SessionClass = TypeVar("SessionClass")
ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)


class BaseResponse(Protocol):
    """Response-like object. Same interface is shared between requests.Response and httpx.Response"""

    @property
    def status_code(self) -> int: ...  # noqa: WPS473

    @property
    def content(self) -> Any: ...

    def json(self) -> Any: ...

    def raise_for_status(self) -> None: ...

    @property
    def headers(self) -> dict[str, str]: ...


class BaseClient(GenericModel, Generic[SessionClass]):
    """Base Horizon client implementation, designed to be subclassed"""

    base_url: AnyHttpUrl
    auth: BaseAuth
    session: Optional[SessionClass] = None

    _backend_version_tuple: Tuple[int, ...] = PrivateAttr(default_factory=tuple)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def session_class(cls) -> type[SessionClass]:
        # Get `Session` from `SyncClient(BaseClient[Session])`
        if pydantic_version >= "2":
            return cls.model_fields["session"].annotation.__args__[0]  # type: ignore[union-attr]
        return cls.__bases__[0].__annotations__["session"].__args__[0]

    @validator("base_url")
    def _validate_url(cls, value: AnyHttpUrl):
        """``http://localhost:8000/`` -> ``http://localhost:8000``"""
        if value.path:
            return urlparse(str(value))._replace(path=value.path.rstrip("/")).geturl()  # noqa: WPS437
        return value

    @validator("session", always=True)
    def _default_session(cls, session: SessionClass | None):
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

    def _handle_backend_version(self, backend_version: str | None):
        if self._backend_version_tuple or not backend_version:
            return

        self._backend_version_tuple = tuple(map(int, backend_version.split(".")))  # noqa: WPS601
        if self._backend_version_tuple > horizon.__version_tuple__:
            message = (
                f"Horizon client version {horizon.__version__!r} does not match backend version {backend_version!r}. "
                "Please upgrade."
            )
            warnings.warn(message, UserWarning, stacklevel=5)

    def _handle_response(  # noqa: WPS238, WPS231
        self,
        response: BaseResponse,
        response_class: type[ResponseSchema] | None,
    ) -> ResponseSchema | None:
        """Convert Response object to expected response class, or raise an exception matching the status code"""
        request_id: str | None = response.headers.get("X-Request-ID", None)
        if request_id:
            logger.debug("Request ID: %r", request_id)

        backend_version = response.headers.get("X-Application-Version", None)
        self._handle_backend_version(backend_version)

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

        if request_id and hasattr(http_exception, "add_note"):
            # add_note is only available in Python 3.11+
            # https://docs.python.org/3/library/exceptions.html#BaseException.add_note
            http_exception.add_note(f"Request ID: {request_id!r}")

        try:
            body = response.json()
            if hasattr(http_exception, "add_note"):
                http_exception.add_note(f"Response body:\n{pprint.pformat(body)}")  # noqa: WPS237

        except Exception as format_err:  # noqa: WPS329
            if hasattr(http_exception, "add_note"):
                http_exception.add_note(f"Response body:\n{response.content!r}")
            else:
                logger.error("Response body:\n%r", response.content)

            raise format_err from http_exception

        error_response = get_response_for_status_code(response.status_code)
        if not error_response:
            # cannot handle this status code
            raise http_exception

        try:
            error_value = parse_obj_as(APIErrorSchema[error_response.schema], body)  # type: ignore[name-defined]
        except ValidationError:  # noqa: WPS329
            # Something wrong with API response, probably wrong URL
            raise http_exception

        get_exception = getattr(error_value.error, "to_exception", None)
        if get_exception:
            raise get_exception() from http_exception

        raise http_exception
