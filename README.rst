.. _readme:

Horizon
=======

|Build Status| |Coverage| |Documentation| |Docker image| |PyPI|

.. |Build Status| image:: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon/badges/develop/pipeline.svg
    :target: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon/-/pipelines
.. |Coverage| image:: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon/badges/develop/coverage.svg
    :target: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon/-/graphs/develop/charts
.. |Documentation| image:: https://img.shields.io/badge/docs-latest-success
    :target: https://bigdata.pages.mts.ru/platform/onetools/horizon/
.. |Docker image| image:: https://img.shields.io/badge/docker-pull-yellow
    :target: https://sregistry.mts.ru/harbor/projects/14/repositories/bigdata%2Fplatform%2Fonetools%2Fhorizon%2Fbackend/artifacts-tab
.. |PyPI| image:: https://img.shields.io/badge/pypi-download-orange
    :target: https://artifactory.mts.ru/ui/native/own-onetl-pypi-local/data-horizon/

|Logo|

.. |Logo| image:: docs/_static/logo.svg
    :width: 400
    :alt: Horizon logo
    :target: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon

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

Non-goals
---------

* This is not a data storage, it is not designed to store raw table rows. It is designed to store only HWM values, e.g. *max value* of a specific table column, list of handled files and so on.
* Attaching machine-readable metadata for HWMs (like ``table``, ``process``, ``origin``) is not supported. This should be stored somewhere else.

Limitations
-----------

* Currently Horizon does not implement any kind of access control, so **anyone can change anything**.
* HWM types and values are not checked, and can contain anything. It is up to user how to parse fetched values and perform validation.
* HWMs cannot be renamed or moved between namespaces. These operations could be performed only by creating new HWM in desired namespace, and deleting the old one.

.. documentation

Documentation
-------------

See https://bigdata.pages.mts.ru/platform/onetools/horizon/
