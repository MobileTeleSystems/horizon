.. _backend-auth-providers:

Auth Providers
==============

Horizon supports different auth provider implementations. You can change implementation via settings:

.. autopydantic_model:: horizon.backend.settings.auth.AuthSettings

.. toctree::
    :maxdepth: 2
    :caption: Auth providers

    dummy
    ldap
    cached_ldap

.. toctree::
    :maxdepth: 2
    :caption: For developers

    custom
