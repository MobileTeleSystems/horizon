# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

"""
Settings for LDAPAuthProvider class.

Basic LDAP terminology is explained here: `LDAP Overview <https://www.zytrax.com/books/ldap/ch2/>`_
"""

import textwrap
from typing import TYPE_CHECKING, Optional, Type, Union

from bonsai import LDAPSearchScope
from pydantic import AnyUrl, BaseModel, Field, SecretStr, validator
from pydantic import __version__ as pydantic_version
from typing_extensions import Annotated, Literal

from horizon.backend.settings.auth.jwt import JWTSettings

if TYPE_CHECKING:
    LDAPUrl = AnyUrl
elif pydantic_version < "2":

    class LDAPUrl(AnyUrl):
        """LDAP connection url, like ``ldap://127.0.0.1:389`` or ``ldaps://127.0.0.1:636``"""

        allowed_schemes = ["ldap", "ldaps"]  # noqa: RUF012
        host_required = True

else:
    from pydantic import UrlConstraints

    LDAPUrl: Type[AnyUrl] = Annotated[
        AnyUrl,
        UrlConstraints(allowed_schemes=["ldap", "ldaps"], host_required=True),
    ]


class LDAPCredentials(BaseModel):
    """LDAP lookup query is executed using this credentials
    (instead of login and password provided by user).

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__USER=uid=techuser,ou=users,dc=example,dc=com
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__PASSWORD=somepassword
    """

    user: str = Field(
        description="DN of user which is used for calling ``lookup`` query in LDAP",
    )
    password: SecretStr = Field(
        description="This user password",
    )


class LDAPConnectionPoolSettings(BaseModel):
    """Settings related to LDAP connection pool.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__LDAP__LOOKUP__POOL__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__POOL__MAX=10
        HORIZON__AUTH__LDAP__LOOKUP__POOL__CHECK_ON_STARTUP=True
    """

    enabled: bool = Field(
        default=True,
        description="Set to ``True`` to enable connection pool",
    )
    initial: int = Field(
        default=1,
        description="Initial size of connection pool",
    )
    max: int = Field(
        default=10,
        description="Maximum size of connection pool",
    )


class LDAPLookupSettings(BaseModel):
    """Settings related to LDAP lookup.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__LDAP__LOOKUP__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__POOL__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__USER=uid=techuser,ou=users,dc=example,dc=com
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__PASSWORD=somepassword
        HORIZON__AUTH__LDAP__LOOKUP__QUERY=(uid={login})
    """

    enabled: bool = Field(
        default=True,
        description="Set to ``True`` to enable lookup",
    )
    check_on_startup: bool = Field(
        default=True,
        description="If ``True``, and LDAP is not available during application start, abort application startup",
    )
    pool: LDAPConnectionPoolSettings = Field(
        default_factory=LDAPConnectionPoolSettings,
        description="LDAP connection pool settings",
    )
    credentials: Optional[LDAPCredentials] = Field(
        default=None,
        description="Credentials used for connecting to LDAP while performing user lookup",
    )
    query_template: str = Field(
        default="({uid_attribute}={login})",
        description=textwrap.dedent(
            """
            LDAP query send in lookup request.

            Usually lookup is performed against attributes ``uid`` (LDAP) or ``sAMAccountName`` (ActiveDirectory).
            You can also pass any query string supported by LDAP.
            See `Bonsai documentation <https://bonsai.readthedocs.io/en/latest/tutorial.html#searching>`_.

            Supported substitution values (see :obj:`horizon.backend.settings.auth.ldap.LDAPSettings`.):
              * ``{uid_attribute}``
              * ``{login}``
            """,
        ),
    )
    scope: LDAPSearchScope = Field(
        default=LDAPSearchScope.ONELEVEL,
        description=textwrap.dedent(
            """
            Lookup scope. Use ``SUBTREE`` for ActiveDirectory.

            See `Bonsai documentation <https://bonsai.readthedocs.io/en/latest/api.html#bonsai.LDAPSearchScope.ONE>`_.
            """,
        ),
    )

    @validator("scope", pre=True)
    def _convert_scope_to_enum(cls, value: Union[str, int, LDAPSearchScope]) -> LDAPSearchScope:  # noqa: N805
        if isinstance(value, str):
            return LDAPSearchScope[value.upper()]
        return LDAPSearchScope(value)


class LDAPSettings(BaseModel):
    """Settings related to LDAP interaction.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__LDAP__URL=ldap://ldap.domain.com:389
        HORIZON__AUTH__LDAP__UID_ATTRIBUTE=sAMAccountName
    """

    url: LDAPUrl = Field(
        description="LDAP URL to connect to",
    )
    timeout_seconds: Optional[int] = Field(
        default=10,
        description="LDAP request timeout, in seconds. ``None`` means no timeout",
    )
    auth_mechanism: Literal["SIMPLE", "DIGEST-MD5"] = Field(
        default="SIMPLE",
        description="LDAP auth mechanism, used for ``bind`` request",
    )
    base_dn: str = Field(
        description="Organization DN, e.g. ``ou=users,dc=example,dc=com``",
    )
    uid_attribute: str = Field(
        default="uid",
        description=textwrap.dedent(
            """
            Attribute containing username.

            Usually ``uid`` (LDAP) or ``sAMAccountName`` (ActiveDirectory).
            """,
        ),
    )
    bind_dn_template: str = Field(
        default="{uid_attribute}={login},{base_dn}",
        description=textwrap.dedent(
            """
            Template for building DN string, used for checking credentials in LDAP.
            You can pass any DN value supported by LDAP.

            Supported substitution values:
              * ``{login}``
              * ``{uid_attribute}`` (see :obj:`~uid_attribute`)
              * ``{base_dn}`` (see :obj:`~base_dn`)
            """,
        ),
    )

    lookup: LDAPLookupSettings = Field(
        default_factory=LDAPLookupSettings,
        description="LDAP search options",
    )


class LDAPAuthProviderSettings(BaseModel):
    """Settings for LDAPAuthProvider.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__PROVIDER=horizon.backend.providers.auth.ldap.LDAPAuthProvider
        HORIZON__AUTH__ACCESS_KEY__SECRET_KEY=secret
        HORIZON__AUTH__LDAP__URL=ldap://ldap.domain.com:389
        HORIZON__AUTH__LDAP__LOOKUP__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__POOL__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__USER=uid=techuser,ou=users,dc=example,dc=com
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__PASSWORD=somepassword
    """

    access_token: JWTSettings = Field(description="Access-token related settings")
    ldap: LDAPSettings = Field(description="LDAP related settings")
