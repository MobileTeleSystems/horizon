.. _readme:

Horizon
=======

|Repo Status| |PyPI| |PyPI License| |PyPI Python Version| |Docker image| |Documentation|
|Build Status| |Coverage|  |pre-commit.ci|

.. |Repo Status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://github.com/MobileTeleSystems/horizon
.. |PyPI| image:: https://img.shields.io/pypi/v/data-horizon
    :target: https://pypi.org/project/data-horizon/
.. |PyPI License| image:: https://img.shields.io/pypi/l/data-horizon.svg
    :target: https://github.com/MobileTeleSystems/horizon/blob/develop/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/data-horizon.svg
    :target: https://badge.fury.io/py/data-horizon
.. |Docker image| image:: https://img.shields.io/docker/v/mtsrus/horizon-backend?sort=semver&label=docker
    :target: https://hub.docker.com/r/mtsrus/horizon-backend
.. |Documentation| image:: https://readthedocs.org/projects/data-horizon/badge/?version=stable
    :target: https://data-horizon.readthedocs.io/
.. |Build Status| image:: https://github.com/MobileTeleSystems/horizon/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/horizon/actions
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/horizon/graph/badge.svg?token=BIRWPTWEE0
    :target: https://codecov.io/gh/MobileTeleSystems/horizon
.. |pre-commit.ci| image:: https://results.pre-commit.ci/badge/github/MobileTeleSystems/horizon/develop.svg
    :target: https://results.pre-commit.ci/latest/github/MobileTeleSystems/horizon/develop


|Logo|

.. |Logo| image:: docs/_static/logo.svg
    :width: 400
    :alt: Horizon logo
    :target: https://github.com/MobileTeleSystems/horizon/

What is Horizon?
----------------

Horizon is an application that implements simple HWM Store. Right now it includes:

* REST API
* Python client

Goals
-----

* Allow users to save and fetch *HWM* (High Water Mark) items. These are ``name+type+value`` triples with few optional fields (``description``, ``entity``, ``expression``).
* Avoid confusion between different user's data by separating HWMs to different *namespaces*. HWMs is created within namespace, each ``namespace name`` + ``HWM name`` is unique.
* Allow users to get HWM change history, to determine who and when changed a specific HWM value and other fields.
* Provide a robust role based access control model to define and enforce permissions within the service. This ensures that user interactions with ``HWMs`` and ``Namespaces`` are governed by their assigned roles.

Non-goals
---------

* This is not a data storage, it is not designed to store raw table rows. It is designed to store only HWM values, e.g. *max value* of a specific table column, list of handled files and so on.
* Attaching machine-readable metadata for HWMs (like ``table``, ``process``, ``origin``) is not supported. This should be stored somewhere else.

Limitations
-----------

* HWM types and values are not checked, and can contain anything. It is up to user how to parse fetched values and perform validation.
* HWMs cannot be renamed or moved between namespaces. These operations could be performed only by creating new HWM in desired namespace, and deleting the old one.

.. documentation

Documentation
-------------

See https://data-horizon.readthedocs.io/
