.. _client-install:

Install client
==============

Requirements
~~~~~~~~~~~~

* Python 3.7 or above
* Pydantic 1.x or 2.x

Installation process
~~~~~~~~~~~~~~~~~~~~

Install horizon package with following *extra* dependencies:

.. code-block:: bash

    pip install horizon[client-sync]

Available *extras* are:

* ``client-sync`` - :ref:`client-sync`, based on `authlib <https://docs.authlib.org>`_ and `requests <https://requests.readthedocs.io>`_
