.. _client-exceptions:

Exceptions
===========

These exception classes are used in client implementations.

Base
----

.. currentmodule:: horizon.commons.exceptions.base

.. autoclass:: ApplicationError
    :members: message, details

Authorization
-------------

.. currentmodule:: horizon.commons.exceptions.auth

.. autoclass:: AuthorizationError
    :members: message, details

Entity
------

.. currentmodule:: horizon.commons.exceptions.entity

.. autoclass:: EntityNotFoundError
    :members: message, details, entity_type, field, value
    :member-order: bysource

.. autoclass:: EntityAlreadyExistsError
    :members: message, details, entity_type, field, value
    :member-order: bysource

Service
-------

.. currentmodule:: horizon.commons.exceptions.service

.. autoclass:: ServiceError
    :members: message
