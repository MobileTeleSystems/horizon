.. _readme:

Data.Horizon
============

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

What is Data.Horizon?
---------------------

Data.Horizon is an application that implements simple HWM Store. Right now it includes:

* REST API
* Python client

Goals
-----

* Allow users to save and fetch High Water Mark (*HWM*) items. These are ``name+type+value`` triples with few optional fields.
* Avoid confusion between different user's data by separating HWMs to different *namespaces*. Each HWM is bound to namespace.
* Allow users to get HWM change history, to determine who and when changed a specific HWM value and other fields.
* Provide RBAC model to ensure that interaction with ``HWMs`` and ``Namespaces`` are governed by role assigned to each user. Roles are assigned per namespace.

Non-goals
---------

* This is not a *data* storage, it is not designed to store raw table rows. It is designed to store only HWM values.
* Attaching machine-readable metadata for HWMs (like ``process``, ``origin``) is not supported. This should be stored somewhere else.

.. documentation

Documentation
-------------

See https://data-horizon.readthedocs.io/
