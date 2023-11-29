.. _backend-configuration-debug:

Enabling debug
===============

Return debug info in backend responses
--------------------------------------

By default, server does not add error details to response bodies,
to avoid exposing instance-specific information to end users.

You can change this by setting:

.. code-block:: bash

    >>> export HORIZON__SERVER__DEBUG=False
    >>> # start backend
    >>> curl -XPOST http://localhost:8000/failing/endpoint ...

    {
        "error": {
            "code": "unknown",
            "message": "Got unhandled exception. Please contact support",
            "details": null,
        },
    }

.. code-block:: bash

    >>> export HORIZON__SERVER__DEBUG=True
    >>> # start backend
    >>> curl -XPOST http://localhost:8000/failing/endpoint ...

    {
        "error": {
            "code": "unknown",
            "message": "Got unhandled exception. Please contact support",
            "details": ["Some exception data", "more data"],
        },
    }

.. warning::

    This is only for development environment only. Do **NOT** use on production!

Print debug logs on backend
---------------------------

See :ref:`backend-configuration-logging`, but replace log level ``INFO`` with ``DEBUG``.

Add ``X-Request-ID`` header on backend
--------------------------------------

Server can add ``X-Request-ID`` header to responses, which allows to match request on client with backend response.

This is done by ``request_id`` middleware, which is enabled by default and can configured as described below:

.. autopydantic_model:: horizon.backend.settings.server.RequestIDSettings

Print request ID  to backend logs
---------------------------------

This is done by adding a specific filter to logging handler:

.. dropdown:: ``logging.yml``

    .. literalinclude:: ../../../horizon/backend/settings/log/plain.yml
        :emphasize-lines: 6-12,17-18,25


Use ``X-Request-ID`` header on client
-------------------------------------

If client got ``X-Request-ID`` header from backend, it is printed to logs with ``DEBUG`` level:

.. code-block:: python

    >>> import logging

    >>> logging.basicConfig(level=logging.DEBUG)
    >>> client.ping()

    DEBUG:urllib3.connectionpool:http://localhost:8000 "GET /monitoring/ping HTTP/1.1" 200 15
    DEBUG:horizon.client.base:Request ID: '018c15e97a068ae09484f8c25e2799dd'

Also, if backend response was not successful, ``Request ID`` is added to exception message:

.. code-block:: python

    >>> client.get_namespace("unknown")

    requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://localhost:8000/v1/namespaces/unknown
    Request ID: '018c15eb80fa81a6b38c9eaa519cd322'
