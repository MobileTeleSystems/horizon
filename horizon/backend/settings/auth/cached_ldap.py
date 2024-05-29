# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

"""
Settings for LDAPAuthProvider class.

Basic LDAP terminology is explained here: `LDAP Overview <https://www.zytrax.com/books/ldap/ch2/>`_
"""

import textwrap
from typing import Any, Dict

from pydantic import BaseModel, Field

from horizon.backend.settings.auth.ldap import LDAPAuthProviderSettings


class LDAPCachePasswordHashSettings(BaseModel):
    """Settings related to LDAP credentials cache password hashing.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__CACHE__PASSWORD_HASH__ALGORITHM=argon2
        HORIZON__AUTH__CACHE__PASSWORD_HASH__OPTIONS={"time_cost": 2, "memory_cost": 1024, "parallelism": 1}
    """

    algorithm: str = Field(
        default="argon2",
        description=textwrap.dedent(
            """
            Hashing algorithm used to hash user credentials.

            See `passlib documentation <https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html#active-hashes>`_
            for more details.
            """,
        ),
    )
    options: Dict[str, Any] = Field(
        default={},
        description="Options passed to hashing algorithm",
    )


class LDAPCacheSettings(BaseModel):
    """Settings related to LDAP credentials cache.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__CACHE__EXPIRE_SECONDS=3600  # 1 hour
    """

    expire_seconds: int = Field(
        default=60 * 60,
        description=textwrap.dedent(
            """
            Credentials cache expiration time, in seconds.

            .. warning::

                Please do not set too large value here, as it may lead to security issues.
            """,
        ),
    )
    password_hash: LDAPCachePasswordHashSettings = Field(
        default_factory=LDAPCachePasswordHashSettings,
        description="Password hashing options",
    )


class CachedLDAPAuthProviderSettings(LDAPAuthProviderSettings):
    """Settings for CachedLDAPAuthProvider.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__PROVIDER=horizon.backend.providers.auth.cached_ldap.CachedLDAPAuthProvider
        HORIZON__AUTH__ACCESS_KEY__SECRET_KEY=secret
        HORIZON__AUTH__LDAP__URL=ldap://ldap.domain.com:389
        HORIZON__AUTH__LDAP__LOOKUP__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__POOL__ENABLED=True
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__USER=uid=techuser,ou=users,dc=example,dc=com
        HORIZON__AUTH__LDAP__LOOKUP__CREDENTIALS__PASSWORD=somepassword
        HORIZON__AUTH__CACHE__EXPIRE_SECONDS=3600  # 1 hour
    """

    cache: LDAPCacheSettings = Field(default_factory=LDAPCacheSettings, description="Cache related settings")
