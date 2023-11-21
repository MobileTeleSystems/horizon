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

* you can search for user by ``uid``, e.g. ``(uid={username})`` or ``(sAMAccountName={username})``
* you can search for user by several attributes, e.g. ``(|(uid={username})(mail={username}@domain.com))``
* you can filter for entries, like ``(&(uid={username})(objectClass=person)``
* you can filter for users matching a specific group or some other condition, like ``(&(uid={username})(memberOf=cn=MyPrettyGroup,ou=Groups,dc=mycompany,dc=com))``

After user is found in LDAP, its :obj:`uid_attribute <horizon.backend.settings.auth.ldap.LDAPSettings.uid_attribute>` is used for audit records.

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