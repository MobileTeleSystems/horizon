.. include:: ../README.rst
    :end-before: |Logo|

.. image:: _static/logo.svg
    :alt: Horizon logo
    :align: center
    :width: 400

.. include:: ../README.rst
    :start-after: |Logo|
    :end-before: documentation

.. toctree::
    :maxdepth: 2
    :caption: Horizon
    :hidden:

    self

.. toctree::
    :maxdepth: 2
    :caption: Backend
    :hidden:

    backend/install
    backend/architecture
    backend/configuration/index
    backend/auth/index
    backend/openapi

.. toctree::
    :maxdepth: 2
    :caption: Permissions
    :hidden:

    permissions/index

.. toctree::
    :maxdepth: 2
    :caption: Client
    :hidden:

    client/install
    client/sync
    client/auth
    client/schemas/index
    client/exceptions

.. toctree::
    :maxdepth: 2
    :caption: Development
    :hidden:

    changelog
    contributing
    security
