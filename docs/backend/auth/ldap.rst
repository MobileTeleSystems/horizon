.. _backend-auth-ldap:

LDAP Auth provider
==================

Description
-----------

This auth provider checks for user credentials in LDAP, and and then issues an access token.

All requests to backend should be made with passing this access token. If token is expired, then new auth token should be issued.

After successful auth, username is saved to backend database. It is then used for creating audit records for any object change, see ``changed_by`` field.

.. warning::

    Until token is valid, no requests will be made to LDAP to check if user exists and not locked.
    So do not set access token expiration time for too long (e.g. longer than a day).

Strategies
----------

.. note::

    Basic LDAP terminology is explained here: `LDAP Overview <https://www.zytrax.com/books/ldap/ch2/>`_

There are 2 strategies to check for user in LDAP:

* Try to call ``bind`` request in LDAP with ``DN`` (``DistinguishedName``) and user password. ``DN`` is generated using :obj:`bind_dn_template <horizon.backend.settings.auth.ldap.LDAPSettings.bind_dn_template>`
* First try to *lookup* for user (``search`` request) in LDAP to get user's ``DN`` using some query, and then try to call ``bind`` using this ``DN``. See :obj:`lookup settings <horizon.backend.settings.auth.ldap.LDAPSettings.lookup>`

By default, **lookup strategy is used**, as it can find user in a complex LDAP/ActiveDirectory environment. For example:

* you can search for user by ``uid``, e.g. ``(uid={login})`` or ``(sAMAccountName={login})``
* you can search for user by several attributes, e.g. ``(|(uid={login})(mail={login}@domain.com))``
* you can filter for entries, like ``(&(uid={login})(objectClass=person)``
* you can filter for users matching a specific group or some other condition, like ``(&(uid={login})(memberOf=cn=MyPrettyGroup,ou=Groups,dc=mycompany,dc=com))``

After user is found in LDAP, its :obj:`uid_attribute <horizon.backend.settings.auth.ldap.LDAPSettings.uid_attribute>` is used for audit records.

Interaction schema
------------------

.. dropdown:: No lookup

    .. plantuml::

        @startuml
            title LDAPAuthProvider (no lookup)
            participant "Client"
            participant "Backend"
            participant "LDAP"

            == POST v1/auth/token ==

            activate "Client"
            alt Successful case
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Successful
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = login
                "Backend" -> "Backend" : Create user if not exist
                "Backend" -[#green]> "Client" -- : Generate and return access_token

            else Wrong credentials | User blocker in LDAP
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" x-[#red]> "Backend" -- : Bind error
                "Backend" x-[#red]> "Client" -- : 401 Unauthorized

            else User is blocked in internal backend database
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Successful
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = login
                "Backend" x-[#red]> "Client" -- : 404 Not found

            else User is deleted in internal backend database
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Return user info
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = login
                "Backend" x-[#red]> "Client" -- : 404 Not found

            else LDAP is unavailable
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : DN = bind_dn_template(login)
                "Backend" -[#red]>x "LDAP" : Call bind(DN, password)
                "Backend" x-[#red]> "Client" -- : 503 Service unavailable
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

.. dropdown:: With lookup

    .. plantuml::

        @startuml
            title LDAPAuthProvider (with lookup)
            participant "Client"
            participant "Backend"
            participant "LDAP"

            == Backend start ==

            "Backend" ->o "LDAP" ++ : bind(lookup.username, lookup.password)
            note right of "LDAP" : Open connection \npool for\nsearch queries\n(optional, recommended)

            == POST v1/auth/token ==

            activate "Client"
            alt Successful case
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : query = query_template(login)
                "Backend" ->o "LDAP" : Call search(query, base_dn, attributes=*)
                "LDAP" --[#green]> "Backend" : Return user DN and uid_attribute
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Successful
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = uid_attribute from LDAP response
                "Backend" -> "Backend" : Create user if not exist
                "Backend" -[#green]> "Client" -- : Generate and return access_token

            else Wrong credentials | User blocker in LDAP
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : query = query_template(login)
                "Backend" ->o "LDAP" : Call search(query, base_dn, attributes=*)
                "LDAP" --[#green]> "Backend" : Return user DN and uid_attribute
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" x--[#red]> "Backend" -- : Bind error
                "Backend" x-[#red]> "Client" -- : 401 Unauthorized

            else User is blocked in internal backend database
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : query = query_template(login)
                "Backend" ->o "LDAP" : Call search(query, base_dn, attributes=*)
                "LDAP" --[#green]> "Backend" : Return user DN and uid_attribute
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Successful
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = uid_attribute from LDAP response
                "Backend" x-[#red]> "Client" -- : 404 Not found

            else User is deleted in internal backend database
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : query = query_template(login)
                "Backend" ->o "LDAP" : Call search(query, base_dn, attributes=*)
                "LDAP" --[#green]> "Backend" : Return user DN and uid_attribute
                "Backend" -> "LDAP" ++ : Call bind(DN, password)
                "LDAP" --[#green]> "Backend" -- : Successful
                "Backend" --> "Backend" : Check user in internal backend database,\nusername = uid_attribute from LDAP response
                "Backend" x-[#red]> "Client" -- : 404 Not found

            else LDAP is unavailable
                "Client" -> "Backend" ++ : login + password
                "Backend" --> "Backend" : query = query_template(login)
                "Backend" -[#red]>x "LDAP" : Call search(query, base_dn, attributes=*)
                "Backend" x-[#red]> "Client" -- : 503 Service unavailable
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

Basic configuration
-------------------

.. autopydantic_model:: horizon.backend.settings.auth.ldap.LDAPAuthProviderSettings
.. autopydantic_model:: horizon.backend.settings.auth.ldap.LDAPSettings
.. autopydantic_model:: horizon.backend.settings.auth.jwt.JWTSettings

.. autopydantic_model:: horizon.backend.settings.auth.ldap.LDAPConnectionPoolSettings

Lookup-related configuration
----------------------------

.. autopydantic_model:: horizon.backend.settings.auth.ldap.LDAPLookupSettings
.. autopydantic_model:: horizon.backend.settings.auth.ldap.LDAPCredentials