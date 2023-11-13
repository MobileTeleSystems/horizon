# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

"""
Settings for LDAPAuthProvider class.

Basic LDAP terminology is explained here: `LDAP Overview <https://www.zytrax.com/books/ldap/ch2/>`_
"""

import textwrap
from typing import List, Optional, Union

from ldap3.operation.search import parse_filter
from pydantic import AnyUrl, BaseModel, Field, SecretStr, validator
from typing_extensions import Literal

from horizon.backend.settings.auth.jwt import JWTSettings


class LDAPUrl(AnyUrl):
    """LDAP connection url, like ``ldap://127.0.0.1:389`` or ``ldaps://127.0.0.1:636``"""

    allowed_schemes = ["ldap", "ldaps"]
    host_required = True


class LDAPCredentials(BaseModel):
    user: str
    password: SecretStr


class LDAPServerPoolSettings(BaseModel):
    urls: List[LDAPUrl] = Field(
        description="""
        LDAP URls to connect to.

        This is used for creating server pool with :obj:`~strategy`.
        """,
    )

    strategy: Literal["FIRST", "ROUND_ROBIN", "RANDOM"] = Field(
        default="ROUND_ROBIN",
        description="Strategy used for selecting server from server pool.",
    )

    retries: Union[bool, int] = Field(
        default=5,
        description=textwrap.dedent(  # noqa: WPS462
            """
            Number of retries for server availability check.

            ``False`` means disable checks.
            ``True`` means check infinitely.
            """,
        ),
    )
    lost_timeout: Union[bool, int] = Field(
        default=10,
        description=textwrap.dedent(  # noqa: WPS462
            """
            Timeout for server to be marked as unavailable, and exclude from pool.

            ``False`` means do not exclude servers from pool.
            ``True`` means exclude immediately.
            """,
        ),
    )

    @validator("urls", pre=True)
    def _parse_urls(cls, urls):
        if isinstance(urls, str):
            return urls.split(",")
        return urls


class LDAPLookupSettings(BaseModel):
    credentials: Optional[LDAPCredentials] = Field(
        default=None,
        description="Credentials used for connecting to LDAP while performing user lookup",
    )
    query: str = Field(
        default="({uid_attribute}={username})",
        description=textwrap.dedent(  # noqa: WPS462
            """
            LDAP query send in lookup request.

            Usually lookup is performed against attributes ``uid`` (LDAP) or ``sAMAccountName`` (ActiveDirectory).
            You can also pass any query string supported by LDAP.
            See `LDAP3 documentation <https://ldap3.readthedocs.io/en/latest/searches.html#the-ldap-filter>`_.

            Supported substitution values (see :obj:`horizon.backend.settings.auth.ldap.LDAPSettings`.):
            * ``{uid_attribute}``
            * ``{username}``
            """,
        ),
    )
    scope: Literal["BASE", "LEVEL", "SUBTREE"] = Field(
        default="LEVEL",
        description=textwrap.dedent(  # noqa: WPS462
            """
            Lookup scope. Use ``SUBTREE`` for ActiveDirectory.

            See `LDAP3 documentation <https://ldap3.readthedocs.io/en/latest/searches.html#search-scope-and-aliases>`_.
            """,
        ),
    )

    @validator("query")
    def _validate_query(cls, query):
        parse_filter(
            query.format(username="someuser", uid_attribute="uid"),
            schema=None,
            auto_escape=None,
            auto_encode=None,
            validator=None,
            check_names=None,
        )
        return query


class LDAPSettings(BaseModel):
    server: LDAPServerPoolSettings

    base_dn: str = Field(
        description="Organization DN, e.g. ``ou=users,dc=example,dc=com``",
    )
    uid_attribute: str = Field(
        default="uid",
        description=textwrap.dedent(  # noqa: WPS462
            """
            Attribute containing username.

            Usually ``uid`` (LDAP) or ``sAMAccountName`` (ActiveDirectory).
            """,
        ),
    )
    bind_dn_template: str = Field(
        default="{uid_attribute}={username},{base_dn}",
        description=textwrap.dedent(  # noqa: WPS462
            """
            Template for building DN string, used for checking credentials in LDAP. You can pass any DN value supported by LDAP.

            Supported substitution values:
            * ``{username}``
            * ``{uid_attribute}`` (see :obj:`~uid_attribute`)
            * ``{base_dn}`` (see :obj:`~base_dn`)
            """,
        ),
    )
    lookup: Optional[LDAPLookupSettings] = Field(
        default_factory=LDAPLookupSettings,
        description="LDAP search options. Set to ``None`` to disable lookup.",
    )


class LDAPAuthProviderSettings(BaseModel):
    access_token: JWTSettings
    ldap: LDAPSettings
