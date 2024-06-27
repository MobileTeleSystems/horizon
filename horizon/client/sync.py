# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import List, Optional, TypeVar, Union

from authlib.integrations.requests_client import OAuth2Session
from pydantic import BaseModel, Field, root_validator, validator
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from horizon import __version__ as horizon_version
from horizon.client.base import BaseClient
from horizon.commons.schemas import PingResponse
from horizon.commons.schemas.v1 import (
    HWMBulkCopyRequestV1,
    HWMBulkDeleteRequestV1,
    HWMCreateRequestV1,
    HWMHistoryPaginateQueryV1,
    HWMHistoryResponseV1,
    HWMListResponseV1,
    HWMPaginateQueryV1,
    HWMResponseV1,
    HWMUpdateRequestV1,
    NamespaceCreateRequestV1,
    NamespaceHistoryPaginateQueryV1,
    NamespaceHistoryResponseV1,
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    NamespaceUpdateRequestV1,
    PageResponseV1,
    PermissionsResponseV1,
    PermissionsUpdateRequestV1,
    UserResponseV1,
    UserResponseV1WithAdmin,
)

ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)


class RetryConfig(BaseModel):
    """
    Configuration for request retries in case of network errors or specific status codes.
    If provided, it customizes the retry behavior for requests made by the client.
    `urllib3 retry documentation <https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html>`_.

    Parameters
    ----------
    total : int, default: ``3``
        The maximum number of retry attempts to make.

    backoff_factor : float, default: ``0.1``
        A backoff factor to apply between attempts after the second try.

    status_forcelist : list[int], default: ``[502, 503, 504]``
        A set of HTTP status codes that we should force a retry on.

    backoff_jitter : float, default: ``None``
        A random jitter amount (between 0 and 1) to add to the backoff delay.
        Helps to avoid "thundering herd" issues by randomizing the delay
        times between retries.

        .. note::

            Requires ``urllib>2.0``
    """

    total: int = 3
    backoff_factor: float = 0.1
    status_forcelist: List[int] = [502, 503, 504]
    backoff_jitter: Optional[float] = None


class TimeoutConfig(BaseModel):
    """
    Configuration for connection and request timeouts.
    If provided, it customizes the timeout behavior for requests made by the client.
    `requests timeout documentation <https://requests.readthedocs.io/en/latest/user/advanced/#timeouts>`_.

    Parameters
    ----------
    connection_timeout : float, default: ``3``
        The maximum number of seconds to wait for a connection to the server.

    request_timeout : float, default: ``5``
        The maximum number of seconds to wait for a response from the server.
    """

    connection_timeout: float = 3
    request_timeout: float = 5


