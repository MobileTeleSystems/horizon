# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TypeVar

from authlib.integrations.requests_client import OAuth2Session
from pydantic import BaseModel, validator

from horizon import __version__ as horizon_version
from horizon.client.base import BaseClient
from horizon.commons.schemas import PingResponse
from horizon.commons.schemas.v1 import (
    HWMCreateRequestV1,
    HWMHistoryPaginateQueryV1,
    HWMHistoryResponseV1,
    HWMPaginateQueryV1,
    HWMResponseV1,
    HWMUpdateRequestV1,
    NamespaceCreateRequestV1,
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    NamespaceUpdateRequestV1,
    PageResponseV1,
    UserResponseV1,
)

ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)


class HorizonClientSync(BaseClient[OAuth2Session]):
    """Sync Horizon client implementation, based on ``authlib`` and ``requests``.

    Parameters
    ----------

    base_url : str
        Base URL of Horizon server, e.g. ``https://some.domain.com``

    auth : :obj:`BaseAuth <horizon.client.auth.base.BaseAuth>`
        Authentication class

    session : :obj:`authlib.integrations.requests_client.OAuth2Session`
        Custom session object. Inherited from :obj:`requests.Session`, so you can pass custom
        session options.

    Examples
    --------

    .. code-block:: python

        from horizon.client.auth import LoginPassword
        from horizon.client.sync import HorizonClientSync

        auth = LoginPassword(login="me", password="12345")
        client = HorizonClientSync(base_url="https://some.domain.com", auth=auth)
    """

    def authorize(self) -> None:
        """Fetch and set access token (if required).

        Raises
        ------
        :obj:`horizon.commons.exceptions.AuthorizationError`
            Authorization failed
        """

        session: OAuth2Session = self.session  # type: ignore[assignment]
        token_kwargs = self.auth.fetch_token_kwargs(self.base_url)
        if token_kwargs:
            session.token = session.fetch_token(**token_kwargs)

        # token will not be verified until we call any endpoint
        # do not call ``self.whoami`` here to avoid recursion
        response = session.request("GET", f"{self.base_url}/v1/users/me")
        self._handle_response(response, UserResponseV1)

    def close(self) -> None:
        """Close session.

        Examples
        --------

        .. code-block:: python

            client.close()
        """
        session: OAuth2Session = self.session  # type: ignore[assignment]
        session.close()

    def __enter__(self):
        """Enter session as context manager. Similar to :obj:`requests.Session` behavior.

        Exiting context manager closes opened session.

        Examples
        --------

        .. code-block:: python

            with client:
                ...
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def ping(self) -> PingResponse:
        """Ping Horizon server.

        Examples
        --------

        .. code-block:: python

            assert client.ping() == PingResponse(status="ok")
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/monitoring/ping",
            response_class=PingResponse,
        )

    def whoami(self) -> UserResponseV1:
        """Get current user info.

        Examples
        --------

        .. code-block:: python

            assert client.whoami() == UserResponseV1(
                id=1,
                username="me",
            )
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/users/me",
            response_class=UserResponseV1,
        )

    def paginate_namespaces(
        self,
        query: NamespacePaginateQueryV1 | None = None,
    ) -> PageResponseV1[NamespaceResponseV1]:
        """Get page with namespaces.

        Parameters
        ----------
        query : :obj:`NamespacePaginateQueryV1 <horizon.commons.schemas.v1.namespace.NamespacePaginateQueryV1>`
            Namespace query parameters

        Returns
        -------
        :obj:`PageResponseV1 <horizon.commons.schemas.v1.pagination.PageResponseV1>` of :obj:`NamespaceResponseV1 <horizon.commons.schemas.v1.namespace.NamespaceResponseV1>`
            List of namespaces, limited and filtered by query parameters.

        Examples
        --------

        Get all namespaces:

        .. code-block:: python

            assert client.paginate_namespaces() == PageResponseV1[NamespaceResponseV1](
                meta=PageMetaResponseV1(
                    page=1,
                    pages_count=1,
                    total_count=10,
                    page_size=20,
                    has_next=False,
                    has_previous=False,
                    next_page=None,
                    previous_page=None,
                ),
                items=[
                    NamespaceResponseV1(...),
                    ...
                ],
            )

        Get all namespaces starting with a page number and page size:

        .. code-block:: python

            namespace_query = NamespacePaginateQueryV1(page=2, page_size=20)
            assert client.paginate_namespaces() == PageResponseV1[NamespaceResponseV1](
                meta=PageMetaResponseV1(
                    page=2,
                    pages_count=3,
                    total_count=50,
                    page_size=20,
                    has_next=True,
                    has_previous=True,
                    next_page=3,
                    previous_page=1,
                ),
                items=[
                    NamespaceResponseV1(...),
                    ...
                ],
            )

        Search for namespace with specific name:

        .. code-block:: python

            namespace_query = NamespacePaginateQueryV1(name="my_namespace")
            assert client.paginate_namespaces(namespace_query) == PageResponseV1[NamespaceResponseV1](
                meta=PageMetaResponseV1(
                    page=1,
                    pages_count=1,
                    total_count=1,
                    page_size=10,
                    has_next=False,
                    has_previous=False,
                    next_page=None,
                    previous_page=None,
                ),
                items=[
                    NamespaceResponseV1(name="my_namespace", ...),
                ]
            )
        """
        query = query or NamespacePaginateQueryV1()
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/",
            response_class=PageResponseV1[NamespaceResponseV1],
            params=query.dict(),
        )

    def get_namespace(self, namespace_id: int) -> NamespaceResponseV1:
        """Get namespace by name.

        Parameters
        ----------
        namespace_id : int
            Namespace name to get

        Returns
        -------
        :obj:`NamespaceResponseV1 <horizon.commons.schemas.v1.namespace.NamespaceResponseV1>`
            Namespace

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found

        Examples
        --------

        .. code-block:: python

            assert client.get_namespace(123) == NamespaceResponseV1(id=123, ...)
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/{namespace_id}",
            response_class=NamespaceResponseV1,
        )

    def create_namespace(self, namespace: NamespaceCreateRequestV1) -> NamespaceResponseV1:
        """Create new namespace.

        Parameters
        ----------
        namespace : :obj:`NamespaceCreateRequestV1 <horizon.commons.schemas.v1.namespace.NamespaceCreateRequestV1>`
            Namespace to create

        Returns
        -------
        :obj:`NamespaceResponseV1 <horizon.commons.schemas.v1.namespace.NamespaceResponseV1>`
            Created namespace

        Raises
        ------
        :obj:`EntityAlreadyExistsError <horizon.commons.exceptions.entity.EntityAlreadyExistsError>`
            Namespace with the same name already exists

        Examples
        --------

        .. code-block:: python

            to_create = NamespaceCreateRequestV1(name="my_namespace")
            assert client.create_namespace(to_create) == NamespaceResponseV1(name="my_namespace", ...)
        """
        return self._request(  # type: ignore[return-value]
            "POST",
            f"{self.base_url}/v1/namespaces/",
            json=namespace.dict(),
            response_class=NamespaceResponseV1,
        )

    def update_namespace(self, namespace_id: int, changes: NamespaceUpdateRequestV1) -> NamespaceResponseV1:
        """Update existing namespace.

        Parameters
        ----------
        namespace_id : int
            Namespace name to update

        changes : :obj:`NamespaceUpdateRequestV1 <horizon.commons.schemas.v1.namespace.NamespaceUpdateRequestV1>`
            Changes to namespace object

        Returns
        -------
        :obj:`NamespaceResponseV1 <horizon.commons.schemas.v1.namespace.NamespaceResponseV1>`
            Updated namespace

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found
        :obj:`EntityAlreadyExistsError <horizon.commons.exceptions.entity.EntityAlreadyExistsError>`
            Namespace with the same name already exists

        Examples
        --------

        .. code-block:: python

            to_update = NamespaceCreateRequestV1(name="new_namespace_name")
            assert client.update_namespace(123, to_update) == NamespaceResponseV1(id=123, name="new_namespace_name", ...)
        """
        return self._request(  # type: ignore[return-value]
            "PATCH",
            f"{self.base_url}/v1/namespaces/{namespace_id}",
            json=changes.dict(exclude_unset=True),
            response_class=NamespaceResponseV1,
        )

    def delete_namespace(self, namespace_id: int) -> None:
        """Delete existing namespace.

        Parameters
        ----------
        namespace_id : int
            Namespace name to delete

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found

        Examples
        --------

        .. code-block:: python

            client.delete_namespace(123)
        """
        self._request(
            "DELETE",
            f"{self.base_url}/v1/namespaces/{namespace_id}",
        )

    def paginate_hwm(
        self,
        query: HWMPaginateQueryV1,
    ) -> PageResponseV1[HWMResponseV1]:
        """Get page with HWMs.

        Parameters
        ----------
        query : :obj:`HWMPaginateQueryV1 <horizon.commons.schemas.v1.hwm.HWMPaginateQueryV1>`
            HWM query parameters

        Returns
        -------
        :obj:`PageResponseV1 <horizon.commons.schemas.v1.pagination.PageResponseV1>` of :obj:`HWMResponseV1 <horizon.commons.schemas.v1.hwm.HWMResponseV1>`
            List of HWM, limited and filtered by query parameters.

        Examples
        --------

        Get all HWM in namespace with specific id:

        .. code-block:: python

            hwm_query = HWMPaginateQueryV1(namespace_id=123)
            result = client.paginate_hwm(hwm_query)
            assert result == PageResponseV1[HWMResponseV1](
                meta=PageMetaResponseV1(
                    page=1,
                    pages_count=2,
                    total_count=10,
                    page_size=10,
                    has_next=True,
                    has_previous=False,
                    next_page=2,
                    previous_page=None,
                ),
                items=[
                    HWMResponseV1(namespace_id=123, ...),
                    ...
                ]
            )

        Get all HWM in namespace starting with a page number and page size:

        .. code-block:: python

            hwm_query = HWMPaginateQueryV1(namespace_id=123, page=2, page_size=20)
            result = client.paginate_hwm(hwm_query)
            assert result == PageResponseV1[HWMResponseV1](
                meta=PageMetaResponseV1(
                    page=2,
                    pages_count=3,
                    total_count=50,
                    page_size=20,
                    has_next=True,
                    has_previous=True,
                    next_page=3,
                    previous_page=1,
                ),
                items=[
                    HWMResponseV1(namespace_id=123, ...),
                    ...
                ]
            )

        Search for HWM with specific namespace and name:

        .. code-block:: python

            hwm_query = HWMPaginateQueryV1(namespace_id=123, name="my_hwm")
            result = client.paginate_hwm(hwm_query)
            assert result == PageResponseV1[HWMResponseV1](
                meta=PageMetaResponseV1(
                    page=1,
                    pages_count=1,
                    total_count=1,
                    page_size=10,
                    has_next=False,
                    has_previous=False,
                    next_page=None,
                    previous_page=None,
                ),
                items=[
                    HWMResponseV1(namespace_id=123, name="my_hwm", ...),
                ]
            )
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/hwm/",
            response_class=PageResponseV1[HWMResponseV1],
            params=query.dict(exclude_unset=True),
        )

    def get_hwm(self, hwm_id: int) -> HWMResponseV1:
        """Get HWM.

        Parameters
        ----------
        hwm_id : int
            HWM id to get

        Returns
        -------
        :obj:`HWMResponseV1 <horizon.commons.schemas.v1.hwm.HWMResponseV1>`
            HWM

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            HWM not found

        Examples
        --------

        .. code-block:: python

            assert client.get_hwm(234) == HWMResponseV1(id=234, namespace_id=123, name="my_hwm", ...)
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/hwm/{hwm_id}",
            response_class=HWMResponseV1,
        )

    def create_hwm(self, data: HWMCreateRequestV1) -> HWMResponseV1:
        """Create new HWM.

        Parameters
        ----------
        data : :obj:`HWMCreateRequestV1 <horizon.commons.schemas.v1.hwm.HWMCreateRequestV1>`
            HWM data

        Returns
        -------
        :obj:`HWMResponseV1 <horizon.commons.schemas.v1.hwm.HWMResponseV1>`
            Created HWM

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found
        :obj:`EntityAlreadyExistsError <horizon.commons.exceptions.entity.EntityAlreadyExistsError>`
            HWM with the same name already exists

        Examples
        --------

        .. code-block:: python

            to_create = HWMCreateRequestV1(namespace_id=123, name="my_hwm", type="column_int", value=5678)
            response = client.create_hwm(to_create)
            assert == HWMResponseV1(
                namespace_id=123,
                id=234,
                name="my_hwm",
                type="column_int",
                value=5678,
                ...,
            )
        """
        return self._request(  # type: ignore[return-value]
            "POST",
            f"{self.base_url}/v1/hwm/",
            json=data.dict(exclude_unset=True),
            response_class=HWMResponseV1,
        )

    def update_hwm(self, hwm_id: int, changes: HWMUpdateRequestV1) -> HWMResponseV1:
        """Update existing HWM.

        Parameters
        ----------
        hwm_id : int
            HWM id to update
        changes : :obj:`HWMUpdateRequestV1 <horizon.commons.schemas.v1.hwm.HWMUpdateRequestV1>`
            HWM changes

        Returns
        -------
        :obj:`HWMResponseV1 <horizon.commons.schemas.v1.hwm.HWMResponseV1>`
            Updated HWM

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            HWM not found
        :obj:`EntityAlreadyExistsError <horizon.commons.exceptions.entity.EntityAlreadyExistsError>`
            HWM with the same name already exists

        Examples
        --------

        .. code-block:: python

            to_update = HWMUpdateRequestV1(type="column_int", value=5678)
            response = client.update_hwm(234, to_update)
            assert == HWMResponseV1(
                namespace_id=123,
                id=234,
                name="my_hwm",
                type="column_int",
                value=5678,
                ...,
            )
        """
        return self._request(  # type: ignore[return-value]
            "PATCH",
            f"{self.base_url}/v1/hwm/{hwm_id}",
            json=changes.dict(exclude_unset=True),
            response_class=HWMResponseV1,
        )

    def delete_hwm(self, hwm_id: int) -> None:
        """Delete existing HWM.

        Parameters
        ----------
        hwm_id : int
            HWM id to delete

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            HWM not found

        Examples
        --------

        .. code-block:: python

            client.delete_hwm(234)
        """
        self._request(
            "DELETE",
            f"{self.base_url}/v1/hwm/{hwm_id}",
        )

    def paginate_hwm_history(
        self,
        query: HWMHistoryPaginateQueryV1,
    ) -> PageResponseV1[HWMHistoryResponseV1]:
        """Get page with HWM changes history.

        Parameters
        ----------
        query : :obj:`HWMHistoryPaginateQueryV1 <horizon.commons.schemas.v1.hwm_history.HWMHistoryPaginateQueryV1>`
            HWM history query parameters

        Returns
        -------
        :obj:`PageResponseV1 <horizon.commons.schemas.v1.pagination.PageResponseV1>` of :obj:`HWMHistoryResponseV1 <horizon.commons.schemas.v1.hwm_history.HWMHistoryResponseV1>`
            List of HWM history items, limited and filtered by query parameters.

        Examples
        --------

        Get all changes of specific HWM:

        .. code-block:: python

            hwm_query = HWMPaginateQueryV1(hwm_id=234)
            result = client.paginate_hwm(hwm_query)
            assert result == PageResponseV1[HWMHistoryResponseV1](
                meta=PageMetaResponseV1(
                    page=1,
                    pages_count=2,
                    total_count=10,
                    page_size=10,
                    has_next=True,
                    has_previous=False,
                    next_page=2,
                    previous_page=None,
                ),
                items=[
                    HWMHistoryResponseV1(hwm_id=234, ...),
                    ...
                ]
            )

        Get all changes of specific HWM starting with a page number and page size:

        .. code-block:: python

            hwm_query = HWMPaginateQueryV1(hwm_id=234, page=2, page_size=20)
            result = client.paginate_hwm(hwm_query)
            assert result == PageResponseV1[HWMHistoryResponseV1](
                meta=PageMetaResponseV1(
                    page=2,
                    pages_count=3,
                    total_count=50,
                    page_size=20,
                    has_next=True,
                    has_previous=True,
                    next_page=3,
                    previous_page=1,
                ),
                items=[
                    HWMHistoryResponseV1(hwm_id=234, ...),
                    ...
                ]
            )
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/hwm-history/",
            response_class=PageResponseV1[HWMHistoryResponseV1],
            params=query.dict(exclude_unset=True),
        )

    @validator("session", always=True)
    def _set_client_info(cls, session: OAuth2Session):
        session.headers["X-Client-Name"] = "python-horizon[sync]"
        session.headers["X-Client-Version"] = horizon_version
        return session

    def _request(
        self,
        method: str,
        url: str,
        response_class: type[ResponseSchema] | None = None,
        json: dict | None = None,
        params: dict | None = None,
    ) -> ResponseSchema | None:
        """Send request to backend and return ``response_class``, ``None`` or raise an exception."""

        session: OAuth2Session = self.session  # type: ignore[assignment]
        if not session.token or session.token.is_expired():
            self.authorize()

        response = session.request(method, url, json=json, params=params)
        return self._handle_response(response, response_class)
