# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import TypeVar

from authlib.integrations.requests_client import OAuth2Session
from pydantic import BaseModel

from horizon_client.client.base import BaseClient
from horizon_commons.schemas import PingResponse
from horizon_commons.schemas.v1 import (
    HWMPaginateQueryV1,
    HWMResponseV1,
    HWMWriteRequestV1,
    NamespaceCreateRequestV1,
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    NamespaceUpdateRequestV1,
    PageResponseV1,
)

ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)


class HorizonClientSync(BaseClient[OAuth2Session]):
    """Sync Horizon client implementation, based on ``requests``.

    Parameters
    ----------

    base_url : str
        Base URL of Horizon server, e.g. ``https://some.domain.com``

    auth : :obj:`BaseAuth <horizon_client.auth.base.BaseAuth>`
        Authentication class

    session : :obj:`OAuth2Session <authlib.integrations.requests_client.OAuth2Session>`
        Custom session object. Inherited from :obj:`requests.Session`, so you can pass custom
        session options.

    Examples
    --------

    .. code-block:: python

        from horizon_client.auth import OAuth2Password
        from horizon_client.client.sync import HorizonClientSync

        auth = OAuth2Password(username="me", password="12345")
        client = HorizonClientSync(base_url="https://some.domain.com", auth=auth)
    """

    def authorize(self) -> None:
        """Fetch and set access token (if required).

        Examples
        --------

        .. code-block:: python

            client.authorize()
        """

        session: OAuth2Session = self.session  # type: ignore[assignment]
        token_kwargs = self.auth.fetch_token_kwargs(self.base_url)
        if not token_kwargs:
            return
        session.token = session.fetch_token(**token_kwargs)
        # token will not be verified until we call any endpoint
        self.ping()

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

    def paginate_namespaces(
        self,
        query: NamespacePaginateQueryV1 | None = None,
    ) -> PageResponseV1[NamespaceResponseV1]:
        """Get page with namespaces.

        Parameters
        ----------
        query : :obj:`NamespacePaginateQueryV1 <horizon_commons.schemas.v1.namespace.NamespacePaginateQueryV1>`
            Namespace query parameters

        Returns
        -------
        :obj:`PageResponseV1 <horizon_commons.schemas.v1.pagination.PageResponseV1>`
            List of namespaces, limited by query parameters.

        Examples
        --------

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

            namespace_query = NamespacePaginateQueryV1(page_size=10)
            assert client.paginate_namespaces(query=namespace_query) == PageResponseV1[NamespaceResponseV1](
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
                    NamespaceResponseV1(...),
                    ...
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

    def get_namespace(self, namespace_name: str) -> NamespaceResponseV1:
        """Get namespace by name.

        Parameters
        ----------
        namespace_name : str
            Namespace name to get

        Returns
        -------
        :obj:`NamespaceResponseV1 <horizon_commons.schemas.v1.namespace.NamespaceResponseV1>`
            Namespace

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found

        Examples
        --------

        .. code-block:: python

            assert client.get_namespace("my_namespace") == NamespaceResponseV1(name="my_namespace", ...)
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/{namespace_name}",
            response_class=NamespaceResponseV1,
        )

    def create_namespace(self, namespace: NamespaceCreateRequestV1) -> NamespaceResponseV1:
        """Create new namespace.

        Parameters
        ----------
        namespace : :obj:`NamespaceCreateRequestV1 <horizon_commons.schemas.v1.namespace.NamespaceCreateRequestV1>`
            Namespace to create

        Returns
        -------
        :obj:`NamespaceResponseV1 <horizon_commons.schemas.v1.namespace.NamespaceResponseV1>`
            Created namespace

        Raises
        ------
        :obj:`EntityAlreadyExistsError <horizon_commons.exceptions.entity.EntityAlreadyExistsError>`
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

    def update_namespace(self, namespace_name: str, changes: NamespaceUpdateRequestV1) -> NamespaceResponseV1:
        """Update existing namespace.

        Parameters
        ----------
        namespace_name : str
            Namespace name to update

        changes : :obj:`NamespaceUpdateRequestV1 <horizon_commons.schemas.v1.namespace.NamespaceUpdateRequestV1>`
            Changes to namespace object

        Returns
        -------
        :obj:`NamespaceResponseV1 <horizon_commons.schemas.v1.namespace.NamespaceResponseV1>`
            Updated namespace

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found

        Examples
        --------

        .. code-block:: python

            to_update = NamespaceCreateRequestV1(name="new_namespace_name")
            assert client.update_namespace("my_namespace", to_create) == NamespaceResponseV1(name="new_namespace_name", ...)
        """
        return self._request(  # type: ignore[return-value]
            "PATCH",
            f"{self.base_url}/v1/namespaces/{namespace_name}",
            json=changes.dict(),
            response_class=NamespaceResponseV1,
        )

    def delete_namespace(self, namespace_name: str) -> None:
        """Delete existing namespace.

        Parameters
        ----------
        namespace_name : str
            Namespace name to delete

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found

        Examples
        --------

        .. code-block:: python

            client.delete_namespace("my_namespace")
        """
        self._request(
            "DELETE",
            f"{self.base_url}/v1/namespaces/{namespace_name}",
        )

    def paginate_hwm(
        self,
        namespace_name: str,
        query: HWMPaginateQueryV1 | None = None,
    ) -> PageResponseV1[HWMResponseV1]:
        """Get page with HWMs.

        Parameters
        ----------
        namespace_name : str
            Namespace name to get HWMs for
        query : :obj:`HWMPaginateQueryV1 <horizon_commons.schemas.v1.hwm.HWMPaginateQueryV1>`
            HWM query parameters

        Returns
        -------
        :obj:`PageResponseV1 <horizon_commons.schemas.v1.pagination.PageResponseV1>`
            List of HWM, limited by query parameters.

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found

        Examples
        --------

        .. code-block:: python

            assert client.paginate_hwm("my_namespace") == PageResponseV1[HWMResponseV1](
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
                    HWMResponseV1(...),
                    ...
                ],
            )

            hwm_query = HWMPaginateQueryV1(page_size=10)
            result = client.paginate_hwm(namespace_name="my_namespace", query=hwm_query)
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
                    HWMResponseV1(...),
                    ...
                ]
            )
        """
        query = query or HWMPaginateQueryV1()
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/{namespace_name}/hwm/",
            response_class=PageResponseV1[HWMResponseV1],
            params=query.dict(),
        )

    def get_hwm(self, namespace_name: str, hwm_name: str) -> HWMResponseV1:
        """Get HWM by name.

        Parameters
        ----------
        namespace_name : str
            Namespace name HWM belongs to
        hwm_name : str
            HWM name to write

        Returns
        -------
        :obj:`HWMResponseV1 <horizon_commons.schemas.v1.hwm.HWMResponseV1>`
            HWM

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            HWM or namespace not found

        Examples
        --------

        .. code-block:: python

            assert client.get_hwm("my_namespace", "my_hwm") == HWMResponseV1(name="my_hwm", ...)
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/{namespace_name}/hwm/{hwm_name}",
            response_class=HWMResponseV1,
        )

    def write_hwm(self, namespace_name: str, hwm_name: str, data: HWMWriteRequestV1) -> HWMResponseV1:
        """Create new or update existing HWM.

        Parameters
        ----------
        namespace_name : str
            Namespace name HWM belongs to
        hwm_name : str
            HWM name to write
        data : :obj:`HWMWriteRequestV1 <horizon_commons.schemas.v1.hwm.HWMWriteRequestV1>`
            HWM data

        Returns
        -------
        :obj:`HWMResponseV1 <horizon_commons.schemas.v1.hwm.HWMResponseV1>`
            New HWM

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            Namespace not found
        :obj:`EntityInvalidError <horizon_commons.exceptions.entity.EntityInvalidError>`
            HWM data is not valid

        Examples
        --------

        .. code-block:: python

            to_create = HWMWriteRequestV1(type="column_int", value=123)
            response = client.write_hwm("my_namespace", "my_hwm", to_create)
            assert == HWMResponseV1(
                name="my_hwm",
                type="column_int",
                value=123,
                ...,
            )
        """
        return self._request(  # type: ignore[return-value]
            "PATCH",
            f"{self.base_url}/v1/namespaces/{namespace_name}/hwm/{hwm_name}",
            json=data.dict(exclude_unset=True),
            response_class=HWMResponseV1,
        )

    def delete_hwm(self, namespace_name: str, hwm_name: str) -> None:
        """Delete existing HWM.

        Parameters
        ----------
        namespace_name : str
            Namespace name HWM belongs to
        hwm_name : str
            HWM name to delete

        Raises
        ------
        :obj:`EntityNotFoundError <horizon_commons.exceptions.entity.EntityNotFoundError>`
            HWM or namespace not found

        Examples
        --------

        .. code-block:: python

            client.delete_hwm("my_namespace", "my_hwm")
        """
        self._request(
            "DELETE",
            f"{self.base_url}/v1/namespaces/{namespace_name}/hwm/{hwm_name}",
        )

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
        if not session.token:
            self.authorize()

        response = session.request(method, url, json=json, params=params)
        return self._handle_response(response, response_class)
