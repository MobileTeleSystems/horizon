.. title

Horizon
=======

Simple HWM store, based on FastAPI & Postgres.

Requirements
============

Backend
-------

Python: 3.7+

.. documentation

Documentation
=============

.. wiki

Wiki page
=========

.. install

Installation
============

.. developing

Develop
=======

Clone repo
----------

.. code:: bash

    git clone git@gitlab.services.mts.ru:bigdata/platform/onetools/horizon.git -b develop

    cd horizon

Setup environment
-----------------

.. code:: bash

    make venv-init


Enable pre-commit hooks
-----------------------

Install pre-commit hooks:

.. code:: bash

    pre-commit install --install-hooks

Test pre-commit hooks run:

.. code:: bash

    pre-commit run

Run pre-commit hooks on whole repo:

.. code:: bash

    pre-commit run --all-files

.. tests

Unit tests
----------

.. code:: bash

    make db
    make dev  # in separate terminal tab
    make test

.. Makefile

Makefile
--------

Most commands have their own aliases in the makefile for more convenient use.

User ``make help`` for show all available commands.
