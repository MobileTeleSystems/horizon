.. _client-sync:

Sync client
===========

Quickstart
----------

Here is a short example of using sync client to interact with backend.

.. code-block:: python

    from horizon.client.sync import HorizonClientSync
    from horizon.client.auth import LoginPassword
    from horizon.commons.schemas.v1 import NamespaceCreateRequestV1, HWMWriteRequestV1

    # create client object
    client = HorizonClientSync(
        base_url="http://some.domain.com",
        auth=LoginPassword(login="me", password="12345"),
    )

    # check for credentials and issue access token
    client.authorize()

    # create namespace with name "my_namespace"
    created_namespace = client.create_namespace(NamespaceCreateRequestV1(name="my_namespace"))

    # create or update HWM with name "my_hwm" in this namespace
    hwm = HWMWriteRequestV1(name="my_hwm", type="column_int", value=123)
    created_hwm = client.write_hwm("my_namespace", hwm)

Reference
---------

.. currentmodule:: horizon.client.sync

.. autoclass:: HorizonClientSync
    :members: authorize, ping, whoami, paginate_namespaces, create_namespace, update_namespace, delete_namespace, paginate_hwm, write_hwm, delete_hwm, paginate_hwm_history
    :member-order: bysource