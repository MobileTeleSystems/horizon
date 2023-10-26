# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import TypeVar

from authlib.integrations.requests_client import OAuth2Session
from pydantic import BaseModel

from horizon_client.client.base import BaseClient
from horizon_commons.schemas import PingResponse

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
        self._request("GET", self.base_url)

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
