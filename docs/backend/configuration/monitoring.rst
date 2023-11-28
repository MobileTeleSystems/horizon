.. _backend-configuration-monitoring:

Setup monitoring
================

Backend provides 2 endpoints with Prometheus compatible metrics:

* ``GET /monitoring/metrics`` - server metrics, like number of requests per path and response status, CPU and RAM usage, and so on.

.. dropdown:: Example

    .. literalinclude:: ../../static/metrics.prom

* ``GET /monitoring/stats`` - usage statistics, like number of users, namespaces, HWMs.

.. dropdown:: Example

    .. literalinclude:: ../../static/stats.prom

These endpoints are enabled and configured using settings below:

.. autopydantic_model:: horizon.backend.settings.server.MonitoringSettings
