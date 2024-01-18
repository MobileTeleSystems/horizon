.. include:: ../README.rst
    :end-before: |Logo|

.. https://gitlab.com/gitlab-org/gitlab-foss/-/issues/17182#note_326840648
.. TODO: move this block directly to README after moving repo to Github

.. raw:: html

    <div align="center">
        <a href="https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon">
            <img width="400" src="_static/logo.svg" alt="Horizon logo">
        </a>
    </div>

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
