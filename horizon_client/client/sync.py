# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import TypeVar

from authlib.integrations.requests_client import OAuth2Session
from pydantic import BaseModel

from horizon_client.client.base import BaseClient
from horizon_commons.schemas import PingResponse
from horizon_commons.schemas.v1 import (
    CreateNamespaceRequestV1,
    NamespaceResponseV1,
    PageResponseV1,
    PaginateNamespaceQueryV1,
    UpdateNamespaceRequestV1,
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
        query: PaginateNamespaceQueryV1 | None = None,
    ) -> PageResponseV1[NamespaceResponseV1]:
        """Get page with namespaces.

        Parameters
        ----------
        query : :obj:`PaginateNamespaceQueryV1 <horizon_commons.schemas.v1.namespace.PaginateNamespaceQueryV1>`
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

            namespace_query = PaginateNamespaceQueryV1(page_size=10)
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
        query = query or PaginateNamespaceQueryV1()
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/",
            response_class=PageResponseV1[NamespaceResponseV1],
            params=query.dict(),
        )

    def get_namespace(self, name: str) -> NamespaceResponseV1:
        """Get namespace by name.

        Parameters
        ----------
        name : str
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
            f"{self.base_url}/v1/namespaces/{name}",
            response_class=NamespaceResponseV1,
        )

    def create_namespace(self, namespace: CreateNamespaceRequestV1) -> NamespaceResponseV1:
        """Create new namespace.

        Parameters
        ----------
        namespace : :obj:`CreateNamespaceRequestV1 <horizon_commons.schemas.v1.namespace.CreateNamespaceRequestV1>`
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

            to_create = CreateNamespaceRequestV1(name="my_namespace")
            assert client.create_namespace(to_create) == NamespaceResponseV1(name="my_namespace", ...)
        """
        return self._request(  # type: ignore[return-value]
            "POST",
            f"{self.base_url}/v1/namespaces/",
            json=namespace.dict(),
            response_class=NamespaceResponseV1,
        )

    def update_namespace(self, name: str, changes: UpdateNamespaceRequestV1) -> NamespaceResponseV1:
        """Update existing namespace.

        Parameters
        ----------
        name : str
            Namespace name to update

        changes : :obj:`UpdateNamespaceRequestV1 <horizon_commons.schemas.v1.namespace.UpdateNamespaceRequestV1>`
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

            to_update = CreateNamespaceRequestV1(name="new_namespace_name")
            assert client.update_namespace("my_namespace", to_create) == NamespaceResponseV1(name="new_namespace_name", ...)
        """
        return self._request(  # type: ignore[return-value]
            "PATCH",
            f"{self.base_url}/v1/namespaces/{name}",
            json=changes.dict(),
            response_class=NamespaceResponseV1,
        )

    def delete_namespace(self, name: str) -> None:
        """Delete existing namespace.

        Parameters
        ----------
        name : str
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
            f"{self.base_url}/v1/namespaces/{name}",
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
