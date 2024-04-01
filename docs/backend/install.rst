.. _backend-install:

Install & run backend
=====================

With docker
-----------

Requirements
~~~~~~~~~~~~

* `Docker <https://docs.docker.com/engine/install/>`_
* `docker-compose <https://github.com/docker/compose/releases/>`_

Installation process
~~~~~~~~~~~~~~~~~~~~

Docker will download backend image of Horizon & Postgres, and run them.
Options can be set via ``.env`` file or ``environment`` section in ``docker-compose.yml``

.. dropdown:: ``docker-compose.yml``

    .. literalinclude:: ../../docker-compose.yml

.. dropdown:: ``.env.docker``

    .. literalinclude:: ../../.env.docker

After container is started and ready, open http://localhost:8000/docs.

Users listed in ``HORIZON__ENTRYPOINT__ADMIN_USERS`` env variable will be automatically promoted to ``SUPERADMIN`` role.

Without docker
--------------

Requirements
~~~~~~~~~~~~

* Python 3.7 or above
* Pydantic 2.x
* ``libldap2-dev``, ``libsasl2-dev``, ``libkrb5-dev`` (for :ref:`backend-auth-ldap`)
* Some relation database instance, like `Postgres <https://www.postgresql.org/>`_

Installation process
~~~~~~~~~~~~~~~~~~~~

Install ``data-horizon`` package with following *extra* dependencies:

.. code-block:: console

    $ pip install data-horizon[backend,postgres,ldap]

Available *extras* are:

* ``backend`` - main backend requirements, like FastAPI, SQLAlchemy and so on.
* ``postgres`` - requirements required to use Postgres as backend data storage.
* ``ldap`` - requirements used by :ref:`backend-auth-ldap`.

.. note::

      For **macOS** users, an additional step is required. `You need to install the "bonsai" Python library from source code <https://bonsai.readthedocs.io/en/latest/install.html#install-from-source-on-macos>`_. This installation is necessary to work with LDAP.

Run database
~~~~~~~~~~~~

Start Postgres instance somewhere, and set up database url using environment variables:

.. code-block:: bash

    HORIZON__DATABASE__URL=postgresql+asyncpg://user:password@postgres-host:5432/database_name

You can use virtually any database supported by `SQLAlchemy <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_,
but the only one we really tested is Postgres.

See :ref:`Database settings <backend-configuration-database>` for more options.

Run migrations
~~~~~~~~~~~~~~

To apply migrations (database structure changes) you need to execute following command:

.. code-block:: console

    $ python -m horizon.backend.db.migrations upgrade head

This is a thin wrapper around `alembic <https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration>`_ cli,
options and commands are just the same.

.. note::

    This command should be executed after each upgrade to new Horizon version.

Run backend
~~~~~~~~~~~

To start backend server you need to execute following command:

.. code-block:: console

    $ python -m horizon.backend --host 0.0.0.0 --port 8000

This is a thin wrapper around `uvicorn <https://www.uvicorn.org/#command-line-options>`_ cli,
options and commands are just the same.

After server is started and ready, open http://localhost:8000/docs.

Add admin users
~~~~~~~~~~~~~~~

To promote specific users to ``SUPERADMIN`` role, run the following script:

.. code-block:: console

    $ python -m horizon.backend.scripts.manage_admins add admin1 admin2

See :ref:`scripts` documentation.
