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
Interaction schema
------------------

.. dropdown:: Interaction schema

    .. plantuml::

        @startuml
            title CachedLDAPAuthProvider
            participant "Client"
            participant "Backend"
            participant "LDAP"

            == POST v1/auth/token ==

            activate "Client"
            alt First time auth | Empty cache | Cache expired
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : Search for credentials cache by login
                "Backend" --> "Backend" : No items found or item expired, using LDAP
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Successful
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = login
                "Backend" -> "Backend" : Create user if not exist
                "Backend" -> "Backend" : Save credentials to cache
                "Backend" -[#green]> "Client" -- : Generate and return access_token

            else Using cache, LDAP is totally ignored
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : Search for credentials cache by login
                "Backend" --> "Backend" : Found credentials, check for expiration
                "Backend" --> "Backend" : Not expired, validate password is matching hash
                "Backend" --> "Backend" : Password match, not calling LDAP
                "Backend" --> "Backend" : Check user in internal backend database
                "Backend" -> "Backend" : Create user if not exist
                "Backend" -[#green]> "Client" -- : Generate and return access_token

            else Password mismatch with cache, LDAP is totally ignored
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : Search for credentials cache by login
                "Backend" --> "Backend" : Found credentials, check for expiration
                "Backend" --> "Backend" : Not expired, validate password is matching hash
                "Backend" --> "Backend" : Password do not match local cache
                "Backend" x-[#red]> "Client" -- : 401 Unauthorized

            else No cache or cache expired, LDAP is unavailable
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : Search for credentials cache by login
                "Backend" --> "Backend" : No items found or item expired, using LDAP
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -[#red]>x "LDAP" : Call bind(DN, password)
                "Backend" x-[#red]> "Client" -- : 503 Service unavailable

            else
                note right of "Client" : Other cases are same as for LDAPAuthProvider,\nlike lookup, blocked/deleted users
            end

            == GET v1/namespaces ==

            alt Successful case
                "Client" -> "Backend" ++ : access_token
                "Backend" --> "Backend" : Validate token
                "Backend" --> "Backend" : Check user in internal backend database
                "Backend" -> "Backend" : Get data
                "Backend" -[#green]> "Client" -- : Return data

            else Token is expired
                "Client" -> "Backend" ++ : access_token
                "Backend" --> "Backend" : Validate token
                "Backend" x-[#red]> "Client" -- : 401 Unauthorized

            else User is blocked
                "Client" -> "Backend" ++ : access_token
                "Backend" --> "Backend" : Validate token
                "Backend" --> "Backend" : Check user in internal backend database
                "Backend" x-[#red]> "Client" -- : 401 Unauthorized

            else User is deleted
                "Client" -> "Backend" ++ : access_token
                "Backend" --> "Backend" : Validate token
                "Backend" --> "Backend" : Check user in internal backend database
                "Backend" x-[#red]> "Client" -- : 404 Not found
            end

            deactivate "Client"
        @enduml

Configuration
-------------

Other settings are just the same as for ``LDAPAuthProvider``

.. autopydantic_model:: horizon.backend.settings.auth.cached_ldap.CachedLDAPAuthProviderSettings
    :inherited-members: BaseModel

.. autopydantic_model:: horizon.backend.settings.auth.cached_ldap.LDAPCacheSettings
.. autopydantic_model:: horizon.backend.settings.auth.cached_ldap.LDAPCachePasswordHashSettings
