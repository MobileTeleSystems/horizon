Contributing Guide
==================

Welcome! There are many ways to contribute, including submitting bug
reports, improving documentation, submitting feature requests, reviewing
new submissions, or contributing code that can be incorporated into the
project.

Limitations
-----------

We should keep close to these items during development:

* Some companies still use Python 3.7. So it is required to keep compatibility if possible, at least for *client* part of package.
* Different users uses Horizon in different ways - someone store data in Postgres, someone in MySQL, some users need LDAP. Such dependencies should be optional.

Initial setup for local development
-----------------------------------

Install Git
~~~~~~~~~~~

Please follow `instruction <https://docs.gitlab.com/ee/topics/git/>`_.

Create a fork
~~~~~~~~~~~~~

If you are not a member of a development team building horizon, you should create a fork before making any changes.

Please follow `instruction <https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html>`_.

Clone the repo
~~~~~~~~~~~~~~

Open terminal and run these commands:

.. code:: bash

    git clone https://gitlab.services.mts.ru/myuser/horizon.git -b develop

    cd horizon

Setup environment
~~~~~~~~~~~~~~~~~

Firstly, install `make <https://www.gnu.org/software/make/manual/make.html>`_. It is used for running complex commands in local environment.

Secondly, create virtualenv and install dependencies:

.. code:: bash

    make venv-init

If you already have venv, but need to install dependencies required for development:

.. code:: bash

    make venv-install

We are using `poetry <https://python-poetry.org/docs/managing-dependencies/>`_ for managing dependencies and building the package.
It allows to keep development environment the same for all developers due to using lock file with fixed dependency versions.

There are *extra* dependencies (included into package as optional):

* ``backend``
* ``client-sync``
* ``postgres``
* ``ldap``

And *groups* (not included into package, used locally and in CI):

* ``test`` - for running tests
* ``dev`` - for development, like linters, formatters, mypy, pre-commit and so on
* ``docs`` - for building documentation

Enable pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~~

`pre-commit <https://pre-commit.com/>`_ hooks allows to validate & fix repository content before making new commit.
It allows to run linters, formatters, fix file permissions and so on. If something is wrong, changes cannot be committed.

Firstly, install pre-commit hooks:

.. code:: bash

    pre-commit install --install-hooks

Ant then test hooks run:

.. code:: bash

    pre-commit run

How to
------

Run development instance locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start DB container:

.. code:: bash

    make db

Then start development server:

.. code:: bash

    make dev

And open http://localhost:8000/docs

Settings are stored in ``.env.local`` file.

Working with migrations
~~~~~~~~~~~~~~~~~~~~~~~

Start database:

.. code:: bash

    make db-start

Generate revision:

.. code:: bash

    make db-revision

Upgrade db to ``head`` migration:

.. code:: bash

    make db-upgrade

Downgrade db to ``head-1`` migration:

.. code:: bash

    make db-downgrade

Run tests locally
~~~~~~~~~~~~~~~~~

Start all containers with dependencies:

.. code:: bash

    make db  # for backend & client tests
    make ldap-start  # for backend tests
    make dev  # for client test, run in separate terminal tab

Run tests:

.. code:: bash

    make test

You can pass additional arguments, they will be passed to pytest:

.. code:: bash

    make test PYTEST_ARG="-m client-sync -lsx -vvvv --log-cli-level=INFO"

Stop all containers and remove created volumes:

.. code:: bash

    make cleanup ARGS="-v"

Get fixtures not used by any test:

.. code:: bash

    make check-fixtures

Build CI image locally
~~~~~~~~~~~~~~~~~~~~~~~~

This image is build in CI for testing purposes, but you can do that locally as well:

.. code:: bash

    make test-build

Run production instance locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Firstly, build production image:

.. code:: bash

    make prod-build

And then start it:

.. code:: bash

    make prod

Then open http://localhost:8000/docs

Settings are stored in ``.env.docker`` file.

Build documentation
~~~~~~~~~~~~~~~~~~~

Build documentation using Sphinx & open it:

.. code:: bash

    make docs

If documentation should be build cleanly instead of reusing existing build result:

.. code:: bash

    make docs-fresh


Review process
--------------

Please create a new Jira issue for any significant changes and
enhancements that you wish to make. Provide the feature you would like
to see, why you need it, and how it will work. Discuss your ideas
transparently and get community feedback before proceeding.

Significant Changes that you wish to contribute to the project should be
discussed first in a Jira issue that clearly outlines the changes and
benefits of the feature.

Small Changes can directly be crafted and submitted to the Gitlab
Repository as a Merge Request.

Create merge request
~~~~~~~~~~~~~~~~~~~~

Commit your changes:

.. code:: bash

    git commit -m "Commit message"
    git push

Then open Gitlab interface and `create merge request <https://docs.gitlab.com/ee/user/project/merge_requests/>`_.
Please follow guide from MR body template.

After pull request is created, it get a corresponding number, e.g. 123 (``mr_number``).

Write release notes
~~~~~~~~~~~~~~~~~~~

``horizon`` uses `towncrier <https://pypi.org/project/towncrier/>`_
for changelog management.

To submit a change note about your PR, add a text file into the
`docs/changelog/next_release <./next_release>`_ folder. It should contain an
explanation of what applying this PR will change in the way
end-users interact with the project. One sentence is usually
enough but feel free to add as many details as you feel necessary
for the users to understand what it means.

**Use the past tense** for the text in your fragment because,
combined with others, it will be a part of the "news digest"
telling the readers **what changed** in a specific version of
the library *since the previous version*.

You should also use
reStructuredText syntax for highlighting code (inline or block),
linking parts of the docs or external sites.
If you wish to sign your change, feel free to add ``-- by
:user:`username``` at the end (replace ``username``
with your own!).

Finally, name your file following the convention that Towncrier
understands: it should start with the number of an issue or a
PR followed by a dot, then add a patch type, like ``feature``,
``doc``, ``misc`` etc., and add ``.rst`` as a suffix. If you
need to add more than one fragment, you may add an optional
sequence number (delimited with another period) between the type
and the suffix.

In general the name will follow ``<mr_number>.<category>.rst`` pattern,
where the categories are:

- ``feature``: Any new feature
- ``bugfix``: A bug fix
- ``improvement``: An improvement
- ``doc``: A change to the documentation
- ``dependency``: Dependency-related changes
- ``misc``: Changes internal to the repo like CI, test and build changes

A pull request may have more than one of these components, for example
a code change may introduce a new feature that deprecates an old
feature, in which case two fragments should be added. It is not
necessary to make a separate documentation fragment for documentation
changes accompanying the relevant code changes.

Examples for adding changelog entries to your Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst
    :caption: docs/changelog/next_release/DOP-1234.doc.1.rst

    Added a ``:user:`` role to Sphinx config -- by :user:`someuser`

.. code-block:: rst
    :caption: docs/changelog/next_release/DOP-2345.bugfix.rst

    Fixed behavior of ``backend`` -- by :user:`someuser`

.. code-block:: rst
    :caption: docs/changelog/next_release/DOP-4567.feature.rst

    Added support of ``timeout`` in ``LDAP``
    -- by :user:`someuser`, :user:`anotheruser` and :user:`otheruser`

.. tip::

    See `pyproject.toml <pyproject.toml>`_ for all available categories
    (``tool.towncrier.type``).

.. _Towncrier philosophy:
    https://towncrier.readthedocs.io/en/stable/#philosophy
