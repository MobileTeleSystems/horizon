# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

"""
Settings for LDAPAuthProvider class.

Basic LDAP terminology is explained here: `LDAP Overview <https://www.zytrax.com/books/ldap/ch2/>`_
"""

import textwrap
from typing import TYPE_CHECKING, Optional, Type

from bonsai import LDAPSearchScope
from pydantic import AnyUrl, BaseModel, Field, SecretStr
from pydantic import __version__ as pydantic_version
from typing_extensions import Annotated, Literal

from horizon.backend.settings.auth.jwt import JWTSettings

if TYPE_CHECKING:
    LDAPUrl = AnyUrl
elif pydantic_version < "2":

    class LDAPUrl(AnyUrl):  # noqa: WPS440
        """LDAP connection url, like ``ldap://127.0.0.1:389`` or ``ldaps://127.0.0.1:636``"""

        allowed_schemes = ["ldap", "ldaps"]
        host_required = True

else:
    from pydantic import UrlConstraints

    LDAPUrl: Type[AnyUrl] = Annotated[  # noqa: WPS440
        AnyUrl,
        UrlConstraints(allowed_schemes=["ldap", "ldaps"], host_required=True),
    ]


class LDAPCredentials(BaseModel):
    """LDAP lookup query is executed using this credentials
    (instead of username and password provided by user).

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

        HORIZON__AUTH__LDAP__POOL__MAX=10
    """

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

        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__USER=uid=techuser,ou=users,dc=example,dc=com
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__PASSWORD=somepassword
        HORIZON__AUTH__LDAP__LOOKUP__QUERY=(uid={username})
    """

    credentials: Optional[LDAPCredentials] = Field(
        default=None,
        description="Credentials used for connecting to LDAP while performing user lookup",
    )
    query: str = Field(
        default="({uid_attribute}={username})",
        description=textwrap.dedent(
            """
            LDAP query send in lookup request.

            Usually lookup is performed against attributes ``uid`` (LDAP) or ``sAMAccountName`` (ActiveDirectory).
            You can also pass any query string supported by LDAP.
            See `Bonsai documentation <https://bonsai.readthedocs.io/en/latest/tutorial.html#searching>`_.

            Supported substitution values (see :obj:`horizon.backend.settings.auth.ldap.LDAPSettings`.):
              * ``{uid_attribute}``
              * ``{username}``
            """,
        ),
    )
    scope: LDAPSearchScope = Field(
        default=LDAPSearchScope.ONELEVEL,
        description=textwrap.dedent(
            """
            Lookup scope. Use ``SUBTREE`` for ActiveDirectory.

            See `Bonsai documentation <https://bonsai.readthedocs.io/en/latest/tutorial.html#searching>`_.
            """,
        ),
    )


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
        default="{uid_attribute}={username},{base_dn}",
        description=textwrap.dedent(
            """
            Template for building DN string, used for checking credentials in LDAP. You can pass any DN value supported by LDAP.

            Supported substitution values:
              * ``{username}``
              * ``{uid_attribute}`` (see :obj:`~uid_attribute`)
              * ``{base_dn}`` (see :obj:`~base_dn`)
            """,
        ),
    )

    pool: LDAPConnectionPoolSettings = Field(
        default_factory=LDAPConnectionPoolSettings,
        description="LDAP connection pool settings",
    )
    lookup: Optional[LDAPLookupSettings] = Field(
        default_factory=LDAPLookupSettings,
        description="LDAP search options. Set to ``None`` to disable lookup.",
    )


class LDAPAuthProviderSettings(BaseModel):
    """Settings for LDAPAuthProvider.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__PROVIDER=horizon.backend.providers.auth.ldap.LDAPAuthProvider
        HORIZON__AUTH__ACCESS_KEY__SECRET_KEY=secret
        HORIZON__AUTH__LDAP__URL=ldap://ldap.domain.com:389
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__USER=uid=techuser,ou=users,dc=example,dc=com
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__PASSWORD=somepassword
    """

    access_token: JWTSettings = Field(description="Access-token related settings")
    ldap: LDAPSettings = Field(description="LDAP related settings")