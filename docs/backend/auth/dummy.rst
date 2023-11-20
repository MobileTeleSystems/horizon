.. _backend-auth-dummy:

Dummy Auth provider
===================

Description
-----------

This auth provider allows to sign-in with any username and password, and and then issues an access token.

After successful auth, username is saved to backend database. It is then used for creating audit records for any object change, see ``changed_by`` field.

Configuration
-------------

.. autopydantic_model:: horizon.backend.settings.auth.dummy.DummyAuthProviderSettings
.. autopydantic_model:: horizon.backend.settings.auth.jwt.JWTSettings
