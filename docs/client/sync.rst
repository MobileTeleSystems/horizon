.. _client-sync:

Sync client
===========

Quickstart
----------

Here is a short example of using sync client to interact with backend.

.. code-block:: python

    from horizon.client.sync import HorizonClientSync
    from horizon.client.auth import LoginPassword
    from horizon.commons.schemas.v1 import NamespaceCreateRequestV1, HWMUpdateRequestV1

    # create client object
    client = HorizonClientSync(
        base_url="http://some.domain.com/api",
        auth=LoginPassword(login="me", password="12345"),
    )

    # check for credentials and issue access token
    client.authorize()

    # create namespace with name "my_namespace"
    created_namespace = client.create_namespace(NamespaceCreateRequestV1(name="my_namespace"))

    # create HWM with name "my_hwm" in this namespace
    hwm = HWMCreateRequestV1(
        namespace_id=created_namespace.id,
        name="my_hwm",
        type="column_int",
        value=123,
    )
    created_hwm = client.create_hwm(hwm)

    # update HWM with name "my_hwm" in this namespace
    hwm_change = HWMUpdateRequestV1(value=234)
    updated_hwm = client.update_hwm(hwm.id, hwm_change)

Reference
---------

.. currentmodule:: horizon.client.sync

.. autoclass:: HorizonClientSync
    :members: authorize, ping, whoami, paginate_namespaces, create_namespace, update_namespace, delete_namespace, paginate_hwm, create_hwm, update_hwm, delete_hwm, paginate_hwm_history, retry
    :member-order: bysource

.. autoclass:: RetryConfig
    :members: *
    :member-order: bysource

.. autoclass:: TimeoutConfig
    :members: *
    :member-order: bysource