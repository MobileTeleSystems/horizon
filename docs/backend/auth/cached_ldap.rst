.. _backend-auth-ldap-cached:

LDAP Cached Auth provider
=========================

Description
-----------

Same as :ref:`backend-auth-ldap`, but if LDAP request for checking user credentials was successful,
credentials are stored in local cache (table in internal database, in form ``login`` + ``hash(password)`` + ``update timestamp``).

Next auth requests for the same login are performed against this cache **first**. LDAP requests are send *only* if cache have been expired.

This allows to:

* Bypass errors with LDAP availability, e.g. network errors
* Reduce number of requests made to LDAP.

Downsides:

* If user changed password, and cache is not expired yet, user may still log in with old credentials.
* Same if user was blocked in LDAP.

Configuration
-------------

Other settings are just the same as for ``LDAPAuthProvider``

.. autopydantic_model:: horizon.backend.settings.auth.cached_ldap.CashedLDAPAuthProviderSettings
    :inherited-members: BaseModel

.. autopydantic_model:: horizon.backend.settings.auth.cached_ldap.LDAPCacheSettings
.. autopydantic_model:: horizon.backend.settings.auth.cached_ldap.LDAPCachePasswordHashSettings