class HorizonClientSync(BaseClient[OAuth2Session]):
    """Sync Horizon client implementation, based on ``authlib`` and ``requests``.

    Parameters
    ----------

    base_url : str
        URL of Horizon API, e.g. ``https://some.domain.com/api``

    auth : :obj:`BaseAuth <horizon.client.auth.base.BaseAuth>`
        Authentication class

    retry : :obj:`RetryConfig <horizon.client.sync.RetryConfig>`
        Configuration for request retries.

    timeout : :obj:`TimeoutConfig <horizon.client.sync.TimeoutConfig>`
        Configuration for request timeouts.

    session : :obj:`authlib.integrations.requests_client.OAuth2Session`
        Custom session object. Inherited from :obj:`requests.Session`, so you can pass custom
        session options.

    Examples
    --------

    Using default parameters:

    >>> from horizon.client.auth import LoginPassword
    >>> from horizon.client.sync import HorizonClientSync
    >>> client = HorizonClientSync(
    ...     base_url="https://some.domain.com/api",
    ...     auth=LoginPassword(login="me", password="12345"),
    ... )

    Customize retry and timeout:

    >>> from horizon.client.auth import LoginPassword
    >>> from horizon.client.sync import HorizonClientSync, RetryConfig, TimeoutConfig
    >>> client = HorizonClientSync(
    ...     base_url="https://some.domain.com/api",
    ...     auth=LoginPassword(login="me", password="12345"),
    ...     retry=RetryConfig(total=2, backoff_factor=10, status_forcelist=[500, 503]),
    ...     timeout=TimeoutConfig(request_timeout=3.5),
    ... )
    """

    retry: RetryConfig = Field(default_factory=RetryConfig)
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)

    def authorize(self) -> None:
        """Fetch and set access token (if required).

        Raises
        ------
        :obj:`horizon.commons.exceptions.AuthorizationError`
            Authorization failed

        Examples
        --------

        >>> client.authorize()
        """

        session: OAuth2Session = self.session  # type: ignore[assignment]
        token_kwargs = self.auth.fetch_token_kwargs(self.base_url)
        if token_kwargs:
            session.token = session.fetch_token(**token_kwargs)

        # token will not be verified until we call any endpoint
        # do not call ``self.whoami`` here to avoid recursion
        timeout = (self.timeout.connection_timeout, self.timeout.request_timeout)
        response = session.request("GET", f"{self.base_url}/v1/users/me", timeout=timeout)
        self._handle_response(response, UserResponseV1)

    def close(self) -> None:
        """Close session.

        Examples
        --------

        >>> client.close()
        """
        session: OAuth2Session = self.session  # type: ignore[assignment]
        session.close()

    def __enter__(self):
        """Enter session as context manager. Similar to :obj:`requests.Session` behavior.

        Exiting context manager closes opened session.

        Examples
        --------

        >>> with client:
        ...    ...
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def ping(self) -> PingResponse:
        """Ping Horizon server.

        Examples
        --------

        >>> client.ping()
        PingResponse(status="ok")
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/monitoring/ping",
            response_class=PingResponse,
        )

    def whoami(self) -> Union[UserResponseV1WithAdmin, UserResponseV1]:
        """Get current user info.

        Examples
        --------

        >>> client.whoami()
        UserResponseV1(
            id=1,
            username="me",
        )

        >>> client.whoami()  # for a superadmin user:
        UserResponseV1WithAdmin(
            id=1,
            username="admin",
            is_admin=True,
        )

        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/users/me",
            response_class=Union[UserResponseV1WithAdmin, UserResponseV1],  # type: ignore[arg-type]
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

        >>> client.paginate_namespaces()
        PageResponseV1[NamespaceResponseV1](
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
            items=[NamespaceResponseV1(...), ...],
        )

        Get all namespaces starting with a page number and page size:

        >>> from horizon.commons.schemas.v1 import NamespacePaginateQueryV1
        >>> namespace_query = NamespacePaginateQueryV1(page=2, page_size=20)
        >>> client.paginate_namespaces(query=namespace_query)
        PageResponseV1[NamespaceResponseV1](
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
            items=[NamespaceResponseV1(...), ...],
        )

        Search for namespace with specific name:

        >>> from horizon.commons.schemas.v1 import NamespacePaginateQueryV1
        >>> namespace_query = NamespacePaginateQueryV1(name="my_namespace")
        >>> client.paginate_namespaces(query=namespace_query)
        PageResponseV1[NamespaceResponseV1](
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
            ],
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

        >>> client.get_namespace(namespace_id=123)
        NamespaceResponseV1(
            id=123,
            name="my_namespace",
            ...
        )
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/{namespace_id}",
            response_class=NamespaceResponseV1,
        )

    def create_namespace(self, data: NamespaceCreateRequestV1) -> NamespaceResponseV1:
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

        >>> from horizon.commons.schemas.v1 import NamespaceCreateRequestV1
        >>> to_create = NamespaceCreateRequestV1(name="my_namespace")
        >>> client.create_namespace(data=to_create)
        NamespaceResponseV1(
            id=123,
            name="my_namespace",
            ...
        )
        """
        return self._request(  # type: ignore[return-value]
            "POST",
            f"{self.base_url}/v1/namespaces/",
            json=data.dict(),
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
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> from horizon.commons.schemas.v1 import NamespaceUpdateRequestV1
        >>> to_update = NamespaceUpdateRequestV1(name="new_namespace_name")
        >>> client.update_namespace(namespace_id=123, changes=to_update)
        NamespaceResponseV1(
            id=123,
            name="new_namespace_name",
            ...
        )
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
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> client.delete_namespace(namespace_id=123)
        """
        self._request(
            "DELETE",
            f"{self.base_url}/v1/namespaces/{namespace_id}",
        )

    def paginate_namespace_history(
        self,
        query: NamespaceHistoryPaginateQueryV1,
    ) -> PageResponseV1[NamespaceHistoryResponseV1]:
        """Get page with namespace changes history.

        Parameters
        ----------
        query : :obj:`NamespaceHistoryPaginateQueryV1 <horizon.commons.schemas.v1.namespace_history.NamespaceHistoryPaginateQueryV1>`
            Namespace history query parameters

        Returns
        -------
        :obj:`PageResponseV1 <horizon.commons.schemas.v1.pagination.PageResponseV1>` of :obj:`NamespaceHistoryResponseV1 <horizon.commons.schemas.v1.namespace_history.NamespaceHistoryResponseV1>`
            List of namespace history items, limited and filtered by query parameters.

        Examples
        --------

        Get all changes of specific namespace:

        >>> from horizon.commons.schemas.v1 import NamespacePaginateQueryV1
        >>> namespace_query = NamespacePaginateQueryV1(namespace_id=234)
        >>> client.paginate_namespace(query=namespace_query)
        PageResponseV1[NamespaceHistoryResponseV1](
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
            items=[NamespaceHistoryResponseV1(namespace_id=234, ...), ...],
        )

        Get all changes of specific namespace starting with a page number and page size:

        >>> from horizon.commons.schemas.v1 import NamespacePaginateQueryV1
        >>> namespace_query = NamespacePaginateQueryV1(namespace_id=234, page=2, page_size=20)
        >>> client.paginate_namespace(query=namespace_query)
        PageResponseV1[NamespaceHistoryResponseV1](
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
            items=[NamespaceHistoryResponseV1(namespace_id=234, ...), ...],
        )
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespace-history/",
            response_class=PageResponseV1[NamespaceHistoryResponseV1],
            params=query.dict(exclude_unset=True),
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

        >>> from horizon.commons.schemas.v1 import HWMPaginateQueryV1
        >>> hwm_query = HWMPaginateQueryV1(namespace_id=123)
        >>> client.paginate_hwm(query=hwm_query)
        PageResponseV1[HWMResponseV1](
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
            items=[HWMResponseV1(namespace_id=123, ...), ...],
        )

        Get all HWM in namespace starting with a page number and page size:

        >>> from horizon.commons.schemas.v1 import HWMPaginateQueryV1
        >>> hwm_query = HWMPaginateQueryV1(namespace_id=123, page=2, page_size=20)
        >>> client.paginate_hwm(query=hwm_query)
        PageResponseV1[HWMResponseV1](
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
            items=[HWMResponseV1(namespace_id=123, ...), ...],
        )

        Search for HWM with specific namespace and name:

        >>> from horizon.commons.schemas.v1 import HWMPaginateQueryV1
        >>> hwm_query = HWMPaginateQueryV1(namespace_id=123, name="my_hwm")
        >>> client.paginate_hwm(query=hwm_query)
        PageResponseV1[HWMResponseV1](
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
            ],
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

        >>> client.get_hwm(hwm_id=234)
        HWMResponseV1(
            id=234,
            namespace_id=123,
            name="my_hwm",
            ...
        )
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
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> from horizon.commons.schemas.v1 import HWMCreateRequestV1
        >>> to_create = HWMCreateRequestV1(
        ...     namespace_id=123,
        ...     name="my_hwm",
        ...     type="column_int",
        ...     value=5678,
        ... )
        >>> client.create_hwm(data=to_create)
        HWMResponseV1(
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
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> from horizon.commons.schemas.v1 import HWMUpdateRequestV1
        >>> to_update = HWMUpdateRequestV1(type="column_int", value=5678)
        >>> client.update_hwm(hwm_id=234, changes=to_update)
        HWMResponseV1(
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
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> client.delete_hwm(hwm_id=234)
        """
        self._request(
            "DELETE",
            f"{self.base_url}/v1/hwm/{hwm_id}",
        )

    def bulk_copy_hwm(self, data: HWMBulkCopyRequestV1) -> HWMListResponseV1:
        """Copy HWMs from one namespace to another.

        .. note::

            Method ignores HWMs that are not related to provided source namespace, or does not exist.

        Parameters
        ----------
        data : :obj:`HWMBulkCopyRequestV1 <horizon.commons.schemas.v1.hwm.HWMBulkCopyRequestV1>`
            HWM copy data

        Returns
        -------
        :obj:`HWMListResponseV1 <horizon.commons.schemas.v1.hwm.HWMListResponseV1>`
            Copied HWMs

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Raised if any of the specified namespaces not found.
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------
        >>> from horizon.commons.schemas.v1 import HWMBulkCopyRequestV1
        >>> copy_data = HWMBulkCopyRequestV1(
        ...     source_namespace_id=123,
        ...     target_namespace_id=456,
        ...     hwm_ids=[1, 2, 3],
        ...     with_history=True,
        ... )
        >>> copied_hwms = client.bulk_copy_hwm(data=copy_data)
        [HWMResponseV1(...), HWMResponseV1(...), HWMResponseV1(...)]
        """
        return self._request(  # type: ignore[return-value]
            "POST",
            f"{self.base_url}/v1/hwm/copy",
            json=data.dict(),
            response_class=HWMListResponseV1,
        )

    def bulk_delete_hwm(self, namespace_id: int, hwm_ids: List[int]) -> None:
        """Bulk delete HWMs.

        .. note::

            Method ignores HWMs that are not related to provided namespace.

        Parameters
        ----------
        namespace_id : int
            Namespace ID where the HWMs belong.
        hwm_ids : List[int]
            List of HWM IDs to be deleted.

        Raises
        ------
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> client.bulk_delete_hwm(
        ...     namespace_id=123,
        ...     hwm_ids=[234, 345, 456]
        ... )
        """

        data = HWMBulkDeleteRequestV1(namespace_id=namespace_id, hwm_ids=hwm_ids)
        self._request(
            "DELETE",
            f"{self.base_url}/v1/hwm/",
            json=data.dict(),
        )

    def get_namespace_permissions(self, namespace_id: int) -> PermissionsResponseV1:
        """Get permissions for a namespace.

        Parameters
        ----------
        namespace_id : int
            The ID of the namespace to get permissions for.

        Returns
        -------
        :obj:`PermissionsResponseV1 <horizon.commons.schemas.v1.permission.PermissionsResponseV1>`
            The permissions of the namespace.

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Namespace or provided user not found.
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.

        Examples
        --------

        >>> client.get_namespace_permissions(namespace_id=234)
        """

        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/namespaces/{namespace_id}/permissions",
            response_class=PermissionsResponseV1,
        )

    def update_namespace_permissions(
        self,
        namespace_id: int,
        changes: PermissionsUpdateRequestV1,
    ) -> PermissionsResponseV1:
        """Update permissions for a namespace.

        Parameters
        ----------
        namespace_id : int
            The ID of the namespace to update permissions for.
        changes : :obj:`PermissionsUpdateRequestV1 <horizon.commons.schemas.v1.permission.PermissionsUpdateRequestV1>`
            The changes to apply to the namespace's permissions.

        Returns
        -------
        :obj:`PermissionsResponseV1 <horizon.commons.schemas.v1.permission.PermissionsResponseV1>`
            Actual permissions of the namespace.

        Raises
        ------
        :obj:`EntityNotFoundError <horizon.commons.exceptions.entity.EntityNotFoundError>`
            Namespace or provided user not found.
        :obj:`PermissionDeniedError <horizon.commons.exceptions.permission.PermissionDeniedError>`
            Permission denied for performing the requested action.
        :obj:`BadRequestError <horizon.commons.exceptions.bad_request.BadRequestError>`
            Bad request with incorrect operating logic.

        Examples
        --------

        >>> from horizon.commons.schemas.v1 import PermissionsUpdateRequestV1, PermissionUpdateRequestItemV1
        >>> to_update = PermissionsUpdateRequestV1([
        ...     PermissionUpdateRequestItemV1(username="new_owner", role="OWNER"),
        ...     PermissionUpdateRequestItemV1(username="add_developer", role="DEVELOPER"),
        ...     PermissionUpdateRequestItemV1(username="make_read_only", role=None),
        ... ])
        >>> client.update_namespace_permissions(namespace_id=234, changes=to_update)
        """
        return self._request(  # type: ignore[return-value]
            "PATCH",
            f"{self.base_url}/v1/namespaces/{namespace_id}/permissions",
            json=changes.dict(exclude_unset=True),
            response_class=PermissionsResponseV1,
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

        >>> from horizon.commons.schemas.v1 import HWMPaginateQueryV1
        >>> hwm_query = HWMPaginateQueryV1(hwm_id=234)
        >>> client.paginate_hwm(query=hwm_query)
        PageResponseV1[HWMHistoryResponseV1](
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
            items=[HWMHistoryResponseV1(hwm_id=234, ...), ...],
        )

        Get all changes of specific HWM starting with a page number and page size:

        >>> from horizon.commons.schemas.v1 import HWMPaginateQueryV1
        >>> hwm_query = HWMPaginateQueryV1(hwm_id=234, page=2, page_size=20)
        >>> client.paginate_hwm(query=hwm_query)
        PageResponseV1[HWMHistoryResponseV1](
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
            items=[HWMHistoryResponseV1(hwm_id=234, ...), ...],
        )
        """
        return self._request(  # type: ignore[return-value]
            "GET",
            f"{self.base_url}/v1/hwm-history/",
            response_class=PageResponseV1[HWMHistoryResponseV1],
            params=query.dict(exclude_unset=True),
        )

    # retry validator is called after "session" validators, when session already created by default or passed directly
    @root_validator(pre=False, skip_on_failure=True)
    def _configure_retries(cls, values):
        session = values.get("session")
        retry_config = values.get("retry")

        optional_retry_args = {}
        if retry_config.backoff_jitter is not None:
            # added to Retry class only in urllib3 2.0+
            optional_retry_args["backoff_jitter"] = retry_config.backoff_jitter

        retries = Retry(
            total=retry_config.total,
            backoff_factor=retry_config.backoff_factor,
            status_forcelist=retry_config.status_forcelist,
            allowed_methods=frozenset(("GET", "POST", "PUT", "PATCH", "DELETE")),
            **optional_retry_args,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return values

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

        timeout = (self.timeout.connection_timeout, self.timeout.request_timeout)
        response = session.request(method, url, json=json, params=params, timeout=timeout)
        return self._handle_response(response, response_class)
